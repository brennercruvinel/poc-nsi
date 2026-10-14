# Métricas v3

Gerado por `src/analyze_v3.py` a partir de `results_v3/scored.csv`. E1 em pontos percentuais: erro colidente menos erro controle, por par; intervalo de 95% por bootstrap de literais.

## E1 em C2

| modelo | recorte | primário | estrito (namespace) | leniente | UNRESOLVED como acerto |
|---|---|---|---|---|---|
| Qwen3-8B | P2 | +0.0 [-33.3; +30.8] (12 pares, 11 literais) | +0.0 [-33.3; +30.8] (12 pares, 11 literais) | +0.0 [-33.3; +30.8] (12 pares, 11 literais) | +2.8 [-21.2; +22.2] (12 pares, 11 literais) |
| Qwen3-8B | P1 | -6.7 [-36.7; +23.3] (10 pares, 10 literais) | -6.7 [-36.7; +23.3] (10 pares, 10 literais) | -6.7 [-36.7; +23.3] (10 pares, 10 literais) | +6.7 [-20.0; +33.3] (10 pares, 10 literais) |
| Qwen3-8B | P1andP2 | -12.5 [-50.0; +20.8] (8 pares, 8 literais) | -12.5 [-50.0; +20.8] (8 pares, 8 literais) | -12.5 [-50.0; +20.8] (8 pares, 8 literais) | +0.0 [-33.3; +25.0] (8 pares, 8 literais) |
| Qwen3-8B | P1strict | n/a | n/a | n/a | n/a |
| gemma-3-12b-it | P2 | +16.0 [-2.3; +33.3] (25 pares, 17 literais) | +16.0 [-2.3; +33.3] (25 pares, 17 literais) | +14.7 [-2.7; +32.1] (25 pares, 17 literais) | +8.0 [-16.0; +30.6] (25 pares, 17 literais) |
| gemma-3-12b-it | P1 | +37.5 [+23.8; +52.4] (8 pares, 7 literais) | +37.5 [+23.8; +52.4] (8 pares, 7 literais) | +33.3 [+18.5; +52.4] (8 pares, 7 literais) | +33.3 [+16.7; +50.0] (8 pares, 7 literais) |
| gemma-3-12b-it | P1andP2 | +33.3 [+19.0; +47.6] (7 pares, 6 literais) | +33.3 [+19.0; +47.6] (7 pares, 6 literais) | +28.6 [+16.7; +44.4] (7 pares, 6 literais) | +28.6 [+11.1; +44.4] (7 pares, 6 literais) |
| gemma-3-12b-it | P1strict | n/a | n/a | n/a | n/a |
| Llama-3.1-8B-Instruct | P2 | +7.9 [-3.2; +21.1] (21 pares, 16 literais) | +7.9 [-3.2; +21.1] (21 pares, 16 literais) | +7.9 [-3.2; +21.1] (21 pares, 16 literais) | +6.3 [-7.2; +21.1] (21 pares, 16 literais) |
| Llama-3.1-8B-Instruct | P1 | +0.0 [-14.3; +12.7] (21 pares, 17 literais) | +0.0 [-14.3; +12.7] (21 pares, 17 literais) | +0.0 [-14.3; +12.7] (21 pares, 17 literais) | -11.1 [-30.0; +6.3] (21 pares, 17 literais) |
| Llama-3.1-8B-Instruct | P1andP2 | +16.7 [+8.3; +26.7] (12 pares, 9 literais) | +16.7 [+8.3; +26.7] (12 pares, 9 literais) | +16.7 [+8.3; +26.7] (12 pares, 9 literais) | +13.9 [+5.1; +24.2] (12 pares, 9 literais) |
| Llama-3.1-8B-Instruct | P1strict | n/a | n/a | n/a | n/a |

## E1 em C3

