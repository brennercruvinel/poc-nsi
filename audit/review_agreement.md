# Concordância entre a v3 automática e a revisão cega assistida

A revisão foi feita por LLM, às cegas para a categoria automática, com justificativa e confiança por item. Não é validação humana independente. Amostra: 144 respostas, sorteadas com semente fixa e seladas por hash antes da revisão (`audit/review_sample.sha256`).

## Concordância por dimensão

| dimensão | iguais | n | taxa |
|---|---:|---:|---:|
| category | 133 | 144 | 92.4% |
| entity | 133 | 144 | 92.4% |
| behaviour | 144 | 144 | 100.0% |
| namespace | 59 | 59 | 100.0% |

O namespace é comparado só nas respostas em que revisão e v3 encontraram a entidade correta, na escala OK (CORRECT ou EQUIVALENT), INCORRECT, UNRESOLVED.

## Concordância da categoria por estrato

| estrato | iguais | n | taxa |
|---|---:|---:|---:|
| changed | 26 | 37 | 70.3% |
| correct | 50 | 50 | 100.0% |
| format | 8 | 8 | 100.0% |
| hedge | 21 | 21 | 100.0% |
| wrong | 28 | 28 | 100.0% |

## Matriz de confusão da categoria (linhas: revisão; colunas: v3)

| revisão \ v3 | AMBIG_DECLARED | AMBIG_FLAG | CORRECT | FORMAT | MIXED | OTHER_WRONG | PARTIAL | SINGLE | SINGLE_CORRECT | UNKNOWN | UNRESOLVED | WRONG |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| AMBIG_DECLARED | 5 |  |  |  |  |  |  |  |  |  |  |  |
| AMBIG_FLAG |  | 8 |  |  |  |  |  |  |  |  |  |  |
| CORRECT |  |  | 44 |  |  |  |  |  |  |  | 2 |  |
| FORMAT |  |  |  | 8 |  |  |  |  |  |  |  |  |
| MIXED |  |  |  |  | 4 |  |  |  |  |  |  |  |
| OTHER_WRONG |  |  |  |  |  | 26 |  |  |  |  | 3 |  |
| PARTIAL |  |  |  |  |  |  | 1 |  |  |  |  |  |
| SINGLE |  |  |  |  |  |  |  | 2 |  |  |  |  |
| SINGLE_CORRECT |  |  |  |  |  |  |  |  | 8 |  | 1 |  |
| UNKNOWN |  |  |  |  |  |  |  |  |  | 7 |  |  |
| UNRESOLVED |  |  |  |  |  |  |  |  |  |  | 11 |  |
| WRONG |  |  |  |  |  |  |  |  |  |  | 5 | 9 |

## Principais desacordos

- revisão WRONG contra v3 UNRESOLVED: 5
- revisão OTHER_WRONG contra v3 UNRESOLVED: 3
- revisão CORRECT contra v3 UNRESOLVED: 2
- revisão SINGLE_CORRECT contra v3 UNRESOLVED: 1

Lista completa com justificativas em `audit/review_disagreements.csv` (11 itens).
