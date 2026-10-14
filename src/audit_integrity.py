"""Integrity manifest for the frozen POC data. Reads only; writes audit/integrity.json.

usage: python audit_integrity.py <repo_root>
Definitive response per call_id: the last record with http == 200; if none, the last record.
"""
import collections
import hashlib
import json
import os
import subprocess
import sys
import tempfile

MODELS = {"qwen3-8b": "Qwen/Qwen3-8B:featherless-ai", "gemma-3-12b": "google/gemma-3-12b-it:featherless-ai",
          "llama-3.1-8b": "meta-llama/Llama-3.1-8B-Instruct:featherless-ai"}


def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def definitive(records):
    """Apply the rule above and return {call_id: record} plus bookkeeping."""
    by = collections.defaultdict(list)
    for r in records: by[r["call_id"]].append(r)
    out, multi = {}, {}
    for cid, rs in by.items():
        ok = [r for r in rs if r.get("http") == 200]
        out[cid] = ok[-1] if ok else rs[-1]
        if len(rs) > 1:
            multi[cid] = [{"http": r.get("http"), "finish": r.get("finish"), "chosen": r is out[cid]} for r in rs]
    return out, multi


def run_model(root, name, calls, planned_ids):
    p = f"{root}/runs/{name}.jsonl"
    recs = [json.loads(l) for l in open(p, encoding="utf-8")]
    chosen, multi = definitive(recs)
    bad_prompt = [r["call_id"] for r in recs if r.get("sent") != calls[r["call_id"]]["prompt"] + (" /no_think" if "Qwen3" in r["model"] else "")]
    models = collections.Counter(r.get("model") for r in recs)
    resp_models = collections.Counter(r.get("resp_model") for r in recs)
    ts = sorted(r["ts"] for r in recs)
    redo = {cid: rs for cid, rs in multi.items() if any(x["http"] == 200 for x in rs[:-1])}
    recovered = {cid: rs for cid, rs in multi.items() if all(x["http"] != 200 for x in rs[:-1])}
    return {"file": f"runs/{name}.jsonl", "sha256": sha(p), "model": dict(models), "resp_model": dict(resp_models),
            "records": len(recs), "distinct_call_ids": len(chosen), "planned": len(planned_ids),
            "missing": sorted(planned_ids - set(chosen)), "extra": sorted(set(chosen) - planned_ids),
            "records_http_not_200": sum(r.get("http") != 200 for r in recs),
            "definitive_http_not_200": sum(r.get("http") != 200 for r in chosen.values()),
            "definitive_content_none": sum(r.get("content") is None for r in chosen.values()),
            "records_finish_length": sum(r.get("finish") == "length" for r in recs),
            "definitive_finish_length": sum(r.get("finish") == "length" for r in chosen.values()),
            "definitive_finish_length_by_cond": dict(collections.Counter(cid.split("|")[0] for cid, r in chosen.items() if r.get("finish") == "length")),
            "call_ids_with_multiple_records": len(multi),
            "redo_truncated": len(redo), "redo_still_truncated": sum(chosen[c].get("finish") == "length" for c in redo),
            "recovered_after_failure": len(recovered), "recovered_ids": sorted(recovered),
            "sent_differs_from_planned": bad_prompt, "ts_first": ts[0], "ts_last": ts[-1],
            "scorer_rule_equivalent": all(chosen[c] is r for c, r in score_rule(recs).items())}


def score_rule(res):
    """The rule used in src/score.py (v1 and v2), copied verbatim."""
    ok = {x["call_id"] for x in res if x.get("http") == 200}
    return {r["call_id"]: r for r in res if r.get("http") == 200 or r["call_id"] not in ok}


