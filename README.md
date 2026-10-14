# POC: Same Code, Different Worlds

Exploratory proof of concept on namespace interference in language models, built only from the published 3char data.
Protocol and decision criteria: docs/PROTOCOL.md, frozen in the first commit before sampling.
Originality review: docs/ORIGINALITY.md.

## Requirements
- uv (https://docs.astral.sh/uv/), which installs Python dependencies per command.
- A Hugging Face token with Inference Providers access, exported as HF_TOKEN.
- A local copy of the 3char dataset; the commands below assume it sits next to this folder as ../3char.

## Reproduce
```
uv run --with 'pyarrow>=16' python -I src/candidates.py ../3char data
uv run --with 'pyarrow>=16' --with requests python -I src/popularity.py ../3char data
uv run --with 'pyarrow>=16' python -I src/select_items.py ../3char data
# manual review of data/gold_draft.csv, saved as data/gold.csv, then: sha256sum data/gold.csv
uv run python -I src/prompts.py data/gold.csv runs/calls.jsonl
uv run --with requests python -I src/run.py runs/calls.jsonl <model:provider> runs/<name>.jsonl 6
uv run python -I src/score.py data/gold.csv runs/calls.jsonl results runs/*.jsonl
```

## Layout -
- src: one script per step.
- data: candidates, pre-sample with popularity, gold file.
- runs: every model call with its raw response, in JSONL.
- results: scored responses and the summary.

## Audit v3 (post hoc, branch audit-v3)
Closed-scope audit of the collected data with a three-dimension evaluator (entity, namespace, behaviour). Contract and rules: docs/AUDIT_PROTOCOL.md. Report: docs/AUDIT_REPORT.md. Decision: docs/DECISION.md. Integrity manifest, inventories and the sealed review sample: audit/. Original v1 and v2 outputs are untouched.
```
uv run python -I src/audit_integrity.py .
uv run python -I src/audit_inventory.py .
uv run python -I -m unittest discover -s tests
uv run python -I src/score_v3.py data/gold.csv runs/calls.jsonl data/namespace_canon.json results_v3 runs/*.jsonl
uv run python -I src/analyze_v3.py data/gold.csv results_v3
uv run python -I src/transitions_v3.py data/gold.csv results results_v2 results_v3
uv run python -I src/review_agreement.py audit results_v3
```
The sealed sample (audit/review_sample.sha256) reproduces with src/sample_review.py run against the evaluator frozen at commit 3a41055, before the single correction round.
