"""Stratified validation sample for the v3 instrument, drawn before the blind review.

usage: python sample_review.py <gold.csv> <calls.jsonl> <results_v3_dir> <results_v2_scored.csv> <audit_dir> <n_per_model> <run1.jsonl> ...
The content column is the full definitive raw response from the run files.
Frame: C1 to C4 responses whose literal is not in the development set. Strata: model x condition x group, where group is
'changed' when the v2 and v3 categories differ, else the v3 category family. Seats per (model, condition) cell are filled
round-robin over groups from seeded shuffles, so every group present in a cell is represented.
Writes review_sample.csv (no automatic categories), review_sample_strata.csv (sealed) and review_sample.sha256.
"""
import csv
import hashlib
import json
import random
import sys

SEED = 20261014
DEV = {"ARU", "OMA", "BRU", "JEY", "LYB", "A", "ALL", "JMD", "FIJ", "MYA", "VAN", "DTE"}
QUOTA = {"C2": 14, "C3": 14, "C4": 8, "C1": 12}
FAMILY = {"CORRECT": "correct", "SINGLE_CORRECT": "correct", "SINGLE": "correct", "MULTI": "correct",
          "COMPETING": "wrong", "OTHER_WRONG": "wrong", "WRONG": "wrong",
          "UNRESOLVED": "unresolved", "MIXED": "unresolved", "PARTIAL": "hedge", "AMBIG_FLAG": "hedge", "AMBIG_DECLARED": "hedge",
          "UNKNOWN": "hedge", "FORMAT": "format"}
RENAME = {"FALSE_ALARM": "AMBIG_DECLARED"}


def literal_of(row):
    return row["item"].split("|")[1] if row["cond"] == "C1" else row["item"].split("|")[0]


def main(gold_p, calls_p, v3_dir, v2_scored, audit_dir, n_per_model, *runs):
    gold = {g["id"]: g for g in csv.DictReader(open(gold_p, encoding="utf-8"))}
    calls = {c["call_id"]: c for c in map(json.loads, open(calls_p, encoding="utf-8"))}
    v2 = {(r["model"], r["call_id"]): RENAME.get(r["category"], r["category"]) for r in csv.DictReader(open(v2_scored, encoding="utf-8"))}
    frame = [r for r in csv.DictReader(open(f"{v3_dir}/scored.csv", encoding="utf-8")) if r["cond"] in QUOTA and literal_of(r) not in DEV]
    full = {}
    for run in runs:
        for l in open(run, encoding="utf-8"):
            x = json.loads(l)
            if x.get("http") == 200 or (x["model"], x["call_id"]) not in full: full[(x["model"], x["call_id"])] = x.get("content") or ""
    cells = {}
    for r in frame:
        g = "changed" if v2[(r["model"], r["call_id"])] != r["category"] else FAMILY[r["category"]]
        cells.setdefault((r["model"], r["cond"]), {}).setdefault(g, []).append(r)
    rng = random.Random(SEED); picked = []
    for (model, cond), groups in sorted(cells.items()):
        pools = {g: rng.sample(rows, len(rows)) for g, rows in sorted(groups.items())}
        quota = round(QUOTA[cond] * int(n_per_model) / 48); order = sorted(pools)
        while quota and any(pools.values()):
            for g in order:
                if pools[g] and quota: picked.append((pools[g].pop(), g)); quota -= 1
    sample, strata = [], []
    for r, g in picked:
        c = calls[r["call_id"]]
        if r["cond"] == "C1":
            role, lit = r["item"].split("|", 1)
            ids = [i for i, x in gold.items() if x["literal"] == lit and x["role"] == role]
            target = "; ".join(f"{gold[i]['system_id']}: {gold[i]['label']}" for i in ids)
            comp = "; ".join(f"{x['system_id']}: {x['label']}" for x in json.loads(gold[ids[0]]["competitors"])) if ids else ""
        else:
            g0 = gold[r["item"]]; target = f"{g0['system_id']}: {g0['label']} | aliases {g0['aliases']}"
            comp = "; ".join(f"{x['system_id']}: {x['label']}" for x in json.loads(g0["competitors"]))
        sample.append({"model": r["model"], "call_id": r["call_id"], "cond": r["cond"], "literal": literal_of(r), "gold_readings": target,
                       "other_readings_of_literal": comp, "prompt": c["prompt"].split("\n\nRespond only")[0], "content": full[(r["model"], r["call_id"])]})
        strata.append({"model": r["model"], "call_id": r["call_id"], "group": g})
    for name, data in (("review_sample.csv", sample), ("review_sample_strata.csv", strata)):
        with open(f"{audit_dir}/{name}", "w", newline="", encoding="utf-8") as fh:
            w = csv.DictWriter(fh, fieldnames=list(data[0])); w.writeheader(); w.writerows(data)
    with open(f"{audit_dir}/review_sample.sha256", "w") as fh:
        for name in ("review_sample.csv", "review_sample_strata.csv"):
            fh.write(f"{hashlib.sha256(open(f'{audit_dir}/{name}', 'rb').read()).hexdigest()}  {name}\n")
    print(len(sample), "sampled from a frame of", len(frame))
    import collections
    print(collections.Counter((s["cond"], g) for s, g in zip(sample, (x["group"] for x in strata))))


if __name__ == "__main__":
    main(*sys.argv[1:])
