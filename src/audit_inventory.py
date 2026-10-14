"""Inventories that ground the v3 scorer: system strings per namespace, and gold alias hazards.

usage: python audit_inventory.py <repo_root>
Writes audit/system_inventory.md, audit/system_inventory.json and audit/alias_inventory.md. Read only otherwise.
"""
import collections
import csv
import json
import re
import sys
import unicodedata

MODELS = ("qwen3-8b", "gemma-3-12b", "llama-3.1-8b")


def norm(s):
    s = unicodedata.normalize("NFKD", str(s or ""))
    s = "".join(ch for ch in s if not unicodedata.combining(ch)).casefold()
    return " ".join(re.sub(r"[^0-9a-z]+", " ", s).split())


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


def definitive(path):
    out = {}
    for l in open(path, encoding="utf-8"):
        r = json.loads(l)
        if r.get("http") == 200 or r["call_id"] not in out: out[r["call_id"]] = r
    return out


def systems(root, gold, calls):
    """Distinct system strings, grouped by the namespace the question asked for (C1 has none: grouped by literal's namespaces)."""
    by_ns = collections.defaultdict(collections.Counter)
    by_model = collections.defaultdict(collections.Counter)
    for m in MODELS:
        for cid, r in definitive(f"{root}/runs/{m}.jsonl").items():
            c = calls[cid]; d = parse(r.get("content"))
            if c["cond"] not in ("C1", "C2", "C3", "C4") or not d or not isinstance(d.get("readings"), list): continue
            ns = gold[c["item"]]["system_id"] if c["cond"] != "C1" else "C1 (none asked)"
            for rd in d["readings"]:
                if isinstance(rd, dict):
                    s = norm(rd.get("system")); by_ns[ns][s] += 1; by_model[m][s] += 1
    return by_ns, by_model


def aliases(gold):
    rows = []
    for g in gold.values():
        al = json.loads(g["aliases"]); comps = json.loads(g["competitors"])
        mine = {norm(a) for a in al + [g["label"]]}
        short = sorted(a for a in al if len(a.strip()) <= 3)
        same_lit = sorted(a for a in al if norm(a) == norm(g["literal"]))
        shared, contained = [], []
        for c in comps:
            theirs = {norm(a) for a in c["aliases"] + [c["label"]]}
            shared += sorted(f"{x} = {c['system_id']}" for x in mine & theirs if x)
            for x in mine:
                for y in theirs:
                    if x and y and x != y and (f" {x} " in f" {y} " or f" {y} " in f" {x} "):
                        contained.append(f"{x} ~ {y} ({c['system_id']})")
        rows.append({"id": g["id"], "role": g["role"], "label": g["label"], "n_aliases": len(al), "short": short, "equals_literal": same_lit,
                     "shared_with_competitor": shared, "token_contained": sorted(set(contained)),
                     "descriptive": g["system_id"] == "cmp/dns"})
    return rows


def main(root):
    gold = {g["id"]: g for g in csv.DictReader(open(f"{root}/data/gold.csv", encoding="utf-8"))}
    calls = {c["call_id"]: c for c in map(json.loads, open(f"{root}/runs/calls.jsonl", encoding="utf-8"))}
    by_ns, by_model = systems(root, gold, calls)
    json.dump({"by_namespace": {k: dict(v.most_common()) for k, v in by_ns.items()}, "by_model": {k: dict(v.most_common()) for k, v in by_model.items()}},
              open(f"{root}/audit/system_inventory.json", "w"), indent=1, ensure_ascii=False)
    with open(f"{root}/audit/system_inventory.md", "w", encoding="utf-8") as fh:
        fh.write("# Inventário do campo system\n\nStrings normalizadas (casefold, sem acentos e pontuação) do campo `system` em cada leitura das respostas definitivas, "
                 "agrupadas pelo namespace pedido. Gerado por `src/audit_inventory.py`; o JSON completo está em `audit/system_inventory.json`.\n\n")
        for ns in sorted(by_ns):
            cnt = by_ns[ns]
            fh.write(f"## {ns}: {len(cnt)} strings distintas, {sum(cnt.values())} leituras\n\n| n | system |\n|---:|---|\n")
            for s, n in cnt.most_common(): fh.write(f"| {n} | {s} |\n")
            fh.write("\n")
    rows = aliases(gold)
    with open(f"{root}/audit/alias_inventory.md", "w", encoding="utf-8") as fh:
        fh.write("# Inventário de aliases do gabarito\n\nRiscos de casamento por linha do gabarito, após normalização. Gerado por `src/audit_inventory.py`.\n\n")
        fh.write(f"- Linhas: {len(rows)}. Com alias de até 3 caracteres: {sum(bool(r['short']) for r in rows)}. "
                 f"Com alias igual ao literal: {sum(bool(r['equals_literal']) for r in rows)}. "
                 f"Com alias idêntico ao de uma leitura concorrente: {sum(bool(r['shared_with_competitor']) for r in rows)}. "
                 f"Com alias contido em alias concorrente, ou vice-versa: {sum(bool(r['token_contained']) for r in rows)}. "
                 f"Descritivos (DNS): {sum(r['descriptive'] for r in rows)}.\n\n")
        fh.write("| id | papel | label | aliases | curtos | = literal | idêntico ao concorrente | contido no concorrente |\n|---|---|---|---:|---|---|---|---|\n")
        for r in rows:
            fh.write(f"| {r["id"].replace("|", "\\|")} | {r['role']} | {r['label']} | {r['n_aliases']} | {', '.join(r['short'])} | {', '.join(r['equals_literal'])} | "
                     f"{'; '.join(r['shared_with_competitor'])} | {'; '.join(r['token_contained'])} |\n")
    print("namespaces:", {k: len(v) for k, v in by_ns.items()})
    print("alias rows with hazards:", sum(bool(r["shared_with_competitor"] or r["token_contained"]) for r in rows))
    for r in rows:
        if r["shared_with_competitor"] or r["token_contained"]: print(" ", r["id"], r["shared_with_competitor"], r["token_contained"])


if __name__ == "__main__":
    main(sys.argv[1])
