# Lista de tarefas da auditoria v3

Escopo fechado: sem chamadas novas, sem alteração de runs/, data/, results/, results_v2/, sem push.
Branch: audit-v3. Cada item é marcado ao concluir, com o artefato que o verifica.

## 0. Preparação
- [x] Branch audit-v3 criada a partir de main (65190d2)
- [x] Esta lista salva em audit/TASKS.md

## 1. Integridade
- [x] sha256 de gold.csv contra data/gold.sha256 e contra o blob do commit 6197b9e
- [x] Sequência dos commits: protocolo < gold < runs < resultados; nenhum arquivo congelado alterado depois
- [x] calls.jsonl reproduzível a partir de gold.csv com prompts.py (hash idêntico)
- [x] Contagem por modelo: planejadas, registros, call_ids distintos, http != 200, finish == length, repetições
- [x] Regra determinística de resposta definitiva por call_id, escrita e aplicada
- [x] Prompt enviado igual ao planejado em todo registro
- [x] results/ e results_v2/ reproduzíveis com score.py (hash)
- [x] Manifesto: audit/INTEGRITY.md e audit/integrity.json

## 2. Especificação do avaliador v3
- [x] 1. Inventário do campo system em audit/system_inventory.md
- [x] 2. Inventário de aliases do gabarito em audit/alias_inventory.md
- [x] 3. Tabela de canonização de namespaces em data/namespace_canon.json, sem colapsar sistemas relacionados
- [x] 4. docs/AUDIT_PROTOCOL.md: três dimensões (entidade, namespace, comportamento), taxonomia congelada, UNRESOLVED, FORMAT/TRUNCATED, dev separado de validação

## 3. Implementação e testes
- [x] 5. src/score_v3.py
- [x] 6. tests/test_score_v3.py com casos positivos e negativos, rodando
- [ ] 7. Avaliador congelado em commit antes da pontuação

## 4. Validação do instrumento
- [ ] 8. Amostra estratificada de 120 a 150 respostas, semente fixa, registrada antes da revisão
- [ ] 9. Revisão assistida cega, com identificador, interpretação, justificativa e confiança
- [ ] 10. Concordância, matriz de confusão e principais erros; no máximo uma rodada de correção

## 5. Reavaliação
- [ ] 11. results_v3/scored.csv com as 5.076 respostas; impacto de FORMAT/TRUNCATED à parte
- [ ] 12. E1 a E4 com recortes P1, P2 e P1 ∩ P2, pares e literais efetivos, sensibilidade às paráfrases
- [ ] 13. Transições v1 → v2 → v3 com regra responsável e impacto nas métricas

## 6. Relatório e decisão
- [ ] 14. docs/AUDIT_REPORT.md
- [ ] 15. docs/DECISION.md
- [ ] 16. Reconstrução do zero a partir de runs/ com hashes; arquivos com até 639 linhas
- [ ] 17. Rascunhos de commit no chat, commits na branch, sem push; resumo executivo e pedido vs entregue

## Regra metodológica fixada antes da v3
- Entidade, namespace e comportamento são dimensões independentes.
- Sistemas relacionados (COI e ISO 3166, IATA e ICAO) nunca são equivalentes; só nomes alternativos do mesmo sistema canonizam.
- O valor original de system é preservado; canônico, regra e confiança ficam em colunas separadas.
- Entidade correta com namespace errado é distinta de entidade concorrente com namespace errado.
- Taxonomia mínima congelada no protocolo; exceções vão para UNRESOLVED.
