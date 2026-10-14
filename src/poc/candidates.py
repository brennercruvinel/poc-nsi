"""Extract same-literal collisions across eligible namespaces of 3char, and non-colliding controls.

usage: python candidates.py <3char_root> <out_dir>
"""
import collections
import csv
import glob
import json
import sys

import pyarrow.parquet as pq

ELIGIBLE = {
    "trp/iata": "IATA airport code",
    "trp/ica2": "ICAO airline designator",
    "lng/i31": "ISO 3166-1 alpha-3 country code",
    "lng/ioc": "IOC country code",
    "fin/i42": "ISO 4217 currency code",
    "fin/tck": "US stock ticker symbol (SEC)",
    "cmp/dns": "DNS resource record type",
}


def load(root, sid):
    rows = pq.read_table(f"{root}/data/{sid}.parquet").to_pylist()
    return [r for r in rows if r["code"] and r["label"] and r["code"].isascii()]


def same_entity(a, b):
    """i31 and ioc readings of one literal are the same country when the IOC row's iso3 equals the ISO code."""
    pair = {a["system_id"], b["system_id"]}
    if pair == {"lng/i31", "lng/ioc"}:
        ioc = a if a["system_id"] == "lng/ioc" else b
        iso = b if ioc is a else a
        return json.loads(ioc["extra"] or "{}").get("iso3") == iso["code"]
    return a["label"].casefold().strip() == b["label"].casefold().strip()


def main(root, out):
    every = collections.defaultdict(set)
    for f in glob.glob(f"{root}/data/*/*.parquet"):
        for r in pq.read_table(f, columns=["system_id", "code"]).to_pylist():
            every[r["code"].casefold()].add(r["system_id"])
    by_lit = collections.defaultdict(list)
    for sid in ELIGIBLE:
        for r in load(root, sid):
            by_lit[r["code"]].append(r)
    coll, ctrl = [], []
    for lit, rs in by_lit.items():
        systems = {r["system_id"] for r in rs}
        if len(rs) != len(systems):
            continue  # code repeated inside one namespace: not a usable key
        if len(systems) >= 2:
            distinct = [r for r in rs if not any(same_entity(r, o) for o in rs if o is not r)]
            if len({r["system_id"] for r in distinct}) >= 2:
                for r in distinct:
                    others = sorted(every[lit.casefold()] - {d["system_id"] for d in distinct})
                    coll.append((lit, r["system_id"], r["label"], len(distinct), len(every[lit.casefold()]), ";".join(others)))
            continue
        # control: one entity across eligible namespaces; other 3char systems may hold the literal, recorded
        anchor = rs[0]
        if all(same_entity(anchor, o) for o in rs[1:]):
            for r in rs:
                others = sorted(every[lit.casefold()] - systems)
                ctrl.append((lit, r["system_id"], r["label"], 1, len(every[lit.casefold()]), ";".join(others)))
    hdr = ["literal", "system_id", "label", "eligible_readings", "systems_in_3char", "other_systems"]
    for name, rows in (("collisions.csv", coll), ("controls_pool.csv", ctrl)):
        with open(f"{out}/{name}", "w", newline="", encoding="utf-8") as fh:
            w = csv.writer(fh); w.writerow(hdr); w.writerows(sorted(rows))
    lits = {c[0] for c in coll}
    pairs = collections.Counter(tuple(sorted({c[1] for c in coll if c[0] == l})) for l in lits)
    print("colliding literals:", len(lits), "| reading rows:", len(coll), "| control pool rows:", len(ctrl))
    print("control pool by system:", dict(collections.Counter(c[1] for c in ctrl)))
    for p, n in pairs.most_common(20):
        print(f"  {n:>5}  {' + '.join(p)}")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
