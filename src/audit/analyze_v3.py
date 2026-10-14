"""Metrics E1 to E4 on the v3 scoring, with familiarity cuts, scoring-rule sensitivities and paraphrase sensitivity.

usage: python analyze_v3.py <gold.csv> <results_v3_dir>
Writes summary.json and metrics.md in the results directory. Bootstrap by literal, 10,000 resamples, seed 20261014.
"""
import collections
import csv
import json
import random
import sys

SEED, B = 20261014, 10000
NS_OK = {"CORRECT", "EQUIVALENT"}
RULES = {"primary": lambda r: r["category"] == "CORRECT",
         "strict_ns": lambda r: r["category"] == "CORRECT" and r["ns_of_correct"] in NS_OK,
         "lenient": lambda r: r["has_correct"] == "True",
         "unresolved_as_correct": lambda r: r["category"] in ("CORRECT", "UNRESOLVED")}


def mean(x): return sum(x) / len(x) if x else float("nan")


def boot(clusters, rng=None):
    rng = random.Random(SEED)  # fresh generator per estimate, so every interval is reproducible on its own
    keys = list(clusters); est = mean([v for k in keys for v in clusters[k]])
    sims = sorted(mean([v for k in (rng.choice(keys) for _ in keys) for v in clusters[k]]) for _ in range(B))
    return {"est": est, "lo": sims[int(0.025 * B)], "hi": sims[int(0.975 * B) - 1]}


def load(gold_p, res_dir):
    gold = {g["id"]: g for g in csv.DictReader(open(gold_p, encoding="utf-8"))}
    rows = collections.defaultdict(dict)
    for r in csv.DictReader(open(f"{res_dir}/scored.csv", encoding="utf-8")): rows[r["model"]][r["call_id"]] = r
    lean = collections.defaultdict(set)  # (model, call_id) whose UNRESOLVED evidence points at a competitor
    for r in csv.DictReader(open(f"{res_dir}/readings.csv", encoding="utf-8")):
        if "competitor" in r["evidence"] or r["evidence"] == "both": lean[r["model"]].add(r["call_id"])
    return gold, rows, lean


def familiarity(gold, cat):
    p1 = {i: cat.get(f"P1|{i}|0", {}).get("category") == "PASS" for i in gold}
    p1s = {i: p1[i] and cat.get(f"P1|{i}|0", {}).get("detail") == "answer" for i in gold}
    p2 = {i: cat.get(f"P2T|{i}|0", {}).get("category") == "yes" and cat.get(f"P2F|{i}|0", {}).get("category") == "no" for i in gold}
    return {"P2": p2, "P1": p1, "P1andP2": {i: p1[i] and p2[i] for i in gold}, "P1strict": p1s}


def err(cat, item, cond, rule, drop_format=False):
    rs = [cat[f"{cond}|{item}|{v}"] for v in range(3)]
    if drop_format: rs = [r for r in rs if r["category"] != "FORMAT"]
    return 1 - mean([RULES[rule](r) for r in rs]) if rs else float("nan")


def e1(gold, cat, known, cond, rule, rng, drop_format=False):
    pairs = collections.defaultdict(list)
    for i, g in gold.items():
        if g["role"] == "control" and known[i] and known.get(g["match_of"]):
            d = err(cat, g["match_of"], cond, rule, drop_format) - err(cat, i, cond, rule, drop_format)
            if d == d: pairs[gold[g["match_of"]]["literal"]].append(d)
    if not pairs: return None
    return boot(pairs, rng) | {"pairs": sum(map(len, pairs.values())), "literals": len(pairs)}