def reproduce(root):
    """Re-run score.py for v1 and v2 into a temp dir and compare file hashes with the committed outputs."""
    out = {}
    runs = [f"{root}/runs/{n}.jsonl" for n in MODELS]
    for tag, env in (("results", {}), ("results_v2", {"SCORER": "v2"})):
        with tempfile.TemporaryDirectory() as tmp:
            subprocess.run([sys.executable, "-I", f"{root}/src/score.py", f"{root}/data/gold.csv", f"{root}/runs/calls.jsonl", tmp, *runs],
                           env={**os.environ, **env}, check=True, capture_output=True)
            out[tag] = {f: {"committed": sha(f"{root}/{tag}/{f}"), "rebuilt": sha(f"{tmp}/{f}")} for f in ("scored.csv", "summary.json")}
            for f in out[tag]: out[tag][f]["equal"] = out[tag][f]["committed"] == out[tag][f]["rebuilt"]
    return out


def main(root):
    git = lambda *a: subprocess.run(["git", "-C", root, *a], capture_output=True, text=True, check=True).stdout.strip()
    rep = {"gold": {"sha256": sha(f"{root}/data/gold.csv"), "recorded": open(f"{root}/data/gold.sha256").read().split()[0],
                    "blob_at_6197b9e": hashlib.sha256(subprocess.run(["git", "-C", root, "show", "6197b9e:data/gold.csv"], capture_output=True, check=True).stdout).hexdigest(),
                    "rows": sum(1 for _ in open(f"{root}/data/gold.csv")) - 1}}
    rep["gold"]["consistent"] = len({rep["gold"]["sha256"], rep["gold"]["recorded"], rep["gold"]["blob_at_6197b9e"]}) == 1
    rep["commits"] = [l for l in git("log", "--format=%h %ad %s", "--date=iso", "main").splitlines()]
    rep["files_changed_after_freeze"] = {
        "gold.csv": git("log", "--format=%h", "6197b9e..main", "--", "data/gold.csv").splitlines(),
        "calls.jsonl": git("log", "--format=%h", "6197b9e..main", "--", "runs/calls.jsonl").splitlines(),
        "PROTOCOL.md": git("log", "--format=%h", "02d6bb5..main", "--", "docs/PROTOCOL.md").splitlines(),
        "score.py": git("log", "--format=%h", "6197b9e..main", "--", "src/score.py").splitlines(),
        "runs": git("log", "--format=%h", "3e5cbfd..main", "--", "runs/").splitlines()}
    with tempfile.TemporaryDirectory() as tmp:
        subprocess.run([sys.executable, "-I", f"{root}/src/prompts.py", f"{root}/data/gold.csv", f"{tmp}/calls.jsonl"], check=True, capture_output=True)
        rep["calls"] = {"sha256": sha(f"{root}/runs/calls.jsonl"), "rebuilt_from_gold": sha(f"{tmp}/calls.jsonl")}
    rep["calls"]["equal"] = rep["calls"]["sha256"] == rep["calls"]["rebuilt_from_gold"]
    calls = {c["call_id"]: c for c in map(json.loads, open(f"{root}/runs/calls.jsonl", encoding="utf-8"))}
    rep["calls"]["planned"] = len(calls)
    rep["calls"]["by_cond"] = dict(collections.Counter(c["cond"] for c in calls.values()))
    rep["runs"] = {n: run_model(root, n, calls, set(calls)) for n in MODELS}
    rep["reproduce_scoring"] = reproduce(root)
    rep["working_tree_clean_for_frozen_paths"] = git("status", "--porcelain", "--", "data", "runs", "results", "results_v2", "docs/PROTOCOL.md") == ""
    json.dump(rep, open(f"{root}/audit/integrity.json", "w"), indent=1)
    print(json.dumps({k: v for k, v in rep.items() if k != "runs"}, indent=1))
    for n, r in rep["runs"].items():
        print(n, json.dumps({k: v for k, v in r.items() if k not in ("recovered_ids", "sent_differs_from_planned")}))
        print("  recovered_ids", r["recovered_ids"], "sent_differs", len(r["sent_differs_from_planned"]))


if __name__ == "__main__":
    main(sys.argv[1])