| modelo | recorte | primário | estrito (namespace) | leniente | UNRESOLVED como acerto |
|---|---|---|---|---|---|
| Qwen3-8B | P2 | +16.7 [-9.1; +41.0] (12 pares, 11 literais) | +19.4 [-6.1; +44.4] (12 pares, 11 literais) | -2.8 [-33.3; +23.1] (12 pares, 11 literais) | +22.2 [-2.8; +44.4] (12 pares, 11 literais) |
| Qwen3-8B | P1 | +3.3 [-20.0; +23.3] (10 pares, 10 literais) | +6.7 [-20.0; +33.3] (10 pares, 10 literais) | -10.0 [-36.7; +16.7] (10 pares, 10 literais) | +6.7 [-23.3; +36.7] (10 pares, 10 literais) |
| Qwen3-8B | P1andP2 | +4.2 [-25.0; +29.2] (8 pares, 8 literais) | +8.3 [-25.0; +41.7] (8 pares, 8 literais) | -16.7 [-50.0; +16.7] (8 pares, 8 literais) | +4.2 [-20.8; +29.2] (8 pares, 8 literais) |
| Qwen3-8B | P1strict | n/a | n/a | n/a | n/a |
| gemma-3-12b-it | P2 | +8.0 [-8.3; +24.2] (25 pares, 17 literais) | +6.7 [-9.3; +22.7] (25 pares, 17 literais) | +9.3 [-9.1; +27.4] (25 pares, 17 literais) | +1.3 [-15.2; +17.4] (25 pares, 17 literais) |
| gemma-3-12b-it | P1 | -4.2 [-38.1; +15.2] (8 pares, 7 literais) | -8.3 [-38.1; +12.5] (8 pares, 7 literais) | -12.5 [-52.4; +14.8] (8 pares, 7 literais) | -4.2 [-38.1; +15.2] (8 pares, 7 literais) |
| gemma-3-12b-it | P1andP2 | -4.8 [-44.4; +18.2] (7 pares, 6 literais) | -9.5 [-44.4; +14.3] (7 pares, 6 literais) | -4.8 [-50.0; +22.2] (7 pares, 6 literais) | -4.8 [-44.4; +18.2] (7 pares, 6 literais) |
| gemma-3-12b-it | P1strict | n/a | n/a | n/a | n/a |
| Llama-3.1-8B-Instruct | P2 | +15.9 [+2.0; +30.3] (21 pares, 16 literais) | +19.0 [+5.9; +33.3] (21 pares, 16 literais) | +12.7 [-1.5; +27.0] (21 pares, 16 literais) | +7.9 [-3.0; +23.3] (21 pares, 16 literais) |
| Llama-3.1-8B-Instruct | P1 | +6.3 [-12.1; +23.2] (21 pares, 17 literais) | +7.9 [-10.5; +24.6] (21 pares, 17 literais) | +6.3 [-12.1; +23.2] (21 pares, 17 literais) | +0.0 [-15.8; +12.8] (21 pares, 17 literais) |
| Llama-3.1-8B-Instruct | P1andP2 | +19.4 [+2.4; +41.7] (12 pares, 9 literais) | +22.2 [+4.8; +43.6] (12 pares, 9 literais) | +19.4 [+2.4; +41.7] (12 pares, 9 literais) | +11.1 [+2.2; +25.9] (12 pares, 9 literais) |
| Llama-3.1-8B-Instruct | P1strict | n/a | n/a | n/a | n/a |

## E1 em C4

