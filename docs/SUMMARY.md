# Same code, different worlds: summary of a closed study

## question

When one literal denotes different entities in different identifier systems (`OMA`: Oman in the IOC list, Oman Air among ICAO airline designators, Eppley Airfield among IATA airports), does a language model miss the asked reading more often than it misses a code with no competing reading, even when it knows the asked reading?

## design (docs/PROTOCOL.md, frozen before sampling)

- Seven systems of the 3char dataset: IATA airports, ICAO airline designators, ISO 3166-1 alpha-3, IOC country codes, ISO 4217, SEC tickers, DNS record types.
- 31 colliding literals with 67 readings; 53 control readings paired by system, code length and Wikipedia pageviews within a factor of 2.
- Gold labels and aliases from the dataset file and Wikidata, reviewed by hand, frozen with a sha256 before the first model call.
- Four conditions, three paraphrases each: no namespace (C1); namespace named (C2); namespace implied by a usage context such as a boarding pass or a medal table (C3); the registry record given in the prompt (C4).
- Two familiarity probes per reading: entity to code (P1) and code to entity with a distractor (P2).
- Three models (Qwen3 8B, Gemma 3 12B, Llama 3.1 8B), one provider, temperature 0, JSON schema output. 1,692 calls per model; raw responses kept, including retries.
- Pre-registered criteria: a difference of 10 points in error between colliding readings and controls, in two of three models, with the competing reading as the dominant error, would justify going deeper.

## original result (docs/REPORT.md, scorer v2)

Error differences of 0 to 15 points with intervals crossing zero; competing reading chosen in 0 to 5% of known readings; recommendation to reformulate.

## audit (docs/AUDIT_PROTOCOL.md, docs/AUDIT_REPORT.md)

- Integrity: gold file identical to the frozen blob; calls rebuilt byte-identical; every call covered per model; original scorer outputs rebuilt hash-identical.
- Defects found in the original scorer: entity match by token subsets ("Oman Air" counted as Oman, "Brussels" as Brussels Airport); the namespace the model named was ignored; multiple readings were scored as one string; the P1 probe's status field was unusable (status "unknown" on 119, 89 and 120 of 120 probes).
- Evaluator v3: three independent dimensions per response, entity, namespace, behaviour; whole-alias matching; related systems never merged (ISO 3166 is not the IOC list); UNRESOLVED for what the rules cannot decide; FORMAT/TRUNCATED for 94 repetition loops.
- Validation: 144 responses sealed by hash and reviewed blind (LLM-assisted, not independent human review); 83.3% category agreement before one correction round, 92.4% after; 100% on namespace where both found the entity.
- All 5,076 responses rescored; 348 changed category; half of the first scorer's effect in Llama C2 was the subset artefact.

## audited findings

| measure | result |
| --- | --- |
| competing reading chosen, readings the model recognises (C2 and C3) | 3 of 666 (0.5%); plus 24 wrong entities built around the competitor's name, 4 literals, mostly Gemma |
| error penalty of colliding literal vs control, by familiarity cut | Llama C2: 0.0 under P1, +16.7 under P1∩P2; Gemma: +37.5 in C2, −4.2 in C3 under P1; Qwen C3: +16.7 primary, −2.8 lenient. Intervals 25 to 60 points |
| namespace of the correct entity | the asked system or an equivalent in 100% of C2 and C4; in C3 Llama labels IOC-context countries as ISO 3166-1 alpha-3 in 14 of 72 |
| no namespace (C1) | ambiguity declared at the same rate on colliding and control literals (42/41, 77/66, 0/0); 21% of Llama's C1 responses are truncated loops |
| record in the prompt (C4) | 0 to 3% error, no competing reading |

## decision (docs/DECISION.md)

Close. Specific interference is near absent in known readings; the general penalty is not robust to the evaluator, the familiarity cut or the model; the behaviours that do repeat (the gap between recognising and producing a reading, hedging indifferent to real ambiguity, full resolution with the record in context) are already in the literature (Sedova et al. 2024; AmbigDocs; WhoQA). With 8 to 25 known pairs per model the material cannot answer the question, and enlarging the sample is not justified by the absence of significance.

What remains reusable: the three-dimension evaluator with an UNRESOLVED state, the canonisation table of how models name code systems (581 distinct strings for 7 systems), and the measurement findings about JSON-schema probes and repetition loops.
