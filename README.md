# poc-nsi

**Do language models misread a code when the same string belongs to several registries?** This closed exploratory study tested that question on seven systems of the [3char](https://huggingface.co/datasets/brennercruvinel/3char) dataset. It found no robust evidence of such an effect, and the line of work was closed; the sample was too small to rule out moderate effects.

## Why this was studied

`OMA` is Oman in the IOC country list, Oman Air among ICAO airline designators and Eppley Airfield among IATA airports. A model asked about one of these readings might return another, either because the competing reading is more familiar or because the request does not make the namespace clear enough. If that happened even when the model demonstrably knew the requested reading, shared codes would be a specific source of error, distinct from not knowing the code at all.

## How it was tested

The design, the decision criteria and the deviations are in `docs/PROTOCOL.md`, committed before sampling. The study used 31 shared codes with 67 readings across seven systems (IATA airports, ICAO airline designators, ISO 3166-1 alpha-3, IOC country codes, ISO 4217, SEC tickers and DNS record types), each paired with a control code of a single reading from the same system, of the same length and with similar Wikipedia pageviews. Gold answers were frozen with a checksum before the first model call.

Each reading was asked under four conditions, with three paraphrases each: with no namespace, with the namespace named, with the namespace implied by a context such as a boarding pass or a medal table, and with the registry record supplied in the prompt. Two probes measured whether the model knew each reading, from entity to code and from code to entity. Three models (Qwen3 8B, Gemma 3 12B and Llama 3.1 8B) answered 1,692 prompts each through one provider, at temperature 0 and with JSON-schema output; all 5,076 responses were kept. The pre-registered criterion for continuing was an error difference of 10 points between shared codes and controls in two of the three models, with the competing reading as the dominant error.

## What happened

The original scoring (`docs/REPORT.md`) found error differences of 0 to 15 points with intervals crossing zero, and the competing reading chosen in 0 to 5% of known readings.

A post hoc audit (`docs/AUDIT_PROTOCOL.md`, `docs/AUDIT_REPORT.md`) then found defects in that scorer: names were matched by token subsets, so "Oman Air" counted as Oman; the namespace named by the model was ignored; and responses with several readings were scored as a single string. A new evaluator scored each response separately on entity, namespace and behaviour, required aliases to match in full, and marked as `UNRESOLVED` whatever its rules could not decide. All 5,076 responses were rescored and 348 changed category. The audit is itself post hoc: it was designed after the original results were known.

Under the audited scores:

- When a model recognized the requested reading, it chose the competing reading in 3 of 666 responses (0.5%). In 24 further responses, 18 of them from Gemma, it built a wrong entity around the competitor's name; these span 7 codes.
- The general error penalty of shared codes against their controls changed sign or disappeared across familiarity cuts, conditions and scoring rules. The 95% intervals were 18 to 71 points wide.
- With the registry record in the prompt, errors fell to 0 to 3%, with no competing reading.

The audit evaluator was checked against a blind, LLM-assisted review of 144 sealed responses. Agreement on category was 83.3% at first. Three systematic causes of disagreement found in that sample were then corrected, and agreement on the same sample rose to 92.4%. Because the corrections were guided by the sample used to measure them, 92.4% overstates agreement on new responses; no second sample and no independent human review were used.

## What was concluded

The study found no robust evidence that shared codes cause a specific error when the model knows the requested reading. This is not evidence that no such effect exists: with 7 to 25 known pairs per model, the intervals cannot exclude effects of about 10 points. The behaviours that did repeat across models, such as hedging that ignores whether a code is actually ambiguous and full resolution when the record is in context, are already described in the literature (Sedova et al. 2024; AmbigDocs; WhoQA). Answering the question would require a different familiarity design and a larger sample, which the absence of a signal did not justify. The decision and its grounds are in `docs/DECISION.md`.

## What remains useful

The three-dimension evaluator with an `UNRESOLVED` state can be reused for any evaluation of short codes. `data/namespace_canon.json` maps the 581 distinct ways the models named the seven systems to canonical systems. The study also documents two measurement problems: the status field of the entity-to-code probe was unusable under JSON-schema output, and 94 responses were truncated repetition loops, 52 of them from Llama with no namespace.

`docs/SUMMARY.md` gives the full results in English. The protocol, reports and audit documents are in Portuguese and form the primary record; `docs/CORRECTIONS.md` lists corrections to them.

## Reproducing

Running the probe again requires an `HF_TOKEN` with Inference Providers access, and the scripts in `src/poc/` take the path of a local copy of the 3char dataset as an argument. The published responses make a new run unnecessary. The audit needs no network access:

```bash
uv run --no-project python -I -m unittest discover -s tests
uv run --no-project python -I src/audit/score_v3.py data/gold.csv runs/calls.jsonl data/namespace_canon.json results_v3 \
    runs/qwen3-8b.jsonl runs/gemma-3-12b.jsonl runs/llama-3.1-8b.jsonl
uv run --no-project python -I src/audit/analyze_v3.py data/gold.csv results_v3
uv run --no-project python -I src/audit/transitions_v3.py data/gold.csv results results_v2 results_v3
```

These commands rewrite `results_v3/` with byte-identical files. `data/pageviews_cache.json` caches the Wikipedia pageview responses of 2026-10-14, so the item selection can be reproduced offline.

## The record

| Path | Contents | State |
| --- | --- | --- |
| `docs/PROTOCOL.md`, `docs/ORIGINALITY.md` | Design and decision criteria; prior work and its overlap with this design | Frozen before sampling |
| `data/gold.csv`, `data/gold.sha256` | 67 readings of shared codes, 53 paired controls, aliases and popularity | Frozen before the first model call |
| `runs/` | The planned prompts (`calls.jsonl`) and each model's raw responses, including retries, with run logs | Raw |
| `src/poc/`, `results/`, `results_v2/`, `docs/REPORT.md` | The study scripts, the pre-registered scorer, its one adjudicated correction and the original report | Original |
| `docs/AUDIT_PROTOCOL.md`, `src/audit/`, `tests/`, `audit/` | The audit evaluator, frozen before rescoring, with its tests, integrity manifest, inventories and blind review | Audit |
| `results_v3/`, `docs/AUDIT_REPORT.md`, `docs/DECISION.md` | Rescored responses, metrics, transitions from earlier scores, findings and the decision | Audit |
| `docs/SUMMARY.md`, `docs/CORRECTIONS.md` | English summary and corrections to the frozen documents | Current |

The code is released under the MIT license. The model outputs in `runs/` were produced by third-party models and are provided as collected.