| modelo | recorte | primário | estrito (namespace) | leniente | UNRESOLVED como acerto |
|---|---|---|---|---|---|
| Qwen3-8B | P2 | +2.8 [+0.0; +9.1] (12 pares, 11 literais) | +2.8 [+0.0; +9.1] (12 pares, 11 literais) | +0.0 [+0.0; +0.0] (12 pares, 11 literais) | +2.8 [+0.0; +9.1] (12 pares, 11 literais) |
| Qwen3-8B | P1 | +0.0 [+0.0; +0.0] (10 pares, 10 literais) | +0.0 [+0.0; +0.0] (10 pares, 10 literais) | +0.0 [+0.0; +0.0] (10 pares, 10 literais) | +0.0 [+0.0; +0.0] (10 pares, 10 literais) |
| Qwen3-8B | P1andP2 | +0.0 [+0.0; +0.0] (8 pares, 8 literais) | +0.0 [+0.0; +0.0] (8 pares, 8 literais) | +0.0 [+0.0; +0.0] (8 pares, 8 literais) | +0.0 [+0.0; +0.0] (8 pares, 8 literais) |
| Qwen3-8B | P1strict | n/a | n/a | n/a | n/a |
| gemma-3-12b-it | P2 | -1.3 [-4.2; +0.0] (25 pares, 17 literais) | -1.3 [-4.2; +0.0] (25 pares, 17 literais) | -1.3 [-4.2; +0.0] (25 pares, 17 literais) | +0.0 [+0.0; +0.0] (25 pares, 17 literais) |
| gemma-3-12b-it | P1 | +0.0 [+0.0; +0.0] (8 pares, 7 literais) | +0.0 [+0.0; +0.0] (8 pares, 7 literais) | +0.0 [+0.0; +0.0] (8 pares, 7 literais) | +0.0 [+0.0; +0.0] (8 pares, 7 literais) |
| gemma-3-12b-it | P1andP2 | +0.0 [+0.0; +0.0] (7 pares, 6 literais) | +0.0 [+0.0; +0.0] (7 pares, 6 literais) | +0.0 [+0.0; +0.0] (7 pares, 6 literais) | +0.0 [+0.0; +0.0] (7 pares, 6 literais) |
| gemma-3-12b-it | P1strict | n/a | n/a | n/a | n/a |
| Llama-3.1-8B-Instruct | P2 | +0.0 [+0.0; +0.0] (21 pares, 16 literais) | +0.0 [+0.0; +0.0] (21 pares, 16 literais) | +0.0 [+0.0; +0.0] (21 pares, 16 literais) | +0.0 [+0.0; +0.0] (21 pares, 16 literais) |
| Llama-3.1-8B-Instruct | P1 | +0.0 [+0.0; +0.0] (21 pares, 17 literais) | +0.0 [+0.0; +0.0] (21 pares, 17 literais) | +0.0 [+0.0; +0.0] (21 pares, 17 literais) | +0.0 [+0.0; +0.0] (21 pares, 17 literais) |
| Llama-3.1-8B-Instruct | P1andP2 | +0.0 [+0.0; +0.0] (12 pares, 9 literais) | +0.0 [+0.0; +0.0] (12 pares, 9 literais) | +0.0 [+0.0; +0.0] (12 pares, 9 literais) | +0.0 [+0.0; +0.0] (12 pares, 9 literais) |
| Llama-3.1-8B-Instruct | P1strict | n/a | n/a | n/a | n/a |

## Categorias em leituras colidentes conhecidas (P2), por condição

| modelo | cond | n leituras | CORRECT | MIXED | COMPETING | UNRESOLVED (inclinado a concorrente) | OTHER_WRONG | AMBIG_FLAG | UNKNOWN | FORMAT |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Qwen3-8B | C2 | 25 | 36 | 0 | 0 | 9 (0) | 9 | 2 | 19 | 0 |
| Qwen3-8B | C3 | 25 | 31 | 10 | 2 | 11 (1) | 20 | 1 | 0 | 0 |
| Qwen3-8B | C4 | 25 | 74 | 1 | 0 | 0 (0) | 0 | 0 | 0 | 0 |
| gemma-3-12b-it | C2 | 45 | 48 | 0 | 0 | 14 (10) | 61 | 6 | 6 | 0 |
| gemma-3-12b-it | C3 | 45 | 45 | 0 | 0 | 14 (8) | 34 | 32 | 10 | 0 |
| gemma-3-12b-it | C4 | 45 | 133 | 0 | 0 | 2 (0) | 0 | 0 | 0 | 0 |
| Llama-3.1-8B-Instruct | C2 | 41 | 78 | 0 | 0 | 11 (2) | 34 | 0 | 0 | 0 |
| Llama-3.1-8B-Instruct | C3 | 41 | 66 | 6 | 1 | 8 (3) | 41 | 0 | 0 | 1 |
| Llama-3.1-8B-Instruct | C4 | 41 | 116 | 0 | 0 | 2 (0) | 4 | 0 | 1 | 0 |

## Categorias em leituras colidentes não conhecidas (P2)

