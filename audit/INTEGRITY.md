# Manifesto de integridade

Gerado por `src/audit_integrity.py`; os números completos estão em `audit/integrity.json`. Nada foi corrigido: este manifesto só registra.

## Gabarito
- `data/gold.csv`: sha256 9048f3d7…033cdd, igual ao `data/gold.sha256` e ao blob do commit 6197b9e. 120 linhas: 67 leituras colidentes e 53 controles.
- Nenhum commit depois de 6197b9e tocou em `data/gold.csv` ou `runs/calls.jsonl`.

## Sequência dos commits (branch main)
1. 02d6bb5, 00:22: protocolo e revisão de originalidade.
2. 6197b9e, 01:04: gabarito congelado, chamadas construídas, desvios 1 a 8, `score.py` v1.
3. 3e5cbfd, 02:00: respostas brutas dos três modelos, desvios 9 e 10, modo `--redo-truncated` em `run.py`.
4. 8776d18, 02:04: `score.py` ganha a v2 (ativada por `SCORER=v2`), adjudicação de BOTH, relatório.
5. 65190d2, 02:39: correção do README.
- O avaliador v1 foi commitado antes das chamadas; a v2 foi commitada depois dos resultados, como o relatório declara.
- `docs/PROTOCOL.md` mudou em 6197b9e e 3e5cbfd só na seção Desvios.

## Chamadas planejadas
- `runs/calls.jsonl` reconstruído de `gold.csv` com `prompts.py`: sha256 idêntico (8f986f3c…).
- 1.692 chamadas: C1 252, C2 360, C3 360, C4 360, P1 120, P2T 120, P2F 120. Total nos três modelos: 5.076.

## Respostas brutas, por modelo

| | Qwen3 8B | Gemma 3 12B | Llama 3.1 8B |
|---|---:|---:|---:|
| Registros no JSONL | 1.700 | 1.727 | 1.765 |
| call_ids distintos | 1.692 | 1.692 | 1.692 |
| Faltando / sobrando | 0 / 0 | 0 / 0 | 0 / 0 |
| Registros com http ≠ 200 | 0 | 1 | 1 |
| call_ids com mais de um registro | 8 | 35 | 73 |
| Repetidos por truncamento (desvio 9) | 8 | 34 | 72 |
| Ainda truncados após a repetição | 4 | 31 | 59 |
| Recuperados após falha de rede (desvio 10) | 0 | 1 | 1 |
| Resposta definitiva com http ≠ 200 ou sem conteúdo | 0 | 0 | 0 |
| Prompt enviado diferente do planejado | 0 | 0 | 0 |

- Truncados definitivos por condição: Qwen3 C1 3 e P1 1; Gemma P1 31; Llama C1 52, C3 6 e C2 1.
- Recuperados: Gemma `C4|NEM|fin/tck|2`, Llama `P2F|CVE|trp/ica2|0`.
- `resp_model` devolvido pelo provedor é sempre o modelo pedido; o registro nulo é a falha de rede repetida.
- Janela de execução: 04:04 a 05:00 UTC de 2026-10-14. As três execuções principais correram em paralelo.

## Regra de resposta definitiva
- Para cada call_id, vale o último registro com http 200; se não houver, o último registro.
- Essa regra foi escrita aqui e conferida contra a regra implícita de `score.py` (v1 e v2): equivalente em 100% dos call_ids dos três modelos.
- Consequência: a repetição com 1.500 tokens substitui a resposta de 400 tokens mesmo quando ambas estão truncadas.

## Preservação dos resultados anteriores
- `results/` (v1) e `results_v2/` reconstruídos com `score.py` em diretório temporário: `scored.csv` e `summary.json` com sha256 idênticos aos commitados.
- Árvore de trabalho limpa em `data/`, `runs/`, `results/`, `results_v2/` e `docs/PROTOCOL.md` no início da auditoria.

## Inconsistências encontradas
- Nenhuma de dados. Duas de processo, já declaradas no relatório anterior: a v2 e a adjudicação de BOTH foram feitas depois de ver os resultados, e a adjudicação cobre só o braço colidente.
- `src/__pycache__` está versionado desde 6197b9e; irrelevante para os dados.
