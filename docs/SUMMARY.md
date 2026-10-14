# Same code, different worlds: summary of a closed study

## Question

When one string denotes different entities in different identifier systems (`OMA` is Oman in the IOC list, Oman Air among ICAO airline designators and Eppley Airfield among IATA airports), does a language model miss the requested reading more often than it misses a code with no competing reading, even when it knows the requested reading?

## Design

The design is set out in `docs/PROTOCOL.md`, frozen before sampling.

- Seven systems of the 3char dataset: IATA airports, ICAO airline designators, ISO 3166-1 alpha-3, IOC country codes, ISO 4217, SEC tickers and DNS record types.
- 31 colliding literals with 67 readings, and 53 control readings paired by system, code length and Wikipedia pageviews within a factor of 2.
- Gold labels and aliases taken from the dataset files and Wikidata, reviewed by hand and frozen with a SHA-256 before the first model call.
- Four conditions with three paraphrases each: no namespace (C1); namespace named (C2); namespace implied by a usage context such as a boarding pass or a medal table (C3); and the registry record given in the prompt (C4).
- Two familiarity probes per reading: entity to code (P1), and code to entity with a distractor (P2).
- Three models (Qwen3 8B, Gemma 3 12B, Llama 3.1 8B), one provider, temperature 0 and JSON-schema output; 1,692 calls per model, with every raw response kept, including retries.
- Pre-registered criterion for continuing: an error difference of 10 points between colliding readings and controls in two of the three models, with the competing reading as the dominant error.

## Original result

The original report (`docs/REPORT.md`, scorer v2) found error differences of 0 to 15 points with intervals crossing zero, and the competing reading chosen in 0 to 5% of known readings. It recommended reformulating the question.

## Audit

The audit is specified in `docs/AUDIT_PROTOCOL.md` and reported in `docs/AUDIT_REPORT.md`.

- **Integrity.** The gold file is identical to the frozen blob, the calls were rebuilt byte for byte, every call is covered for every model, and the original scorer outputs were rebuilt with identical hashes.
- **Defects in the original scorer.** Entities were matched by token subsets, so "Oman Air" counted as Oman and "Brussels" as Brussels Airport. The namespace named by the model was ignored, and responses with several readings were scored as one string. The status field of the P1 probe was unusable: the models returned "unknown" in 119, 89 and 120 of 120 probes.
- **Evaluator v3.** Each response is scored on three independent dimensions: entity, namespace and behaviour. Aliases must match in full, related systems are never merged (ISO 3166 is not the IOC list), what the rules cannot decide is marked `UNRESOLVED`, and 94 repetition loops are marked `FORMAT`/`TRUNCATED`.
- **Validation.** 144 responses were sealed by hash and reviewed blind, with LLM assistance rather than independent human review. Category agreement was 83.3%. Three systematic causes of disagreement found in that sample were then corrected, and agreement on the same sample rose to 92.4%; because the corrections were guided by that sample, 92.4% overstates agreement on new responses. Namespace agreement was 100% where both found the entity.
- **Rescoring.** All 5,076 responses were rescored, and 348 changed category. In Llama C2, the penalty fell from +22.2 points under the first scorer to +7.9 under the corrected scorers.

## Audited findings

| Measure | Result |
| --- | --- |
| Competing reading chosen, among readings the model recognizes (C2 and C3) | 3 of 666 (0.5%). A further 24 responses build a wrong entity around the competitor's name: 18 from Gemma, across 7 literals in total |
| Error penalty of a colliding literal against its control, by familiarity cut | Llama C2: 0.0 under P1, +16.7 under P1∩P2. Gemma under P1: +37.5 in C2, −4.2 in C3. Qwen C3: +16.7 with the primary rule, −2.8 with the lenient rule. The 95% intervals are 18 to 71 points wide |
| Namespace of the correct entity | The requested system or an equivalent in 100% of C2 and C4. In C3, Llama labels countries in an Olympic context as ISO 3166-1 alpha-3 in 14 of 72 cases |
| No namespace (C1) | Ambiguity declared at similar rates for colliding and control literals (Qwen 42% and 41%, Gemma 77% and 66%, Llama 0% and 0%); 21% of Llama's C1 responses are truncated loops |
| Record in the prompt (C4) | 0 to 3% error, and no competing reading |

## Decision

The study was closed (`docs/DECISION.md`). Specific interference was nearly absent among known readings, and the general penalty was not robust to the evaluator, the familiarity cut or the model. The behaviours that did repeat, namely the gap between recognizing and producing a reading, hedging that ignores real ambiguity, and full resolution when the record is in context, are already described in the literature (Sedova et al. 2024; AmbigDocs; WhoQA). With 7 to 25 known pairs per model, the material cannot answer the question, and the absence of significance does not by itself justify a larger sample. The intervals cannot exclude effects of 10 points in any model, so the absence of a robust effect is not evidence that no effect exists.

Three results remain reusable: the three-dimension evaluator with an `UNRESOLVED` state; the table that maps how models name code systems to canonical systems (581 distinct strings for 7 systems); and the measurement findings on JSON-schema probes and repetition loops.