def analyse_model(gold, cat, lean, rng):
    fam = familiarity(gold, cat); S = {"n": len(cat)}
    S["familiarity"] = {k: {"readings_known": sum(v.values()), "collision_known": sum(v[i] for i in v if gold[i]["role"] == "collision"),
                            "control_known": sum(v[i] for i in v if gold[i]["role"] == "control")} for k, v in fam.items()}
    S["familiarity"]["P1_P2_table"] = dict(collections.Counter(f"P1={fam['P1'][i]},P2={fam['P2'][i]}" for i in gold))
    S["familiarity"]["P1_status"] = dict(collections.Counter(r["detail"] for r in cat.values() if r["cond"] == "P1"))
    S["format"] = dict(collections.Counter(r["cond"] for r in cat.values() if r["category"] == "FORMAT"))
    S["behaviour"] = {c: dict(collections.Counter(r["behaviour"] for r in cat.values() if r["cond"] == c)) for c in ("C1", "C2", "C3", "C4")}
    for cond in ("C2", "C3", "C4"):
        C = S[cond] = {}
        C["E1"] = {cut: {rule: e1(gold, cat, fam[cut], cond, rule, rng) for rule in RULES} for cut in fam}
        C["E1_P2_without_format"] = e1(gold, cat, fam["P2"], cond, "primary", rng, drop_format=True)
        for cut in ("P2", "P1andP2"):
            kc = [i for i, g in gold.items() if g["role"] == "collision" and fam[cut][i]]
            uc = [i for i, g in gold.items() if g["role"] == "collision" and not fam[cut][i]]
            kk = [i for i, g in gold.items() if g["role"] == "control" and fam[cut][i]]
            for name, ids in (("known_collision", kc), ("unknown_collision", uc), ("known_control", kk)):
                rs = [cat[f"{cond}|{i}|{v}"] for i in ids for v in range(3)]
                C[f"{cut}_{name}_categories"] = dict(collections.Counter(r["category"] for r in rs))
                C[f"{cut}_{name}_n_readings"] = len(ids)
                C[f"{cut}_{name}_err"] = {rule: 1 - mean([RULES[rule](r) for r in rs]) if rs else None for rule in RULES}
                C[f"{cut}_{name}_ns_of_correct"] = dict(collections.Counter(r["ns_of_correct"] for r in rs if r["has_correct"] == "True"))
                C[f"{cut}_{name}_unresolved_competitor_leaning"] = sum(r["category"] == "UNRESOLVED" and r["call_id"] in lean for r in rs)
        kc = [i for i, g in gold.items() if g["role"] == "collision" and fam["P2"][i]]
        kk = [i for i, g in gold.items() if g["role"] == "control" and fam["P2"][i]]
        C["paraphrase_err_P2_known_collision"] = [1 - mean([RULES["primary"](cat[f"{cond}|{i}|{v}"]) for i in kc]) for v in range(3)]
        C["paraphrase_err_P2_known_control"] = [1 - mean([RULES["primary"](cat[f"{cond}|{i}|{v}"]) for i in kk]) for v in range(3)]
        C["paraphrase_E1_P2"] = [mean([err_v(cat, g["match_of"], cond, v) - err_v(cat, i, cond, v) for i, g in gold.items()
                                       if g["role"] == "control" and fam["P2"][i] and fam["P2"].get(g["match_of"])]) for v in range(3)]
    c1 = [r for r in cat.values() if r["cond"] == "C1"]
    S["C1"] = {role: dict(collections.Counter(r["category"] for r in c1 if r["item"].startswith(role))) for role in ("collision", "control")}
    S["C1"]["ambiguous_rate_without_format"] = {role: mean([r["behaviour"] == "AMBIGUOUS" for r in c1 if r["item"].startswith(role) and r["category"] != "FORMAT"]) for role in ("collision", "control")}
    S["C1"]["single_detail"] = dict(collections.Counter(r["detail"] for r in c1 if r["category"] == "SINGLE"))
    S["C1"]["control_ambig_detail"] = dict(collections.Counter(r["detail"] for r in c1 if r["category"] == "AMBIG_DECLARED"))
    by_lit = collections.defaultdict(list)
    for r in c1:
        if r["item"].startswith("collision") and r["category"] != "FORMAT": by_lit[r["item"]].append(r["category"] == "SINGLE")
    S["C1"]["single_rate_collision_without_format"] = boot(by_lit, rng) if by_lit else None
    return S


def err_v(cat, item, cond, v): return 0 if RULES["primary"](cat[f"{cond}|{item}|{v}"]) else 1


def fmt(e): return "n/a" if not e else f"{100 * e['est']:+.1f} [{100 * e['lo']:+.1f}; {100 * e['hi']:+.1f}] ({e['pairs']} pares, {e['literals']} literais)"


