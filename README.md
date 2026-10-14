# poc-nsi

Record of a closed exploratory study. The study asked whether language models resolve a short code less accurately when the same string belongs to several identifier systems, using seven systems of the [3char](https://huggingface.co/datasets/brennercruvinel/3char) dataset. It found no robust evidence of such an effect. Choosing the competing reading was rare, and the general error penalty for shared codes changed sign across models, familiarity cuts and scoring rules. A post hoc audit rescored every response with a stricter evaluator and reached the same conclusion. The sample cannot exclude effects of about 10 points, so the result is inconclusive rather than evidence that no effect exists. The decision to close this line of work, and its grounds, are in `docs/DECISION.md`. The 3char dataset is not affected.

`docs/SUMMARY.md` is the English summary. The protocol, reports and audit documents are in Portuguese and form the primary record. `docs/CORRECTIONS.md` lists corrections to those frozen documents.

## Contents

| Path | Contents | State |
| --- | --- | --- |
| `docs/PROTOCOL.md` | Question, design and decision criteria, committed before sampling; deviations listed | Frozen |
| `docs/ORIGINALITY.md` | Prior work read in full and its overlap with this design | Frozen |
| `data/gold.csv`, `data/gold.sha256` | 67 colliding readings, 53 paired controls, aliases and popularity, frozen before the first model call | Frozen |
| `runs/` | The planned calls (`calls.jsonl`) and, for each of three models, the raw responses to its 1,692 calls, including retries, with run logs | Raw |
| `src/poc/`, `results/`, `results_v2/` | The study scripts, the pre-registered scorer and its one adjudicated correction | Original |
| `docs/REPORT.md` | The report written on the v2 scores | Original |
| `docs/AUDIT_PROTOCOL.md`, `src/audit/`, `tests/` | Post hoc evaluator in three dimensions (entity, namespace, behaviour), frozen before rescoring | Audit |
| `audit/` | Integrity manifest, inventories, sealed review sample, blind labels and agreement | Audit |
| `results_v3/` | Every response rescored, with metrics and the transitions from v1 and v2, each with the rule responsible | Audit |
| `docs/AUDIT_REPORT.md`, `docs/DECISION.md` | Findings by level of evidence, and the decision | Audit |
| `docs/SUMMARY.md`, `docs/CORRECTIONS.md` | English summary and corrections to the frozen documents | Current |

## Main results

- Three models (Qwen3 8B, Gemma 3 12B, Llama 3.1 8B), one provider, temperature 0 and JSON-schema output; 5,076 responses, all kept.
- When a model recognized the requested reading, it chose the competing reading in 3 of 666 responses (0.5%). In 24 further responses, 18 of them from Gemma, it built a wrong entity around the competitor's name; these span 7 literals.
- The general error penalty of a colliding code against its paired control changes sign or disappears across familiarity cuts, conditions and scoring rules. The 95% intervals are 18 to 71 points wide.
- The pre-registered scorer matched names by token subsets. In Llama under the named-namespace condition, the penalty fell from +22.2 points under that scorer to +7.9 under the corrected scorers.
- The audit evaluator agreed with a blind, LLM-assisted review of 144 sealed responses on 92.4% of categories after one correction round (83.3% before), and on 100% of namespaces where both found the entity.

## Reproducing

Running the probe again requires an `HF_TOKEN` with Inference Providers access, and the scripts in `src/poc/` take the path of a local copy of the 3char dataset as an argument. The published `runs/` make a new run unnecessary. The audit needs no network access:

```bash
uv run --no-project python -I -m unittest discover -s tests
uv run --no-project python -I src/audit/score_v3.py data/gold.csv runs/calls.jsonl data/namespace_canon.json results_v3 \
    runs/qwen3-8b.jsonl runs/gemma-3-12b.jsonl runs/llama-3.1-8b.jsonl
uv run --no-project python -I src/audit/analyze_v3.py data/gold.csv results_v3
uv run --no-project python -I src/audit/transitions_v3.py data/gold.csv results results_v2 results_v3
```

These commands rewrite `results_v3/` with byte-identical files. `data/pageviews_cache.json` caches the Wikipedia pageview responses of 2026-10-14, so the item selection can be reproduced offline.

The code is released under the MIT license. The model outputs in `runs/` were produced by third-party models and are provided as collected.
