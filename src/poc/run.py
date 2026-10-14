"""Run calls.jsonl against one model through the Hugging Face router. Resumable; raw output kept.

usage: HF_TOKEN=... python run.py <calls.jsonl> <model:provider> <out.jsonl> [workers]
"""
import concurrent.futures as cf
import datetime as dt
import json
import os
import sys
import threading
import time

import requests

URL = "https://router.huggingface.co/v1/chat/completions"


def one(model, c, token, max_tokens=400):
    text = c["prompt"] + (" /no_think" if "Qwen3" in model else "")
    body = {"model": model, "messages": [{"role": "user", "content": text}], "temperature": 0, "seed": 7,
            "max_tokens": max_tokens, "response_format": {"type": "json_schema", "json_schema": {"name": "out", "schema": c["schema"]}}}
    for attempt in range(6):
        t0 = time.time()
        try:
            r = requests.post(URL, headers={"Authorization": f"Bearer {token}"}, json=body, timeout=120)
        except requests.RequestException as e:
            time.sleep(2 ** attempt); last = {"http": None, "error": str(e)[:200]}; continue
        last = {"http": r.status_code}
        if r.status_code == 200:
            d = r.json()
            return {"call_id": c["call_id"], "model": model, "sent": text, "http": 200, "content": d["choices"][0]["message"]["content"],
                    "finish": d["choices"][0].get("finish_reason"), "usage": d.get("usage"), "resp_model": d.get("model"),
                    "fingerprint": d.get("system_fingerprint"), "latency_s": round(time.time() - t0, 2),
                    "ts": dt.datetime.now(dt.timezone.utc).isoformat()}
        last["error"] = r.text[:300]
        time.sleep(2 ** attempt if r.status_code in (429, 500, 502, 503, 504) else 1)
    return {"call_id": c["call_id"], "model": model, "sent": text, "content": None, **last,
            "ts": dt.datetime.now(dt.timezone.utc).isoformat()}


def redo_truncated(calls_path, model, out, max_tokens=1500):
    """Re-run calls whose last response hit the token limit; the new record is appended and wins in scoring."""
    token = os.environ["HF_TOKEN"]
    calls = {c["call_id"]: c for c in map(json.loads, open(calls_path, encoding="utf-8"))}
    last = {}
    for l in open(out, encoding="utf-8"):
        r = json.loads(l); last[r["call_id"]] = r
    todo = [calls[k] for k, r in last.items() if r.get("finish") == "length"]
    print(f"{model}: {len(todo)} truncated, re-running with max_tokens={max_tokens}", flush=True)
    with open(out, "a", encoding="utf-8") as fh:
        for c in todo:
            fh.write(json.dumps(one(model, c, token, int(max_tokens)), ensure_ascii=False) + "\n"); fh.flush()


def main(calls_path, model, out, workers=6):
    token = os.environ["HF_TOKEN"]
    calls = [json.loads(l) for l in open(calls_path, encoding="utf-8")]
    done = set()
    if os.path.exists(out):
        done = {json.loads(l)["call_id"] for l in open(out, encoding="utf-8") if json.loads(l).get("http") == 200}
    todo = [c for c in calls if c["call_id"] not in done]
    print(f"{model}: {len(done)} done, {len(todo)} to run", flush=True)
    lock = threading.Lock()
    with open(out, "a", encoding="utf-8") as fh, cf.ThreadPoolExecutor(int(workers)) as ex:
        for i, res in enumerate(ex.map(lambda c: one(model, c, token), todo), 1):
            with lock:
                fh.write(json.dumps(res, ensure_ascii=False) + "\n"); fh.flush()
            if i % 200 == 0: print(f"  {i}/{len(todo)}", flush=True)
    print("finished", model, flush=True)


if __name__ == "__main__":
    if sys.argv[1] == "--redo-truncated":
        redo_truncated(*sys.argv[2:])
    else:
        main(*sys.argv[1:])
