"""Deterministic scoring and analysis, following docs/PROTOCOL.md.

usage: python score.py <gold.csv> <calls.jsonl> <out_dir> <run1.jsonl> [run2.jsonl ...]
"""
import collections
import csv
import json
import os
import random
import re
import sys
import unicodedata

SEED, B = 20261014, 10000
GENERIC = {"airport", "international", "airlines", "airline", "inc", "corporation", "corp", "company", "co", "ltd", "plc", "the"}


def toks(s):
    s = unicodedata.normalize("NFKD", s or "")
    s = "".join(ch for ch in s if not unicodedata.combining(ch)).casefold()
    return re.sub(r"[^0-9a-z]+", " ", s).split()


def cores(aliases, literal):
    out = []
    for a in aliases:
        t = toks(a)
        if len(a.strip()) <= 3 or t == [literal.casefold()]:
            continue  # a bare code is not an entity name
        c = frozenset(x for x in t if x not in GENERIC)
        if c: out.append(c)
    return out


def hit(text, core_list):
    t = set(toks(text))
    return any(c <= t for c in core_list)


def parse(content):
    try:
        d = json.loads(content)
        return d if isinstance(d, dict) else None
    except (TypeError, json.JSONDecodeError):
        m = re.search(r"\{.*\}", content or "", re.S)
        try:
            return json.loads(m.group(0)) if m else None
        except json.JSONDecodeError:
            return None


def classify(d, target, competitors):
    if d is None or d.get("status") not in ("answer", "ambiguous", "unknown"): return "FORMAT"
    if d["status"] == "unknown": return "UNKNOWN"
    if d["status"] == "ambiguous": return "AMBIG_FLAG"
    text = " ; ".join(str(r.get("entity", "")) for r in d.get("readings") or [] if isinstance(r, dict))
    a, b = hit(text, target), any(hit(text, c) for c in competitors)
    return "CORRECT" if a and not b else "COMPETING" if b and not a else "BOTH" if a and b else "OTHER_WRONG"


def c1_class(d, readings, top_id, is_control):
    if d is None or d.get("status") not in ("answer", "ambiguous", "unknown"): return "FORMAT", ""
    if d["status"] == "unknown": return "UNKNOWN", ""
    text = " ; ".join(str(r.get("entity", "")) for r in d.get("readings") or [] if isinstance(r, dict))
    matched = [rid for rid, c in readings.items() if hit(text, c)]
    if is_control:
        if d["status"] == "ambiguous": return "FALSE_ALARM", ""
        return ("SINGLE_CORRECT" if matched else "WRONG"), ""
    if len(matched) >= 2: return "MULTI", ""
    if d["status"] == "ambiguous": return "PARTIAL", ""
    if len(matched) == 1: return "SINGLE", ("top" if matched[0] == top_id else "other")
    return "WRONG", ""


def boot(values_by_cluster, fn, rng):
    keys = list(values_by_cluster)
    est = fn([v for k in keys for v in values_by_cluster[k]])
    sims = sorted(fn([v for k in (rng.choice(keys) for _ in keys) for v in values_by_cluster[k]]) for _ in range(B))
    return est, sims[int(0.025 * B)], sims[int(0.975 * B) - 1]


def mean(x): return sum(x) / len(x) if x else float("nan")


