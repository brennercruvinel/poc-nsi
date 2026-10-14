"""Apply the manual review to gold_draft.csv and write gold.csv. Every decision is listed here.

usage: python finalize_gold.py <data_dir>
"""
import csv
import json
import sys

# Wikidata resolved the code to a different organisation than the 3char record: unsafe identity, excluded.
EXCLUDE = {"RKT|trp/ica2": "Wikidata article Rayani Air, 3char label Rotormotion",
           "PWA|trp/ica2": "Wikidata article Pacific Western Airlines, 3char label Priester Aviation",
           "CLA|trp/ica2": "Wikidata article Color Air, 3char label Comlux Aviation",
           "SRV|trp/ica2": "Wikidata article Serve Air Cargo, 3char label Aero Servicio Corporativo",
           "WDL|trp/ica2": "control; Wikidata article German Regional Airlines, identity with WDL Aviation not confirmed"}
# DNS labels are IANA descriptions, not names; accepted names added by hand.
DNS_ALIASES = {"A|cmp/dns": ["A record", "address record", "IPv4 address record", "host address record"],
               "TXT|cmp/dns": ["TXT record", "text record", "text strings record"]}


def main(data):
    rows = list(csv.DictReader(open(f"{data}/gold_draft.csv", encoding="utf-8")))
    out = [r for r in rows if r["id"] not in EXCLUDE and r["match_of"] not in EXCLUDE]
    while True:
        n = {}
        for r in out:
            if r["role"] == "collision": n[r["literal"]] = n.get(r["literal"], 0) + 1
        drop = {l for l, k in n.items() if k < 2}
        if not drop: break
        ids = {r["id"] for r in out if r["role"] == "collision" and r["literal"] in drop}
        out = [r for r in out if r["id"] not in ids and r["match_of"] not in ids]
    for r in out:
        if r["id"] in DNS_ALIASES:
            r["aliases"] = json.dumps(sorted(set(json.loads(r["aliases"]) + DNS_ALIASES[r["id"]])))
    with open(f"{data}/gold.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(out[0])); w.writeheader(); w.writerows(out)
    lits = {r["literal"] for r in out if r["role"] == "collision"}
    print(f"literals {len(lits)}, collision readings {sum(r['role'] == 'collision' for r in out)}, "
          f"controls {sum(r['role'] == 'control' for r in out)}")
    by = {}
    for r in out:
        if r["role"] == "collision": by.setdefault(r["stratum"], set()).add(r["literal"])
    print({k: len(v) for k, v in sorted(by.items())})


if __name__ == "__main__":
    main(sys.argv[1])
