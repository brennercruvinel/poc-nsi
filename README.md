# poc-nsi

record of a closed exploratory study: whether language models resolve a short code worse when the same literal belongs to several identifier systems, built on seven systems of the [3char](https://huggingface.co/datasets/brennercruvinel/3char) dataset. the probe found no robust effect; a post hoc audit of the collected responses rescored everything with a stricter evaluator and confirmed the negative result. the decision to close the line and its grounds are in `docs/DECISION.md`. the dataset is not affected.

`docs/SUMMARY.md` is the english summary. the protocol, reports and audit documents are in portuguese and are the primary record.

## what is here

| path | what it is | state |
| --- | --- | --- |
| `docs/PROTOCOL.md` | question, design, decision criteria; committed before sampling; deviations listed | frozen |
| `docs/ORIGINALITY.md` | prior work read in full and the overlap with this design | frozen |
| `data/gold.csv`, `data/gold.sha256` | 67 colliding readings, 53 paired controls, aliases, popularity; frozen before the first model call | frozen |
| `runs/` | 1,692 calls per model, three models, raw responses and retries, JSONL | raw |
| `results/`, `results_v2/` | the pre-registered scorer and its one adjudicated correction | original |
| `docs/REPORT.md` | the report written on v2 | original |
| `docs/AUDIT_PROTOCOL.md`, `src/audit/`, `tests/` | post hoc evaluator in three dimensions (entity, namespace, behaviour), frozen before rescoring | audit |
| `audit/` | integrity manifest, inventories, sealed review sample and blind labels, agreement | audit |
| `results_v3/` | every response rescored; metrics; transitions from v1 and v2 with the rule responsible | audit |
| `docs/AUDIT_REPORT.md`, `docs/DECISION.md` | findings by level of evidence; the single decision | audit |

## headline numbers

- three models (Qwen3 8B, Gemma 3 12B, Llama 3.1 8B), one provider, temperature 0, JSON schema output; 5,076 responses, all kept.
- confusion with the competing reading in readings the model recognises: 3 of 666 responses (0.5%); 24 more build a wrong entity around the competitor's name, in 4 literals and mostly one model.
- the general error penalty of a colliding literal against its paired control changes sign or vanishes across familiarity cuts, conditions and scoring rules; intervals are 25 to 60 points wide.
- the first scorer matched names by token subsets; half of its effect in one model was that artefact. agreement between the audit evaluator and a blind review of 144 sealed responses: 92.4% on category, 100% on namespace where both found the entity.

## reproduce

the probe needs `HF_TOKEN` with Inference Providers access and a local copy of the dataset next to this folder as `../3char`; the published `runs/` make it unnecessary. the audit needs no network.

```bash
uv run python -I -m unittest discover -s tests
uv run python -I src/audit/score_v3.py data/gold.csv runs/calls.jsonl data/namespace_canon.json results_v3 runs/*.jsonl
uv run python -I src/audit/analyze_v3.py data/gold.csv results_v3
uv run python -I src/audit/transitions_v3.py data/gold.csv results results_v2 results_v3
```

`data/pageviews_cache.json` is the cached Wikipedia pageview response of 2026-10-14 so the item selection reproduces offline.

code is MIT. the model outputs in `runs/` are outputs of third-party models, provided as collected.