| modelo | cond | n | CORRECT | COMPETING | UNRESOLVED (inclinado) | OTHER_WRONG | AMBIG_FLAG | UNKNOWN | FORMAT |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Qwen3-8B | C2 | 42 | 10 | 3 | 21 (12) | 43 | 7 | 42 | 0 |
| Qwen3-8B | C3 | 42 | 7 | 5 | 36 (8) | 71 | 5 | 0 | 0 |
| gemma-3-12b-it | C2 | 22 | 2 | 1 | 5 (3) | 53 | 3 | 2 | 0 |
| gemma-3-12b-it | C3 | 22 | 1 | 0 | 2 (0) | 25 | 35 | 3 | 0 |
| Llama-3.1-8B-Instruct | C2 | 26 | 3 | 2 | 8 (8) | 64 | 0 | 0 | 1 |
| Llama-3.1-8B-Instruct | C3 | 26 | 3 | 7 | 11 (4) | 55 | 0 | 0 | 2 |

## Namespace da leitura correta, colidentes conhecidos (P2)

| modelo | cond | CORRECT | EQUIVALENT | INCORRECT | UNRESOLVED |
|---|---|---:|---:|---:|---:|
| Qwen3-8B | C2 | 26 | 11 | 0 | 0 |
| Qwen3-8B | C3 | 16 | 18 | 0 | 8 |
| Qwen3-8B | C4 | 49 | 26 | 0 | 0 |
| gemma-3-12b-it | C2 | 35 | 15 | 0 | 0 |
| gemma-3-12b-it | C3 | 21 | 22 | 1 | 7 |
| gemma-3-12b-it | C4 | 94 | 39 | 0 | 0 |
| Llama-3.1-8B-Instruct | C2 | 56 | 22 | 0 | 0 |
| Llama-3.1-8B-Instruct | C3 | 38 | 19 | 14 | 1 |
| Llama-3.1-8B-Instruct | C4 | 78 | 39 | 0 | 0 |

## Paráfrases: erro primário por variante, P2 conhecidas

| modelo | cond | colidente v0/v1/v2 | controle v0/v1/v2 | E1 por variante |
|---|---|---|---|---|
| Qwen3-8B | C2 | 36/92/28 | 37/47/32 | -17/+33/-17 |
| Qwen3-8B | C3 | 68/52/56 | 42/42/37 | +17/+8/+25 |
| gemma-3-12b-it | C2 | 56/73/64 | 53/62/53 | +8/+28/+12 |
| gemma-3-12b-it | C3 | 71/60/69 | 74/74/71 | +12/+4/+8 |
| Llama-3.1-8B-Instruct | C2 | 27/59/24 | 40/50/37 | +5/+19/+0 |
| Llama-3.1-8B-Instruct | C3 | 49/44/46 | 43/40/47 | +19/+14/+14 |

## C1, sem namespace

| modelo | papel | MULTI | PARTIAL | SINGLE | SINGLE_CORRECT | AMBIG_DECLARED | UNRESOLVED | WRONG | UNKNOWN | FORMAT | ambíguo sem FORMAT |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Qwen3-8B | collision | 1 | 37 | 6 | 0 | 0 | 8 | 38 | 1 | 2 | 42% |
| Qwen3-8B | control | 0 | 0 | 0 | 21 | 65 | 0 | 72 | 0 | 1 | 41% |
| gemma-3-12b-it | collision | 0 | 72 | 2 | 0 | 0 | 3 | 16 | 0 | 0 | 77% |
| gemma-3-12b-it | control | 0 | 0 | 0 | 10 | 105 | 1 | 43 | 0 | 0 | 66% |
| Llama-3.1-8B-Instruct | collision | 0 | 0 | 7 | 0 | 0 | 5 | 56 | 0 | 25 | 0% |
| Llama-3.1-8B-Instruct | control | 0 | 0 | 0 | 28 | 0 | 1 | 102 | 1 | 27 | 0% |

## Familiaridade e falhas de geração

| modelo | P2 conhecidas (col/ctrl) | P1 conhecidas | P1 ∩ P2 | P1 estrita (status answer) | status em P1 | FORMAT por condição |
|---|---|---|---|---|---|---|
| Qwen3-8B | 44 (25/19) | 35 | 28 | 0 | {'unknown': 119, '': 1} | {'C1': 3, 'P1': 1} |
| gemma-3-12b-it | 79 (45/34) | 29 | 22 | 0 | {'unknown': 89, '': 31} | {'P1': 31} |
| Llama-3.1-8B-Instruct | 71 (41/30) | 70 | 51 | 0 | {'unknown': 120} | {'C1': 52, 'C3': 6, 'C2': 1} |
