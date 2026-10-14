# Concordância entre a v3 automática e a revisão cega assistida

A revisão foi feita por LLM, às cegas para a categoria automática, com justificativa e confiança por item. Não é validação humana independente. Amostra: 144 respostas, sorteadas com semente fixa e seladas por hash antes da revisão (`audit/review_sample.sha256`).

## Concordância por dimensão

| dimensão | iguais | n | taxa |
|---|---:|---:|---:|
| category | 120 | 144 | 83.3% |
| entity | 120 | 144 | 83.3% |
| namespace | 98 | 144 | 68.1% |
| behaviour | 144 | 144 | 100.0% |

## Concordância da categoria por estrato

| estrato | iguais | n | taxa |
|---|---:|---:|---:|
| changed | 14 | 37 | 37.8% |
| correct | 50 | 50 | 100.0% |
| format | 8 | 8 | 100.0% |
| hedge | 21 | 21 | 100.0% |
| wrong | 27 | 28 | 96.4% |

## Matriz de confusão da categoria (linhas: revisão; colunas: v3)

| revisão \ v3 | AMBIG_DECLARED | AMBIG_FLAG | CORRECT | FORMAT | MIXED | OTHER_WRONG | PARTIAL | SINGLE | SINGLE_CORRECT | UNKNOWN | UNRESOLVED | WRONG |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| AMBIG_DECLARED | 5 |  |  |  |  |  |  |  |  |  |  |  |
| AMBIG_FLAG |  | 8 |  |  |  |  |  |  |  |  |  |  |
| CORRECT |  |  | 41 |  |  |  |  |  |  |  | 5 |  |
| FORMAT |  |  |  | 8 |  |  |  |  |  |  |  |  |
| MIXED |  |  |  |  | 4 |  |  |  |  |  |  |  |
| OTHER_WRONG |  |  |  |  |  | 20 |  |  |  |  | 9 |  |
| PARTIAL |  |  |  |  |  |  | 1 |  |  |  |  |  |
| SINGLE |  |  |  |  |  |  |  | 2 |  |  |  |  |
| SINGLE_CORRECT |  |  |  |  |  |  |  |  | 7 |  | 2 |  |
| UNKNOWN |  |  |  |  |  |  |  |  |  | 7 |  |  |
| UNRESOLVED |  |  |  |  |  | 1 |  |  |  |  | 10 |  |
| WRONG |  |  |  |  |  |  |  |  |  |  | 7 | 7 |

## Principais desacordos

- revisão OTHER_WRONG contra v3 UNRESOLVED: 9
- revisão WRONG contra v3 UNRESOLVED: 7
- revisão CORRECT contra v3 UNRESOLVED: 5
- revisão SINGLE_CORRECT contra v3 UNRESOLVED: 2
- revisão UNRESOLVED contra v3 OTHER_WRONG: 1

Lista completa com justificativas em `audit/review_disagreements.csv` (24 itens).
