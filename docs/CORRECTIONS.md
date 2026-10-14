# Corrections to the frozen documents

The protocol, reports, audit documents and generated outputs of this study are kept as they were written and are not edited. This note records the corrections found during a later editorial review. Every figure below was recomputed from the files in this repository; no model was called and no score changed. `README.md` and `docs/SUMMARY.md` already use the corrected values.

## Script paths

The scripts were moved from `src/` into `src/poc/` and `src/audit/` (commit `f336dde`). The frozen documents still cite the old paths, and the generated reports in `audit/` and `results_v3/` print them in their headers, because the scripts were moved without changing their output.

| Old path | Current path | Cited in |
| --- | --- | --- |
| `src/finalize_gold.py` | `src/poc/finalize_gold.py` | `docs/PROTOCOL.md` |
| `src/score_v3.py` | `src/audit/score_v3.py` | `docs/AUDIT_PROTOCOL.md`, `docs/AUDIT_REPORT.md`, `audit/TASKS.md` |
| `src/audit_integrity.py` | `src/audit/audit_integrity.py` | `audit/INTEGRITY.md` |
| `src/audit_inventory.py` | `src/audit/audit_inventory.py` | `audit/alias_inventory.md`, `audit/system_inventory.md` |
| `src/analyze_v3.py` | `src/audit/analyze_v3.py` | `results_v3/metrics.md` |
| `src/transitions_v3.py` | `src/audit/transitions_v3.py` | `results_v3/DIFF.md` |

## Width of the E1 intervals

`docs/AUDIT_REPORT.md` (section 4) and `docs/DECISION.md` (item 4) state that the 95% intervals of E1 are 25 to 60 points wide. Across the three models, conditions C2 and C3, the familiarity cuts P2, P1 and P1∩P2, and the primary scoring rule in `results_v3/summary.json`, the widths range from 18.3 points (Llama, C2, P1∩P2) to 70.8 points (Qwen, C2, P1∩P2). The conclusion that only very large effects would be detectable is unchanged.

## Wrong entities built on the competitor's name

`docs/AUDIT_REPORT.md` (sections 4 and 5) and `docs/DECISION.md` (item 1) describe the 24 `UNRESOLVED` responses that lean towards the competing reading as concentrated in 4 literals and one model. The 18 responses from Gemma cover 4 literals (`ARU`, `COP`, `DTE`, `MYA`). Including the 5 responses from Llama (`ARU`, `OMA`, `SIG`) and the 1 from Qwen (`TXT`), the 24 responses cover 7 literals.

## Number of known pairs per model

`docs/DECISION.md` (item 4) gives 8 to 25 known pairs per model, and `docs/AUDIT_REPORT.md` (section 5) gives 8 to 12 pairs for the P1∩P2 cut. For Gemma, the P1∩P2 cut has 7 pairs (`results_v3/metrics.md`), so the ranges are 7 to 25 and 7 to 12.

## Reproduction command

The previous `README.md` passed `runs/*.jsonl` to `score_v3.py`. The pattern also matches `runs/calls.jsonl`, which holds the planned calls rather than responses, and the scorer stops with a `KeyError`. The current README lists the three response files explicitly; with them, the commands rebuild every file in `results_v3/` byte for byte.
