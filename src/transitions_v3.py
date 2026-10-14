"""Trace every category change between v1, v2 and v3, with the v3 evidence that explains it, and the effect on E1.

usage: python transitions_v3.py <gold.csv> <results_v1> <results_v2> <results_v3>
Writes results_v3/transitions.csv and results_v3/DIFF.md.
"""
import collections
import csv
import os
import random
import sys

sys.path.insert(0, os.path.dirname(__file__))
import analyze_v3 as A  # noqa: E402

RENAME = {"FALSE_ALARM": "AMBIG_DECLARED"}


def load_scored(d):
    return {(r["model"], r["call_id"]): r for r in csv.DictReader(open(f"{d}/scored.csv", encoding="utf-8"))}


def reason(v_old, r3, reads):
    ev = sorted({x["evidence"] for x in reads}); ents = sorted({x["entity"] for x in reads})
    if r3["cond"] in ("P1", "P2T", "P2F"): return "probe: FORMAT split from FAIL"
    if r3["category"] == "FORMAT" or v_old == "FORMAT": return "format"
    if r3["category"] in ("UNKNOWN", "AMBIG_FLAG") or v_old in ("UNKNOWN", "AMBIG_FLAG"): return "status"
    if v_old == "FALSE_ALARM": return "rename FALSE_ALARM to AMBIG_DECLARED"
    if r3["category"] == "MIXED": return "multiple readings, wrong claims no longer discarded"
    if r3["category"] == "UNRESOLVED": return "no strong alias match: " + ",".join(ev)
    if v_old in ("BOTH", "COMPETING") and r3["category"] == "CORRECT": return "whole-alias match: competitor hit was a token subset"
    if v_old == "BOTH" and r3["category"] == "COMPETING": return "whole-alias match: competitor exact, target was a token subset"
    if v_old in ("CORRECT", "SINGLE", "SINGLE_CORRECT", "MULTI") and r3["category"] in ("OTHER_WRONG", "WRONG", "COMPETING"): return "subset match removed: " + ",".join(ents)
    if v_old in ("OTHER_WRONG", "WRONG") and r3["category"] in ("CORRECT", "SINGLE", "SINGLE_CORRECT", "MULTI"): return "alias now active or suffix/bag equality: " + ",".join(ev)
    return f"{v_old}->{r3['category']}: " + ",".join(ev)


def main(gold_p, d1, d2, d3):
    gold = {g["id"]: g for g in csv.DictReader(open(gold_p, encoding="utf-8"))}
    v1, v2, v3 = load_scored(d1), load_scored(d2), load_scored(d3)
    reads = collections.defaultdict(list)
    for r in csv.DictReader(open(f"{d3}/readings.csv", encoding="utf-8")): reads[(r["model"], r["call_id"])].append(r)
    rows = []
    for k, r3 in v3.items():
        a, b = RENAME.get(v1[k]["category"], v1[k]["category"]), RENAME.get(v2[k]["category"], v2[k]["category"])
        rows.append({"model": A.short(k[0]), "call_id": k[1], "cond": r3["cond"], "v1": a, "v2": b, "v3": r3["category"],
                     "changed_v2_v3": a != r3["category"] or b != r3["category"], "reason": reason(b, r3, reads[k]) if b != r3["category"] else "",
                     "content": r3["content"][:120]})
    with open(f"{d3}/transitions.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
    grp = lambda c: "C1" if c == "C1" else "C234" if c in ("C2", "C3", "C4") else "probes"
    mats = {("v1", "v3"): collections.defaultdict(collections.Counter), ("v2", "v3"): collections.defaultdict(collections.Counter)}
    for r in rows:
        mats[("v1", "v3")][grp(r["cond"])][(r["v1"], r["v3"])] += 1; mats[("v2", "v3")][grp(r["cond"])][(r["v2"], r["v3"])] += 1
    e1 = {}
    for tag, d in (("v1", d1), ("v2", d2), ("v3", d3)):
        rowsd = collections.defaultdict(dict)
        for r in csv.DictReader(open(f"{d}/scored.csv", encoding="utf-8")): rowsd[r["model"]][r["call_id"]] = r
        for m, cat in rowsd.items():
            fam = A.familiarity(gold, cat)
            for cond in ("C2", "C3"): e1[(tag, A.short(m), cond)] = A.e1(gold, cat, fam["P2"], cond, "primary", random.Random(A.SEED))
    with open(f"{d3}/DIFF.md", "w", encoding="utf-8") as fh:
        fh.write("# Transições v1 → v2 → v3\n\nGerado por `src/transitions_v3.py`. Cada mudança por call_id, com a evidência v3 responsável, está em `results_v3/transitions.csv`.\n\n")
        n = len([r for r in rows if r["cond"] not in ("P1", "P2T", "P2F")]); ch = sum(r["changed_v2_v3"] for r in rows if r["cond"] not in ("P1", "P2T", "P2F"))
        pr = sum(r["v2"] != r["v3"] for r in rows if r["cond"] in ("P1", "P2T", "P2F"))
        fh.write(f"- Respostas C1 a C4: {n}; com categoria diferente entre alguma versão anterior e a v3: {ch} ({100 * ch / n:.1f}%). Sondas P1 e P2 com diferença v2 → v3: {pr}.\n\n")
        for (x, y), groups in mats.items():
            for g, cm in sorted(groups.items()):
                cats = sorted({c for p in cm for c in p}); fh.write(f"## {x} → {y}, {g}\n\n| {x} \\ {y} | " + " | ".join(cats) + " |\n|---|" + "---|" * len(cats) + "\n")
                for a in cats: fh.write(f"| {a} | " + " | ".join(str(cm[(a, b)]) if cm[(a, b)] else "" for b in cats) + " |\n")
                fh.write("\n")
        fh.write("## Regras responsáveis pelas mudanças v2 → v3\n\n| regra | n | exemplo (call_id) |\n|---|---:|---|\n")
        reasons = collections.defaultdict(list)
        for r in rows:
            if r["reason"]: reasons[r["reason"].split(":")[0]].append(r)
        for k, rs in sorted(reasons.items(), key=lambda x: -len(x[1])):
            ex = rs[0]; fh.write(f"| {k} | {len(rs)} | {ex['model']} {ex['call_id']} {ex['v2']}→{ex['v3']} |\n")
        fh.write("\n## Efeito sobre E1 primário, recorte P2\n\n| modelo | cond | v1 | v2 | v3 |\n|---|---|---|---|---|\n")
        for m in sorted({k[1] for k in e1}):
            for cond in ("C2", "C3"): fh.write(f"| {m} | {cond} | " + " | ".join(A.fmt(e1[(t, m, cond)]) for t in ("v1", "v2", "v3")) + " |\n")
    print("changed:", sum(r["changed_v2_v3"] for r in rows), "of", len(rows)); print({k: len(v) for k, v in reasons.items()})


if __name__ == "__main__":
    main(*sys.argv[1:])
