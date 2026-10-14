"""Seeded pre-sample per stratum, Wikidata article lookup and Wikipedia pageviews.

usage: python popularity.py <3char_root> <data_dir>
"""
import collections
import csv
import json
import os
import random
import sys
import time
import urllib.parse

import pyarrow.parquet as pq
import requests

SEED = 20261014
PRE_PER_STRATUM = 60
PRE_CONTROLS = 150
UA = {"User-Agent": "3char-poc/0.1 (https://huggingface.co/datasets/brennercruvinel/3char) python-requests"}
PROP = {"trp/iata": "P238", "trp/ica2": "P230", "lng/i31": "P298", "lng/ioc": "P984",
        "fin/i42": "P498", "fin/tck": "P5531"}
DNS_ARTICLES = {"A": "IPv4 address", "AAAA": "IPv6 address", "CNAME": "CNAME record", "MX": "MX record",
                "NS": "Name server", "PTR": "Reverse DNS lookup", "SOA": "SOA record", "TXT": "TXT record",
                "SRV": "SRV record", "CAA": "DNS Certification Authority Authorization",
                "DS": "Domain Name System Security Extensions", "TLSA": "DNS-based Authentication of Named Entities",
                "SPF": "Sender Policy Framework", "LOC": "LOC record", "DNAME": "DNAME record",
                "NAPTR": "NAPTR record", "HINFO": "HINFO record", "SSHFP": "SSHFP record"}


def stratum(systems):
    if systems & {"lng/i31", "lng/ioc"}: return "S1_country"
    if "fin/i42" in systems: return "S2_currency"
    if "cmp/dns" in systems: return "S5_dns"
    if {"fin/tck", "trp/iata"} <= systems: return "S3_ticker_airport"
    if {"trp/iata", "trp/ica2"} <= systems: return "S4_airport_airline"
    return "other"


def key_of(root):
    """Wikidata lookup key per (system, code): the code itself, or the zero-padded CIK for tickers."""
    rows = pq.read_table(f"{root}/data/fin/tck.parquet", columns=["code", "extra"]).to_pylist()
    return {r["code"]: f'{json.loads(r["extra"])["cik"]:010d}' for r in rows}


def sparql(prop, values):
    out = {}
    for i in range(0, len(values), 150):
        vals = " ".join(json.dumps(v) for v in values[i:i + 150])
        q = f"""SELECT ?v ?item ?title ?label (GROUP_CONCAT(DISTINCT ?alt; separator="|") AS ?alts) WHERE {{
          VALUES ?v {{ {vals} }} ?item wdt:{prop} ?v .
          OPTIONAL {{ ?art schema:about ?item; schema:isPartOf <https://en.wikipedia.org/>; schema:name ?title }}
          OPTIONAL {{ ?item rdfs:label ?label FILTER(lang(?label)="en") }}
          OPTIONAL {{ ?item skos:altLabel ?alt FILTER(lang(?alt)="en") }} }} GROUP BY ?v ?item ?title ?label"""
        for attempt in range(4):
            r = requests.get("https://query.wikidata.org/sparql", params={"query": q, "format": "json"}, headers=UA, timeout=120)
            if r.status_code == 200: break
            time.sleep(5 * (attempt + 1))
        r.raise_for_status()
        for b in r.json()["results"]["bindings"]:
            out.setdefault(b["v"]["value"], []).append({k: b[k]["value"] for k in ("item", "title", "label", "alts") if k in b})
        time.sleep(1)
    return out


def pageviews(title, cache):
    if title in cache: return cache[title]
    t = urllib.parse.quote(title.replace(" ", "_"), safe="")
    u = f"https://wikimedia.org/api/rest_v1/metrics/pageviews/per-article/en.wikipedia/all-access/user/{t}/monthly/2025090100/2026083100"
    for attempt in range(8):
        r = requests.get(u, headers=UA, timeout=60)
        if r.status_code == 200:
            cache[title] = sum(i["views"] for i in r.json()["items"]); return cache[title]
        if r.status_code == 404:
            cache[title] = 0; return 0
        time.sleep(int(r.headers.get("retry-after", 5 * (attempt + 1))) + 1)
    return None


def main(root, data):
    rng = random.Random(SEED)
    coll = list(csv.DictReader(open(f"{data}/collisions.csv", encoding="utf-8")))
    ctrl = list(csv.DictReader(open(f"{data}/controls_pool.csv", encoding="utf-8")))
    by_lit = collections.defaultdict(list)
    for r in coll: by_lit[r["literal"]].append(r)
    strata = collections.defaultdict(list)
    for lit, rs in sorted(by_lit.items()): strata[stratum({r["system_id"] for r in rs})].append(lit)
    pre = []
    for s in sorted(strata):
        if s == "other": continue
        lits = strata[s][:]; rng.shuffle(lits)
        for lit in lits[:PRE_PER_STRATUM]:
            for r in by_lit[lit]: pre.append({**r, "role": "collision", "stratum": s})
    lengths = {len(r["literal"]) for r in pre}
    by_sys = collections.defaultdict(list)
    for r in ctrl:
        if len(r["literal"]) in lengths and r["system_id"] in PROP | {"cmp/dns": None}: by_sys[r["system_id"]].append(r)
    for sid in sorted(by_sys):
        pool = by_sys[sid][:]; rng.shuffle(pool)
        for r in pool[:PRE_CONTROLS]: pre.append({**r, "role": "control", "stratum": ""})
    cik = key_of(root)
    for sid, prop in PROP.items():
        items = [r for r in pre if r["system_id"] == sid]
        keys = sorted({cik.get(r["literal"], r["literal"]) if sid == "fin/tck" else r["literal"] for r in items})
        found = sparql(prop, keys)
        for r in items:
            k = cik.get(r["literal"], r["literal"]) if sid == "fin/tck" else r["literal"]
            hits = found.get(k, [])
            r["wd_n"] = len({h["item"] for h in hits})
            h = hits[0] if len({h["item"] for h in hits}) == 1 else {}
            r["wd_item"] = h.get("item", "").rsplit("/", 1)[-1]
            r["wp_title"] = h.get("title", "")
            r["wd_label"] = h.get("label", "")
            r["wd_alts"] = h.get("alts", "")
        print(f"{sid}: {len(items)} rows, {sum(1 for r in items if r['wp_title'])} with a unique article")
    for r in pre:
        if r["system_id"] == "cmp/dns":
            r.update(wd_n=0, wd_item="", wd_label="", wd_alts="", wp_title=DNS_ARTICLES.get(r["literal"], ""))
    titles = sorted({r["wp_title"] for r in pre if r["wp_title"]})
    cache_p = f"{data}/pageviews_cache.json"
    pv = json.load(open(cache_p)) if os.path.exists(cache_p) else {}
    for i, t in enumerate(titles):
        pageviews(t, pv)
        time.sleep(0.2)
        if i % 50 == 0:
            json.dump(pv, open(cache_p, "w")); print(f"pageviews {i}/{len(titles)}", flush=True)
    json.dump(pv, open(cache_p, "w"))
    for r in pre: r["pageviews"] = pv.get(r["wp_title"], "") if r["wp_title"] else ""
    cols = ["role", "stratum", "literal", "system_id", "label", "eligible_readings", "systems_in_3char", "other_systems",
            "wd_n", "wd_item", "wd_label", "wd_alts", "wp_title", "pageviews"]
    with open(f"{data}/presample.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=cols, extrasaction="ignore"); w.writeheader(); w.writerows(pre)
    print("strata sizes:", {s: len(v) for s, v in strata.items()})
    print("presample rows:", len(pre))


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
