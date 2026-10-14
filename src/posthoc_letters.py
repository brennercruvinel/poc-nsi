"""Post hoc, exploratory: are wrong answers built from the code's letters more often than true names are?

usage: python posthoc_letters.py <gold.csv> <scored.csv>
"""
import collections
import csv
import json
import re
import sys
import unicodedata

STOP = {"airport", "international", "airlines", "airline", "inc", "corporation", "corp", "company", "co", "ltd", "plc",
        "the", "of", "and", "de", "la", "del", "air", "regional", "municipal", "field", "airfield", "base"}


def words(s):
    s = unicodedata.normalize("NFKD", s or ""); s = "".join(c for c in s if not unicodedata.combining(c)).casefold()
    return [w for w in re.sub(r"[^0-9a-z]+", " ", s).split() if w not in STOP]


def letter_consistent(code, entity):
    c, w = code.casefold(), words(entity)
    if not w: return False
    if "".join(x[0] for x in w[:len(c)]) == c: return True
    return any(x.startswith(c[:3]) for x in w)


gold = {g["id"]: g for g in csv.DictReader(open(sys.argv[1], encoding="utf-8"))}
tab = collections.defaultdict(lambda: [0, 0])
for r in csv.DictReader(open(sys.argv[2], encoding="utf-8")):
    if r["cond"] not in ("C2", "C3") or r["category"] not in ("CORRECT", "OTHER_WRONG"): continue
    try: ents = [x.get("entity", "") for x in json.loads(r["content"])["readings"]]
    except Exception: continue
    if not ents: continue
    code = gold[r["item"]]["literal"]
    k = (r["model"].split("/")[1].split(":")[0], r["category"])
    tab[k][0] += letter_consistent(code, ents[0]); tab[k][1] += 1
for k, (a, n) in sorted(tab.items()): print(f"{k[0]:<24} {k[1]:<12} letter-consistent {a}/{n} = {a/n:.2f}")
