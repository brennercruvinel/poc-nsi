# Transições v1 → v2 → v3

Gerado por `src/transitions_v3.py`. Cada mudança por call_id, com a evidência v3 responsável, está em `results_v3/transitions.csv`.

- Respostas C1 a C4: 3996; com categoria diferente entre alguma versão anterior e a v3: 316 (7.9%). Sondas P1 e P2 com diferença v2 → v3: 32.

## v1 → v3, C1

| v1 \ v3 | AMBIG_DECLARED | FORMAT | MULTI | PARTIAL | SINGLE | SINGLE_CORRECT | UNKNOWN | UNRESOLVED | WRONG |
|---|---|---|---|---|---|---|---|---|---|
| AMBIG_DECLARED | 170 |  |  |  |  |  |  |  |  |
| FORMAT |  | 55 |  |  |  |  |  |  |  |
| MULTI |  |  | 1 | 2 |  |  |  |  |  |
| PARTIAL |  |  |  | 107 |  |  |  |  |  |
| SINGLE |  |  |  |  | 15 |  |  | 5 |  |
| SINGLE_CORRECT |  |  |  |  |  | 59 |  | 1 |  |
| UNKNOWN |  |  |  |  |  |  | 2 |  |  |
| UNRESOLVED |  |  |  |  |  |  |  |  |  |
| WRONG |  |  |  |  |  |  |  | 12 | 327 |

## v1 → v3, C234

| v1 \ v3 | AMBIG_FLAG | BOTH | COMPETING | CORRECT | FORMAT | MIXED | OTHER_WRONG | UNKNOWN | UNRESOLVED |
|---|---|---|---|---|---|---|---|---|---|
| AMBIG_FLAG | 150 |  |  |  |  |  |  |  |  |
| BOTH |  |  |  | 50 |  | 1 |  |  | 2 |
| COMPETING |  |  | 21 |  |  |  |  |  | 36 |
| CORRECT |  |  |  | 1620 |  | 24 |  |  | 10 |
| FORMAT |  |  |  |  | 7 |  |  |  |  |
| MIXED |  |  |  |  |  |  |  |  |  |
| OTHER_WRONG |  |  |  | 2 |  |  | 1002 |  | 171 |
| UNKNOWN |  |  |  |  |  |  |  | 144 |  |
| UNRESOLVED |  |  |  |  |  |  |  |  |  |

## v1 → v3, probes

| v1 \ v3 | FAIL | FORMAT | PASS | no | unknown | yes |
|---|---|---|---|---|---|---|
| FAIL | 194 | 32 |  |  |  |  |
| FORMAT |  |  |  |  |  |  |
| PASS |  |  | 134 |  |  |  |
| no |  |  |  | 405 |  |  |
| unknown |  |  |  |  | 28 |  |
| yes |  |  |  |  |  | 287 |

## v2 → v3, C1

| v2 \ v3 | AMBIG_DECLARED | FORMAT | MULTI | PARTIAL | SINGLE | SINGLE_CORRECT | UNKNOWN | UNRESOLVED | WRONG |
|---|---|---|---|---|---|---|---|---|---|
| AMBIG_DECLARED | 170 |  |  |  |  |  |  |  |  |
| FORMAT |  | 55 |  |  |  |  |  |  |  |
| MULTI |  |  | 1 | 2 |  |  |  |  |  |
| PARTIAL |  |  |  | 107 |  |  |  |  |  |
| SINGLE |  |  |  |  | 15 |  |  | 5 |  |
| SINGLE_CORRECT |  |  |  |  |  | 59 |  | 1 |  |
| UNKNOWN |  |  |  |  |  |  | 2 |  |  |
| UNRESOLVED |  |  |  |  |  |  |  |  |  |
| WRONG |  |  |  |  |  |  |  | 12 | 327 |

## v2 → v3, C234

| v2 \ v3 | AMBIG_FLAG | COMPETING | CORRECT | FORMAT | MIXED | OTHER_WRONG | UNKNOWN | UNRESOLVED |
|---|---|---|---|---|---|---|---|---|
| AMBIG_FLAG | 150 |  |  |  |  |  |  |  |
| COMPETING |  | 21 |  |  |  |  |  | 36 |
| CORRECT |  |  | 1672 |  | 24 |  |  | 12 |
| FORMAT |  |  |  | 7 |  |  |  |  |
| MIXED |  |  |  |  |  |  |  |  |
| OTHER_WRONG |  |  |  |  | 1 | 1002 |  | 171 |
| UNKNOWN |  |  |  |  |  |  | 144 |  |
| UNRESOLVED |  |  |  |  |  |  |  |  |

## v2 → v3, probes

| v2 \ v3 | FAIL | FORMAT | PASS | no | unknown | yes |
|---|---|---|---|---|---|---|
| FAIL | 194 | 32 |  |  |  |  |
| FORMAT |  |  |  |  |  |  |
| PASS |  |  | 134 |  |  |  |
| no |  |  |  | 405 |  |  |
| unknown |  |  |  |  | 28 |  |
| yes |  |  |  |  |  | 287 |

## Regras responsáveis pelas mudanças v2 → v3

| regra | n | exemplo (call_id) |
|---|---:|---|
| no strong alias match | 237 | Qwen3-8B C3|ARU|lng/ioc|1 OTHER_WRONG→UNRESOLVED |
| probe | 32 | Qwen3-8B P1|SIG|fin/tck|0 FAIL→FORMAT |
| multiple readings, wrong claims no longer discarded | 25 | Qwen3-8B C3|KUW|lng/ioc|1 CORRECT→MIXED |
| MULTI->PARTIAL | 2 | Qwen3-8B C1|collision|BRU|1 MULTI→PARTIAL |

## Efeito sobre E1 primário, recorte P2

| modelo | cond | v1 | v2 | v3 |
|---|---|---|---|---|
| Llama-3.1-8B-Instruct | C2 | +22.2 [+8.3; +36.5] (21 pares, 16 literais) | +7.9 [-3.2; +21.1] (21 pares, 16 literais) | +7.9 [-3.2; +21.1] (21 pares, 16 literais) |
| Llama-3.1-8B-Instruct | C3 | +20.6 [+1.5; +40.9] (21 pares, 16 literais) | +11.1 [-1.6; +25.0] (21 pares, 16 literais) | +15.9 [+2.0; +30.3] (21 pares, 16 literais) |
| Qwen3-8B | C2 | -2.8 [-39.4; +28.6] (12 pares, 11 literais) | -2.8 [-39.4; +28.6] (12 pares, 11 literais) | +0.0 [-33.3; +30.8] (12 pares, 11 literais) |
| Qwen3-8B | C3 | -2.8 [-33.3; +23.1] (12 pares, 11 literais) | -2.8 [-33.3; +23.1] (12 pares, 11 literais) | +16.7 [-9.1; +41.0] (12 pares, 11 literais) |
| gemma-3-12b-it | C2 | +21.3 [+3.7; +39.1] (25 pares, 17 literais) | +14.7 [-2.9; +33.3] (25 pares, 17 literais) | +16.0 [-2.3; +33.3] (25 pares, 17 literais) |
| gemma-3-12b-it | C3 | +8.0 [-8.3; +24.2] (25 pares, 17 literais) | +8.0 [-8.3; +24.2] (25 pares, 17 literais) | +8.0 [-8.3; +24.2] (25 pares, 17 literais) |