def write_md(summary, out):
    with open(out, "w", encoding="utf-8") as fh:
        fh.write("# Métricas v3\n\nGerado por `src/analyze_v3.py` a partir de `results_v3/scored.csv`. E1 em pontos percentuais: erro colidente menos erro controle, por par; intervalo de 95% por bootstrap de literais.\n\n")
        for cond in ("C2", "C3", "C4"):
            fh.write(f"## E1 em {cond}\n\n| modelo | recorte | primário | estrito (namespace) | leniente | UNRESOLVED como acerto |\n|---|---|---|---|---|---|\n")
            for m, S in summary.items():
                for cut in ("P2", "P1", "P1andP2", "P1strict"):
                    E = S[cond]["E1"][cut]; fh.write(f"| {short(m)} | {cut} | {fmt(E['primary'])} | {fmt(E['strict_ns'])} | {fmt(E['lenient'])} | {fmt(E['unresolved_as_correct'])} |\n")
            fh.write("\n")
        fh.write("## Categorias em leituras colidentes conhecidas (P2), por condição\n\n| modelo | cond | n leituras | CORRECT | MIXED | COMPETING | UNRESOLVED (inclinado a concorrente) | OTHER_WRONG | AMBIG_FLAG | UNKNOWN | FORMAT |\n|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|\n")
        for m, S in summary.items():
            for cond in ("C2", "C3", "C4"):
                c = S[cond]["P2_known_collision_categories"]; n = S[cond]["P2_known_collision_n_readings"]
                fh.write(f"| {short(m)} | {cond} | {n} | {c.get('CORRECT', 0)} | {c.get('MIXED', 0)} | {c.get('COMPETING', 0)} | {c.get('UNRESOLVED', 0)} ({S[cond]['P2_known_collision_unresolved_competitor_leaning']}) | {c.get('OTHER_WRONG', 0)} | {c.get('AMBIG_FLAG', 0)} | {c.get('UNKNOWN', 0)} | {c.get('FORMAT', 0)} |\n")
        fh.write("\n## Categorias em leituras colidentes não conhecidas (P2)\n\n| modelo | cond | n | CORRECT | COMPETING | UNRESOLVED (inclinado) | OTHER_WRONG | AMBIG_FLAG | UNKNOWN | FORMAT |\n|---|---|---:|---:|---:|---:|---:|---:|---:|---:|\n")
        for m, S in summary.items():
            for cond in ("C2", "C3"):
                c = S[cond]["P2_unknown_collision_categories"]
                fh.write(f"| {short(m)} | {cond} | {S[cond]['P2_unknown_collision_n_readings']} | {c.get('CORRECT', 0)} | {c.get('COMPETING', 0)} | {c.get('UNRESOLVED', 0)} ({S[cond]['P2_unknown_collision_unresolved_competitor_leaning']}) | {c.get('OTHER_WRONG', 0)} | {c.get('AMBIG_FLAG', 0)} | {c.get('UNKNOWN', 0)} | {c.get('FORMAT', 0)} |\n")
        fh.write("\n## Namespace da leitura correta, colidentes conhecidos (P2)\n\n| modelo | cond | CORRECT | EQUIVALENT | INCORRECT | UNRESOLVED |\n|---|---|---:|---:|---:|---:|\n")
        for m, S in summary.items():
            for cond in ("C2", "C3", "C4"):
                c = S[cond]["P2_known_collision_ns_of_correct"]; fh.write(f"| {short(m)} | {cond} | {c.get('CORRECT', 0)} | {c.get('EQUIVALENT', 0)} | {c.get('INCORRECT', 0)} | {c.get('UNRESOLVED', 0)} |\n")
        fh.write("\n## Paráfrases: erro primário por variante, P2 conhecidas\n\n| modelo | cond | colidente v0/v1/v2 | controle v0/v1/v2 | E1 por variante |\n|---|---|---|---|---|\n")
        for m, S in summary.items():
            for cond in ("C2", "C3"):
                C = S[cond]; fh.write(f"| {short(m)} | {cond} | {'/'.join(f'{100 * x:.0f}' for x in C['paraphrase_err_P2_known_collision'])} | {'/'.join(f'{100 * x:.0f}' for x in C['paraphrase_err_P2_known_control'])} | {'/'.join(f'{100 * x:+.0f}' for x in C['paraphrase_E1_P2'])} |\n")
        fh.write("\n## C1, sem namespace\n\n| modelo | papel | " + " | ".join(C1CATS) + " | ambíguo sem FORMAT |\n|---|---|" + "---:|" * (len(C1CATS) + 1) + "\n")
        for m, S in summary.items():
            for role in ("collision", "control"):
                c = S["C1"][role]; fh.write(f"| {short(m)} | {role} | " + " | ".join(str(c.get(k, 0)) for k in C1CATS) + f" | {100 * S['C1']['ambiguous_rate_without_format'][role]:.0f}% |\n")
        fh.write("\n## Familiaridade e falhas de geração\n\n| modelo | P2 conhecidas (col/ctrl) | P1 conhecidas | P1 ∩ P2 | P1 estrita (status answer) | status em P1 | FORMAT por condição |\n|---|---|---|---|---|---|---|\n")
        for m, S in summary.items():
            f = S["familiarity"]; fh.write(f"| {short(m)} | {f['P2']['readings_known']} ({f['P2']['collision_known']}/{f['P2']['control_known']}) | {f['P1']['readings_known']} | {f['P1andP2']['readings_known']} | {f['P1strict']['readings_known']} | {f['P1_status']} | {S['format']} |\n")


C1CATS = ("MULTI", "PARTIAL", "SINGLE", "SINGLE_CORRECT", "AMBIG_DECLARED", "UNRESOLVED", "WRONG", "UNKNOWN", "FORMAT")


def short(m): return m.split("/")[1].split(":")[0]


def main(gold_p, res_dir):
    gold, rows, lean = load(gold_p, res_dir); summary = {}
    for m in rows: summary[m] = analyse_model(gold, rows[m], lean[m], random.Random(SEED))
    json.dump(summary, open(f"{res_dir}/summary.json", "w"), indent=1)
    write_md(summary, f"{res_dir}/metrics.md")
    for m, S in summary.items():
        print(short(m), {c: fmt(S[c]["E1"]["P2"]["primary"]) for c in ("C2", "C3")}, "| strict:", {c: fmt(S[c]["E1"]["P2"]["strict_ns"]) for c in ("C2", "C3")})


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
