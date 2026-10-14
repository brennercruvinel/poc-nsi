"""Agreement between the automatic v3 scoring and the blind LLM-assisted review of the sealed sample.

usage: python review_agreement.py <audit_dir> <results_v3_dir>
Compares, per sampled response: derived category, entity (response level), namespace (collapsed to OK / INCORRECT /
UNRESOLVED / NA) and behaviour. Writes review_agreement.md and review_disagreements.csv.
"""
import collections
import csv
import sys

NS_OK = {"CORRECT", "EQUIVALENT", "OK"}


def collapse_ns(v):
    return "OK" if v in NS_OK else (v or "NA")


def auto_entity(row):
    if row["category"] in ("FORMAT", "UNKNOWN", "AMBIG_FLAG", "AMBIG_DECLARED", "PARTIAL"): return "NA" if row["category"] in ("FORMAT", "UNKNOWN") else (
        "CORRECT" if row["has_correct"] == "True" else "OTHER")
    if row["category"] in ("CORRECT", "MIXED", "SINGLE", "SINGLE_CORRECT", "MULTI"): return "CORRECT"
    if row["category"] == "COMPETING": return "COMPETITOR"
    if row["category"] == "UNRESOLVED": return "UNRESOLVED"
    return "OTHER"


def main(audit, v3):
    labels = list(csv.DictReader(open(f"{audit}/review_labels.csv", encoding="utf-8")))
    auto = {(r["model"], r["call_id"]): r for r in csv.DictReader(open(f"{v3}/scored.csv", encoding="utf-8"))}
    strata = {(r["model"], r["call_id"]): r["group"] for r in csv.DictReader(open(f"{audit}/review_sample_strata.csv", encoding="utf-8"))}
    cm = collections.Counter(); dims = collections.defaultdict(lambda: [0, 0]); dis = []; by_group = collections.defaultdict(lambda: [0, 0])
    for l in labels:
        a = auto[(l["model"], l["call_id"])]
        pairs = {"category": (l["category"], a["category"]), "entity": (l["entity"], auto_entity(a)),
                 "namespace": (collapse_ns(l["namespace"]), collapse_ns(a["ns_of_correct"]) if a["has_correct"] == "True" else "NA"),
                 "behaviour": (l["behaviour"], a["behaviour"])}
        cm[pairs["category"]] += 1
        for k, (x, y) in pairs.items():
            if k == "namespace" and not (l["entity"] == "CORRECT" and a["has_correct"] == "True"): continue  # only where both found the entity
            dims[k][1] += 1; dims[k][0] += x == y
        g = strata[(l["model"], l["call_id"])]; by_group[g][1] += 1; by_group[g][0] += pairs["category"][0] == pairs["category"][1]
        if pairs["category"][0] != pairs["category"][1] or pairs["entity"][0] != pairs["entity"][1]:
            dis.append({"call_id": l["call_id"], "model": l["model"].split("/")[1].split(":")[0], "group": g, "review_category": l["category"],
                        "auto_category": a["category"], "review_entity": l["entity"], "auto_entity": auto_entity(a), "review_ns": l["namespace"],
                        "auto_ns": a["ns_of_correct"], "confidence": l["confidence"], "justification": l["justification"], "content": a["content"][:160]})
    with open(f"{audit}/review_disagreements.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(dis[0]) if dis else ["call_id"]); w.writeheader(); w.writerows(dis)
    cats = sorted({c for p in cm for c in p})
    with open(f"{audit}/review_agreement.md", "w", encoding="utf-8") as fh:
        fh.write("# Concordância entre a v3 automática e a revisão cega assistida\n\n")
        fh.write("A revisão foi feita por LLM, às cegas para a categoria automática, com justificativa e confiança por item. Não é validação humana independente. "
                 f"Amostra: {len(labels)} respostas, sorteadas com semente fixa e seladas por hash antes da revisão (`audit/review_sample.sha256`).\n\n")
        fh.write("## Concordância por dimensão\n\n| dimensão | iguais | n | taxa |\n|---|---:|---:|---:|\n")
        for k, (ok, n) in dims.items(): fh.write(f"| {k} | {ok} | {n} | {ok / n:.1%} |\n")
        fh.write("\nO namespace é comparado só nas respostas em que revisão e v3 encontraram a entidade correta, na escala OK (CORRECT ou EQUIVALENT), INCORRECT, UNRESOLVED.\n")
        fh.write("\n## Concordância da categoria por estrato\n\n| estrato | iguais | n | taxa |\n|---|---:|---:|---:|\n")
        for g, (ok, n) in sorted(by_group.items()): fh.write(f"| {g} | {ok} | {n} | {ok / n:.1%} |\n")
        fh.write("\n## Matriz de confusão da categoria (linhas: revisão; colunas: v3)\n\n| revisão \\ v3 | " + " | ".join(cats) + " |\n|---|" + "---|" * len(cats) + "\n")
        for r in cats: fh.write(f"| {r} | " + " | ".join(str(cm[(r, c)]) if cm[(r, c)] else "" for c in cats) + " |\n")
        fh.write("\n## Principais desacordos\n\n")
        kinds = collections.Counter((d["review_category"], d["auto_category"]) for d in dis)
        for (r, a), n in kinds.most_common(): fh.write(f"- revisão {r} contra v3 {a}: {n}\n")
        fh.write(f"\nLista completa com justificativas em `audit/review_disagreements.csv` ({len(dis)} itens).\n")
    print({k: f"{ok}/{n}" for k, (ok, n) in dims.items()}); print(kinds.most_common())


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