def main(gold_p, calls_p, out_dir, *runs):
    rng = random.Random(SEED)
    gold = {g["id"]: g for g in csv.DictReader(open(gold_p, encoding="utf-8"))}
    calls = {c["call_id"]: c for c in map(json.loads, open(calls_p, encoding="utf-8"))}
    tgt = {i: cores(json.loads(g["aliases"]), g["literal"]) for i, g in gold.items()}
    comp = {i: [cores(c["aliases"] + [c["label"]], g["literal"]) for c in json.loads(g["competitors"])] for i, g in gold.items()}
    lit_readings = collections.defaultdict(dict)
    for i, g in gold.items():
        if g["role"] == "collision":
            lit_readings[g["literal"]][i] = tgt[i]
            for c in json.loads(g["competitors"]):
                lit_readings[g["literal"]].setdefault(f"{g['literal']}|{c['system_id']}", cores(c["aliases"] + [c["label"]], g["literal"]))
    top = {}
    for i, g in gold.items():
        if g["role"] == "collision" and int(g["pageviews"]) >= int(gold.get(top.get(g["literal"], i), g)["pageviews"]): top[g["literal"]] = i
    os.makedirs(out_dir, exist_ok=True)
    rows, summary = [], {}
    for run in runs:
        res = [json.loads(l) for l in open(run, encoding="utf-8")]
        res = {r["call_id"]: r for r in res if r.get("http") == 200 or r["call_id"] not in {x["call_id"] for x in res if x.get("http") == 200}}
        model = next(iter(res.values()))["model"]
        cat = {}
        for cid, r in res.items():
            c = calls[cid]; d = parse(r.get("content"))
            if c["cond"] in ("C2", "C3", "C4"):
                k = classify(d, tgt[c["item"]], comp[c["item"]]); extra = ""
            elif c["cond"] == "C1":
                role, lit = c["item"].split("|", 1)
                if role == "control":
                    gid = next(i for i, g in gold.items() if g["literal"] == lit and g["role"] == "control")
                    k, extra = c1_class(d, {gid: tgt[gid]}, gid, True)
                else:
                    k, extra = c1_class(d, lit_readings[lit], top[lit], False)
            elif c["cond"] == "P1":
                k = "PASS" if d and str(d.get("code", "")).strip().casefold() == gold[c["item"]]["literal"].casefold() else "FAIL"; extra = ""
            else:
                k = (d or {}).get("answer", "FORMAT"); extra = ""
            cat[cid] = k
            rows.append({"model": model, "call_id": cid, "cond": c["cond"], "item": c["item"], "var": c["var"], "category": k,
                         "detail": extra, "content": (r.get("content") or "")[:300]})
        p2 = {i: cat.get(f"P2T|{i}|0") == "yes" and cat.get(f"P2F|{i}|0") == "no" for i in gold}
        p1 = {i: cat.get(f"P1|{i}|0") == "PASS" for i in gold}
        err = lambda i, cond: 1 - mean([cat.get(f"{cond}|{i}|{v}") == "CORRECT" for v in range(3)])
        S = {"n_calls": len(res), "http_fail": sum(r.get("http") != 200 for r in res.values()),
             "format": sum(v == "FORMAT" for v in cat.values()),
             "p1_pass": mean(list(p1.values())), "p2_pass": mean(list(p2.values())),
             "p1_p2_agree": mean([p1[i] == p2[i] for i in gold]),
             "p1_p2_table": collections.Counter(f"P1={p1[i]},P2={p2[i]}" for i in gold)}
        for cond in ("C2", "C3", "C4"):
            pairs = collections.defaultdict(list)
            for i, g in gold.items():
                if g["role"] == "control" and p2[i] and p2.get(g["match_of"]):
                    pairs[gold[g["match_of"]]["literal"]].append(err(g["match_of"], cond) - err(i, cond))
            S[f"E1_{cond}"] = dict(zip(("delta", "lo", "hi"), boot(pairs, mean, rng))) | {"pairs": sum(map(len, pairs.values())), "literals": len(pairs)} if pairs else None
            known_coll = [i for i, g in gold.items() if g["role"] == "collision" and p2[i]]
            ctrl_known = [i for i, g in gold.items() if g["role"] == "control" and p2[i]]
            S[f"{cond}_err_known_collision"] = mean([err(i, cond) for i in known_coll])
            S[f"{cond}_err_known_control"] = mean([err(i, cond) for i in ctrl_known])
            S[f"{cond}_categories_known_collision"] = collections.Counter(cat.get(f"{cond}|{i}|{v}") for i in known_coll for v in range(3))
            S[f"{cond}_categories_unknown_collision"] = collections.Counter(cat.get(f"{cond}|{i}|{v}") for i, g in gold.items() if g["role"] == "collision" and not p2[i] for v in range(3))
            S[f"{cond}_categories_known_control"] = collections.Counter(cat.get(f"{cond}|{i}|{v}") for i in ctrl_known for v in range(3))
            S[f"{cond}_variant_err_known_collision"] = [mean([cat.get(f"{cond}|{i}|{v}") != "CORRECT" for i in known_coll]) for v in range(3)]
        c1 = collections.defaultdict(list)
        for cid, k in cat.items():
            if calls[cid]["cond"] == "C1": c1[calls[cid]["item"].split("|")[0]].append(k)
        S["E3_C1_collision"] = collections.Counter(c1["collision"]); S["E3_C1_control"] = collections.Counter(c1["control"])
        by_lit = collections.defaultdict(list)
        for cid, k in cat.items():
            if calls[cid]["cond"] == "C1" and calls[cid]["item"].startswith("collision|"): by_lit[calls[cid]["item"]].append(k == "SINGLE")
        S["E3_single_rate"] = dict(zip(("est", "lo", "hi"), boot(by_lit, mean, rng)))
        fa = collections.defaultdict(list)
        for cid, k in cat.items():
            if calls[cid]["cond"] == "C1" and calls[cid]["item"].startswith("control|"): fa[calls[cid]["item"]].append(k == "FALSE_ALARM")
        S["E3_false_alarm_rate"] = dict(zip(("est", "lo", "hi"), boot(fa, mean, rng)))
        S["E3_single_which"] = collections.Counter(r["detail"] for r in rows if r["model"] == model and r["cond"] == "C1" and r["category"] == "SINGLE")
        summary[model] = S
    with open(f"{out_dir}/scored.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
    json.dump(summary, open(f"{out_dir}/summary.json", "w"), indent=1, default=dict)
    print(json.dumps(summary, indent=1, default=dict)[:6000])


if __name__ == "__main__":
    main(*sys.argv[1:])
