"""Final selection, control matching and gold file, following docs/PROTOCOL.md.

usage: python select_items.py <3char_root> <data_dir>
"""
import collections
import csv
import json
import math
import random
import sys

import pyarrow.parquet as pq

SEED = 20261014
PER_STRATUM, MIN_PV, MAX_READINGS = 8, 1000, 3
NS = {"trp/iata": "IATA airport code system", "trp/ica2": "ICAO airline designator system",
      "lng/i31": "ISO 3166-1 alpha-3 country code standard", "lng/ioc": "International Olympic Committee country code system",
      "fin/i42": "ISO 4217 currency code standard", "fin/tck": "US stock ticker symbol listings",
      "cmp/dns": "DNS resource record type registry"}


def extras(root):
    out = {}
    for sid in NS:
        for r in pq.read_table(f"{root}/data/{sid}.parquet").to_pylist():
            out[(sid, r["code"])] = (json.loads(r["extra"] or "{}"), r["aliases"] or [])
    return out


def desc(sid, label, ex):
    if sid == "trp/iata":
        return f"{label} ({ex.get('municipality') or '?'}, {ex.get('country') or '?'})"
    if sid == "trp/ica2" and ex.get("country"):
        return f"{label} ({ex['country']})"
    if sid == "fin/i42" and ex.get("countries"):
        return f"{label} (currency of {', '.join(ex['countries'][:2])})"
    if sid == "cmp/dns":
        return f"the DNS record type that {label}"
    return label


def usable(r):
    return r["wp_title"] and r["pageviews"] not in ("", "None") and int(r["pageviews"]) >= MIN_PV and (r["system_id"] == "cmp/dns" or r["wd_n"] == "1")


def aliases(r, ex_aliases):
    a = [r["label"], r["wd_label"], r["wp_title"], *ex_aliases, *(r["wd_alts"].split("|") if r["wd_alts"] else [])]
    return sorted({x.strip() for x in a if x and x.strip()})


def main(root, data):
    rng = random.Random(SEED)
    ex = extras(root)
    pre = list(csv.DictReader(open(f"{data}/presample.csv", encoding="utf-8")))
    lits = collections.OrderedDict()
    for r in pre:
        if r["role"] == "collision": lits.setdefault((r["stratum"], r["literal"]), []).append(r)
    chosen = collections.defaultdict(list)
    for (s, lit), rs in lits.items():
        scored = sorted([r for r in rs if usable(r)], key=lambda r: -int(r["pageviews"]))[:MAX_READINGS]
        if len(scored) < 2: continue
        ratio = int(scored[0]["pageviews"]) / max(int(scored[1]["pageviews"]), 1)
        band = "balanced" if ratio < 3 else "dominated" if ratio >= 10 else "middle"
        chosen[s].append((lit, band, ratio, scored, rs))
    final = []
    for s in sorted(chosen):
        bal = [c for c in chosen[s] if c[1] == "balanced"][:PER_STRATUM // 2]
        dom = [c for c in chosen[s] if c[1] == "dominated"][:PER_STRATUM // 2]
        rest = [c for c in chosen[s] if c not in bal and c not in dom]
        pick = bal + dom + rest[:PER_STRATUM - len(bal) - len(dom)]
        print(f"{s}: eligible {len(chosen[s])}, picked {len(pick)} (balanced {len(bal)}, dominated {len(dom)})")
        final += [(s, *c) for c in pick]
    pool = collections.defaultdict(list)
    for r in pre:
        if r["role"] == "control" and usable(r): pool[(r["system_id"], len(r["literal"]))].append(r)
    gold, used = [], set()
    for s, lit, band, ratio, scored, rs in sorted(final, key=lambda x: (x[0], x[1])):
        comp = [{"system_id": r["system_id"], "label": r["label"], "aliases": aliases(r, ex[(r["system_id"], lit)][1])} for r in rs]
        for r in scored:
            e, ea = ex[(r["system_id"], lit)]
            rid = f"{lit}|{r['system_id']}"
            gold.append(dict(id=rid, role="collision", stratum=s, band=band, ratio=round(ratio, 2), literal=lit,
                             system_id=r["system_id"], namespace=NS[r["system_id"]], label=r["label"],
                             aliases=json.dumps(aliases(r, ea)), desc=desc(r["system_id"], r["label"], e),
                             pageviews=r["pageviews"], wp_title=r["wp_title"], wd_item=r["wd_item"],
                             competitors=json.dumps([c for c in comp if c["system_id"] != r["system_id"]]),
                             match_of="", match_factor="", other_systems=r["other_systems"]))
            p = math.log10(int(r["pageviews"]))
            cands = [c for c in pool[(r["system_id"], len(lit))] if c["literal"] not in used]
            best = sorted(cands, key=lambda c: abs(math.log10(int(c["pageviews"])) - p))
            for factor in (2, 4):
                ok = [c for c in best if abs(math.log10(int(c["pageviews"])) - p) <= math.log10(factor)]
                if ok:
                    c = ok[0]; used.add(c["literal"]); ce, cea = ex[(c["system_id"], c["literal"])]
                    gold.append(dict(id=f"{c['literal']}|{c['system_id']}", role="control", stratum=s, band="", ratio="",
                                     literal=c["literal"], system_id=c["system_id"], namespace=NS[c["system_id"]], label=c["label"],
                                     aliases=json.dumps(aliases(c, cea)), desc=desc(c["system_id"], c["label"], ce),
                                     pageviews=c["pageviews"], wp_title=c["wp_title"], wd_item=c["wd_item"], competitors="[]",
                                     match_of=rid, match_factor=factor, other_systems=c["other_systems"]))
                    break
    by_ns = collections.defaultdict(list)
    for g in gold: by_ns[g["system_id"]].append(g)
    for g in gold:
        foils = [f for f in by_ns[g["system_id"]] if f["literal"] != g["literal"]]
        g["foil_desc"] = rng.choice(foils)["desc"] if foils else ""
    with open(f"{data}/gold_draft.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(gold[0])); w.writeheader(); w.writerows(gold)
    n_lit = len({g["literal"] for g in gold if g["role"] == "collision"})
    print(f"collision literals {n_lit}, collision readings {sum(g['role'] == 'collision' for g in gold)}, "
          f"controls {sum(g['role'] == 'control' for g in gold)}, factor-4 controls {sum(g['match_factor'] == 4 for g in gold)}")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
