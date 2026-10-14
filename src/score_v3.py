"""Post-hoc scorer v3, following docs/AUDIT_PROTOCOL.md. Three independent dimensions per response:
entity (per reading), namespace (per reading) and behaviour (per response). No model calls, no gold edits.

usage: python score_v3.py <gold.csv> <calls.jsonl> <canon.json> <out_dir> <run1.jsonl> [run2.jsonl ...]
       python score_v3.py --alias-policy <gold.csv> <out.csv>
"""
import csv
import json
import re
import sys
import unicodedata

GENERIC = {"airport", "international", "airlines", "airline", "inc", "corporation", "corp", "company", "co", "ltd", "plc", "the",
           "of", "record", "dns", "currency", "code", "dollar", "peso"}
WRAPPER = {"the", "of", "a", "an", "republic", "state", "sultanate", "kingdom", "nation", "country", "island", "islands",
           "currency", "code", "record", "type", "dns", "inc", "incorporated", "corp", "corporation", "co", "company", "ltd", "limited", "plc", "llc"}
EXCLUDED_ALIASES = {"null", "peso", "dollar", "dollars"}
STATUS = ("answer", "ambiguous", "unknown")


def norm(s):
    s = unicodedata.normalize("NFKD", str(s if s is not None else ""))
    s = "".join(ch for ch in s if not unicodedata.combining(ch)).casefold()
    return " ".join(re.sub(r"[^0-9a-z]+", " ", s).split())


# ---------------------------------------------------------------- aliases
def alias_policy(alias, literal):
    """Return the reason an alias is inactive, or '' when it is an entity name."""
    raw = alias.strip(); n = norm(raw)
    if not n: return "empty_after_normalisation"
    if n == norm(literal): return "equals_literal"
    if raw.casefold() in EXCLUDED_ALIASES: return "generic_or_null"
    if len(n) <= 3 and not (len(raw) == 3 and raw.isalpha() and raw[0].isupper() and raw[1:].islower()): return "code_like_short"
    if raw.isupper() and len(re.sub(r"[^0-9A-Za-z]", "", raw)) <= 4: return "code_like_upper"
    return ""


def active_aliases(aliases, label, literal):
    out = []
    for a in [label] + list(aliases):
        if not alias_policy(a, literal) and norm(a) not in out: out.append(norm(a))
    return out


def export_alias_policy(gold_p, out_p):
    rows = []
    for g in csv.DictReader(open(gold_p, encoding="utf-8")):
        for a in [g["label"]] + json.loads(g["aliases"]):
            rows.append({"id": g["id"], "alias": a, "normalised": norm(a), "status": alias_policy(a, g["literal"]) or "active"})
        for c in json.loads(g["competitors"]):
            for a in [c["label"]] + c["aliases"]:
                rows.append({"id": f"{g['literal']}|{c['system_id']} (competitor of {g['id']})", "alias": a, "normalised": norm(a),
                             "status": alias_policy(a, g["literal"]) or "active"})
    with open(out_p, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
    return rows


# ---------------------------------------------------------------- entity
def match_level(e_norm, alias_norms, literal_norm):
    """'exact', 'phrase', 'partial' or '' for one entity string against one alias set."""
    et = e_norm.split(); eset = set(et); level = ""
    for a in alias_norms:
        at = a.split()
        if e_norm == a or eset == set(at): return "exact"
        if len(at) >= 2 and f" {a} " in f" {e_norm} ": level = "phrase"
        elif len(at) == 1 and at[0] in eset and all(t in WRAPPER or t == at[0] or t == literal_norm for t in et): level = "phrase"
        elif not level and (eset - GENERIC) & (set(at) - GENERIC): level = "partial"
    return level


def entity_eval(entity_raw, readings, literal, target_sid=None):
    """readings: {sid: alias_norms}. Returns (entity, evidence, matched_sid)."""
    e = norm(entity_raw); ln = norm(literal)
    if alias_policy(str(entity_raw if entity_raw is not None else ""), literal): return "UNRESOLVED", "no_entity", ""
    levels = {sid: match_level(e, al, ln) for sid, al in readings.items()}
    strong = [sid for sid, l in levels.items() if l in ("exact", "phrase")]
    partial = [sid for sid, l in levels.items() if l == "partial"]
    if len(strong) == 1:
        sid = strong[0]
        if target_sid is None or sid == target_sid: return "CORRECT", levels[sid], sid
        return "COMPETITOR", levels[sid], sid
    if len(strong) > 1: return "UNRESOLVED", "both", ";".join(sorted(strong))
    if partial:
        if target_sid is None: ev = "partial"
        elif target_sid in partial: ev = "partial_both" if len(partial) > 1 else "partial_target"
        else: ev = "partial_competitor"
        return "UNRESOLVED", ev, ";".join(sorted(partial))
    return "OTHER", "none", ""


# ---------------------------------------------------------------- namespace
class Canon:
    def __init__(self, path):
        d = json.load(open(path, encoding="utf-8"))
        self.rules = [(re.compile(r["pattern"]), r) for r in d["rules"]]
        self.asked = {k: v["canon"] for k, v in d["asked"].items()}
        self.org = d["org_equivalent_for"]

    def canon(self, system_raw):
        s = norm(system_raw)
        for rx, r in self.rules:
            if rx.search(s): return s, r["canon"], r["rule"], r["confidence"]
        return s, "", "none", ""

    def evaluate(self, asked_sid, c):
        _, canon, rule, conf = c
        if not canon: return "UNRESOLVED"
        want = self.asked[asked_sid]
        if canon == want: return "CORRECT" if conf == "high" else "EQUIVALENT"
        if canon.startswith("org/") and self.org.get(canon) == want: return "EQUIVALENT"
        return "INCORRECT"


# ---------------------------------------------------------------- response
def parse(content):
    try:
        d = json.loads(content)
        return d if isinstance(d, dict) else None
    except (TypeError, json.JSONDecodeError):
        m = re.search(r"\{.*\}", content or "", re.S)
        try:
            d = json.loads(m.group(0)) if m else None
            return d if isinstance(d, dict) else None
        except json.JSONDecodeError:
            return None


def behaviour(record, d):
    if d is None: return "FAILURE", "TRUNCATED" if record.get("finish") == "length" else "INVALID_JSON"
    if d.get("status") not in STATUS or not isinstance(d.get("readings"), list): return "FAILURE", "SCHEMA"
    if d["status"] == "unknown": return "ABSTAIN", ""
    if d["status"] == "ambiguous": return "AMBIGUOUS", ""
    n = sum(isinstance(x, dict) for x in d["readings"])
    return ("SINGLE" if n == 1 else "MULTI" if n > 1 else "FAILURE"), ("" if n else "SCHEMA")


def score_readings(d, readings, literal, canon, target_sid, sid_of):
    """One dict per reading. sid_of maps a gold reading id to its system_id."""
    out = []
    for i, rd in enumerate([x for x in (d or {}).get("readings") or [] if isinstance(x, dict)]):
        ent, ev, mid = entity_eval(rd.get("entity"), readings, literal, target_sid)
        c = canon.canon(rd.get("system"))
        ref = target_sid if target_sid is not None else (mid if ent == "CORRECT" else "")
        ns = canon.evaluate(sid_of[ref], c) if ref in sid_of else ""
        out.append({"idx": i, "system_raw": rd.get("system"), "system_norm": c[0], "ns_canon": c[1], "ns_rule": c[2], "ns_confidence": c[3],
                    "ns_eval": ns, "entity_raw": rd.get("entity"), "entity_norm": norm(rd.get("entity")), "entity": ent, "evidence": ev, "matched": mid})
    return out


def derive_c234(beh, reads):
    if beh == "FAILURE": return "FORMAT"
    if beh == "ABSTAIN": return "UNKNOWN"
    if beh == "AMBIGUOUS": return "AMBIG_FLAG"
    ents = [r["entity"] for r in reads]
    if ents and all(e == "CORRECT" for e in ents): return "CORRECT"
    if "CORRECT" in ents: return "MIXED"
    if "COMPETITOR" in ents: return "COMPETING"
    if "UNRESOLVED" in ents: return "UNRESOLVED"
    return "OTHER_WRONG"


def derive_c1(beh, reads, is_control, top_id):
    matched = {r["matched"] for r in reads if r["entity"] == "CORRECT"}
    unres = any(r["entity"] == "UNRESOLVED" and r["evidence"] != "no_entity" for r in reads)
    if beh == "FAILURE": return "FORMAT", ""
    if beh == "ABSTAIN": return "UNKNOWN", ""
    if is_control:
        if beh == "AMBIGUOUS": return "AMBIG_DECLARED", "with_target" if matched else "without_target"
        if matched: return "SINGLE_CORRECT", ""
        return ("UNRESOLVED" if unres else "WRONG"), ""
    if len(matched) >= 2: return "MULTI", ""
    if beh == "AMBIGUOUS": return "PARTIAL", "with_one" if matched else "with_none"
    if len(matched) == 1: return "SINGLE", "top" if next(iter(matched)) == top_id else "other"
    return ("UNRESOLVED" if unres else "WRONG"), ""


def ns_of_correct(reads):
    vals = [r["ns_eval"] for r in reads if r["entity"] == "CORRECT"]
    for v in ("CORRECT", "EQUIVALENT", "UNRESOLVED", "INCORRECT"):
        if v in vals: return v
    return ""


# ---------------------------------------------------------------- driver
def load_gold(gold_p):
    gold = {g["id"]: g for g in csv.DictReader(open(gold_p, encoding="utf-8"))}
    readings = {}       # per gold id: {sid: alias_norms} covering target and competitors
    sid_of = {}         # reading id -> system_id, for every target and competitor
    lit_readings = {}   # literal -> {reading id: alias_norms}, collision literals only
    for i, g in gold.items():
        readings[i] = {i: active_aliases(json.loads(g["aliases"]), g["label"], g["literal"])}
        sid_of[i] = g["system_id"]
        for c in json.loads(g["competitors"]):
            cid = f"{g['literal']}|{c['system_id']}"
            readings[i][cid] = active_aliases(c["aliases"], c["label"], g["literal"]); sid_of[cid] = c["system_id"]
        if g["role"] == "collision": lit_readings.setdefault(g["literal"], {}).update(readings[i])
    top = {}
    for i, g in gold.items():
        if g["role"] == "collision" and int(g["pageviews"]) >= int(gold[top[g["literal"]]]["pageviews"] if g["literal"] in top else 0): top[g["literal"]] = i
    ctrl_of_lit = {g["literal"]: i for i, g in gold.items() if g["role"] == "control"}
    return gold, readings, sid_of, lit_readings, top, ctrl_of_lit


def definitive(run_p):
    out = {}
    for l in open(run_p, encoding="utf-8"):
        r = json.loads(l)
        if r.get("http") == 200 or r["call_id"] not in out: out[r["call_id"]] = r
    return out


def score_run(run_p, gold, calls, canon, G):
    gold_rows, readings, sid_of, lit_readings, top, ctrl_of_lit = G
    rows, reads_out = [], []
    for cid, r in definitive(run_p).items():
        c = calls[cid]; d = parse(r.get("content")); beh, fail = behaviour(r, d)
        row = {"model": r["model"], "call_id": cid, "cond": c["cond"], "item": c["item"], "var": c["var"], "behaviour": beh, "failure_type": fail,
               "n_readings": 0, "category": "", "detail": "", "has_correct": "", "has_competitor": "", "ns_of_correct": "", "matched": "",
               "content": (r.get("content") or "")[:300]}
        reads = []
        if c["cond"] in ("C2", "C3", "C4"):
            g = gold_rows[c["item"]]
            reads = score_readings(d, readings[c["item"]], g["literal"], canon, c["item"], sid_of)
            row["category"] = derive_c234(beh, reads)
        elif c["cond"] == "C1":
            role, lit = c["item"].split("|", 1)
            rset = lit_readings[lit] if role == "collision" else readings[ctrl_of_lit[lit]]
            reads = score_readings(d, rset, lit, canon, None, sid_of)
            row["category"], row["detail"] = derive_c1(beh, reads, role == "control", top.get(lit))
        elif c["cond"] == "P1":
            row["category"] = "FORMAT" if d is None else "UNKNOWN" if d.get("status") == "unknown" else \
                "PASS" if str(d.get("code", "")).strip().casefold() == gold_rows[c["item"]]["literal"].casefold() else "FAIL"
        else:
            row["category"] = (d or {}).get("answer", "FORMAT")
        if reads:
            row.update(n_readings=len(reads), has_correct=any(x["entity"] == "CORRECT" for x in reads),
                       has_competitor=any(x["entity"] == "COMPETITOR" for x in reads), ns_of_correct=ns_of_correct(reads),
                       matched=";".join(sorted({x["matched"] for x in reads if x["entity"] == "CORRECT"})))
            reads_out += [{"model": r["model"], "call_id": cid, **x} for x in reads]
        rows.append(row)
    return rows, reads_out


def main(gold_p, calls_p, canon_p, out_dir, *runs):
    import os
    os.makedirs(out_dir, exist_ok=True)
    G = load_gold(gold_p); canon = Canon(canon_p)
    calls = {c["call_id"]: c for c in map(json.loads, open(calls_p, encoding="utf-8"))}
    rows, reads = [], []
    for run in runs:
        a, b = score_run(run, G[0], calls, canon, G); rows += a; reads += b
    for name, data in (("scored.csv", rows), ("readings.csv", reads)):
        with open(f"{out_dir}/{name}", "w", newline="", encoding="utf-8") as fh:
            w = csv.DictWriter(fh, fieldnames=list(data[0])); w.writeheader(); w.writerows(data)
    print(f"{len(rows)} responses, {len(reads)} readings -> {out_dir}")


if __name__ == "__main__":
    if sys.argv[1] == "--alias-policy":
        rows = export_alias_policy(sys.argv[2], sys.argv[3]); print(len(rows), "aliases;", sum(r["status"] != "active" for r in rows), "inactive")
    else:
        main(*sys.argv[1:])
