# Relatório da auditoria v3: Same Code, Different Worlds

Auditoria pós-hoc dos dados coletados pela POC, sem chamadas novas. Tudo aqui é reconstruível a partir de `runs/`, `data/gold.csv` e dos scripts em `src/`, nos commits da branch `audit-v3`. Os resultados originais (v1, pré-registrados; v2, corrigidos após ver os resultados) ficam intactos em `results/` e `results_v2/`. A v3 é declaradamente pós-hoc: foi especificada depois de conhecer v1 e v2.

## 1. O que foi verificado
- Integridade (`audit/INTEGRITY.md`): gabarito igual ao blob congelado; chamadas reconstruídas byte a byte; 1.692 call_ids cobertos por modelo; regra de resposta definitiva escrita e equivalente à usada antes; v1 e v2 reconstruídas com hash idêntico. Nenhuma inconsistência de dados.
- Avaliador (`docs/AUDIT_PROTOCOL.md`, `src/score_v3.py`, 21 testes): três dimensões independentes, entidade, namespace e comportamento; casamento por alias inteiro; sistemas relacionados nunca colapsados; `UNRESOLVED` para o que as regras não decidem; `FORMAT/TRUNCATED` como falha de geração.
- Validação (`audit/review_agreement.md`): 144 respostas seladas por hash e revisadas às cegas por LLM, não por humano independente. Concordância de categoria 92,4% depois de uma única rodada de correção, 83,3% antes; namespace 100% nos 59 itens em que ambos acharam a entidade; comportamento 100%. Os 11 desacordos restantes são cautela do avaliador em casos semânticos.
- Cobertura: as 5.076 respostas têm categoria ou estado `UNRESOLVED` em `results_v3/scored.csv`; as 5.488 leituras têm as três dimensões em `results_v3/readings.csv`.

## 2. O que mudou entre v1, v2 e v3 (`results_v3/DIFF.md`)
- 348 das 5.076 respostas mudaram de categoria da v2 para a v3; 316 em C1 a C4 (7,9%).
- 237 viraram `UNRESOLVED`: 171 eram `OTHER_WRONG` com sobreposição parcial de nome e 36 eram `COMPETING` por casamento de subconjunto, como "Brussels" contado como Brussels Airport. Só 21 das 57 `COMPETING` da v1 sobrevivem ao casamento por alias inteiro.
- 25 viraram `MIXED`: respostas com leitura correta e leitura errada, que a v1 contava como `CORRECT`.
- As 53 `BOTH` da v1 viram 50 `CORRECT`, 1 `MIXED` e 2 `UNRESOLVED`, de acordo com a adjudicação manual da v2.
- 32 sondas P1 truncadas saem de `FAIL` para `FORMAT`.
- Efeito sobre E1 primário, recorte P2, em pontos: Llama C2 +22,2 (v1) → +7,9 (v2) → +7,9 (v3); Llama C3 +20,6 → +11,1 → +15,9; Gemma C2 +21,3 → +14,7 → +16,0; Gemma C3 +8,0 em todas; Qwen C2 −2,8 → −2,8 → 0,0; Qwen C3 −2,8 → −2,8 → +16,7.
- A metade do efeito da v1 em Llama C2 e um quarto em Gemma C2 eram artefato do casamento por subconjunto. A subida de Qwen C3 na v3 vem inteira da regra `MIXED`: com a regra leniente volta a −2,8.

## 3. Defeito de instrumento encontrado nesta auditoria
- A sonda P1 é inutilizável no campo status: os três modelos devolvem status "unknown" em 119, 89 e 120 das 120 sondas, mesmo emitindo um código. O recorte P1 usa só a igualdade do código, como a v1 fazia; o recorte estrito tem zero leituras conhecidas e não é analisável.
- 94 respostas definitivas estão truncadas por laço de repetição; 52 delas são C1 do Llama (21% das 252), o que compromete E3 nesse modelo.

## 4. Resultados (`results_v3/metrics.md`)

### E1, penalidade geral do literal colidente
Diferença de erro colidente menos controle, pares com as duas leituras conhecidas, intervalo de 95% por bootstrap de literais.

| modelo | recorte | C2 | C3 | pares / literais |
|---|---|---|---|---|
| Qwen3 8B | P2 | 0,0 [−33; +31] | +16,7 [−9; +41] | 12 / 11 |
| Qwen3 8B | P1 ∩ P2 | −12,5 [−50; +21] | +4,2 [−25; +29] | 8 / 8 |
| Gemma 3 12B | P2 | +16,0 [−2; +33] | +8,0 [−8; +24] | 25 / 17 |
| Gemma 3 12B | P1 | +37,5 [+24; +52] | −4,2 [−38; +15] | 8 / 7 |
| Llama 3.1 8B | P2 | +7,9 [−3; +21] | +15,9 [+2; +30] | 21 / 16 |
| Llama 3.1 8B | P1 | 0,0 [−14; +13] | +6,3 [−12; +23] | 21 / 17 |
| Llama 3.1 8B | P1 ∩ P2 | +16,7 [+8; +27] | +19,4 [+2; +42] | 12 / 9 |

- Nenhuma célula é estável: o sinal muda com o recorte de familiaridade dentro do mesmo modelo (Llama C2: 0,0 em P1, +16,7 em P1 ∩ P2), com a condição dentro do mesmo recorte (Gemma P1: +37,5 em C2, −4,2 em C3) e com a regra de pontuação (Qwen C3: +16,7 primário, −2,8 leniente, +22,2 com `UNRESOLVED` como acerto).
- Os intervalos têm 25 a 60 pontos de largura. Só efeitos muito grandes seriam detectáveis, e nenhum efeito grande se repete entre modelos.
- Paráfrases: a variante "X is a code in the NS. What does it denote?" é a pior em C2 nos três modelos, com erro de 59% a 92% em colidentes conhecidos; E1 por variante vai de −17 a +33 no mesmo modelo.

### E2, confusão com a leitura concorrente
Leituras colidentes conhecidas por P2, C2 e C3 juntas, 666 respostas nos três modelos.

| modelo | respostas | COMPETING | UNRESOLVED inclinado ao concorrente | OTHER_WRONG | UNKNOWN + AMBIG_FLAG |
|---|---:|---:|---:|---:|---:|
| Qwen3 8B | 150 | 2 | 1 | 29 | 22 |
| Gemma 3 12B | 270 | 0 | 18 | 95 | 54 |
| Llama 3.1 8B | 246 | 1 | 5 | 75 | 0 |

- `COMPETING` estrito: 3 de 666 (0,5%). Os casos: Qwen `C3|VAN|trp/iata|0` e `|1`, "Vanuatu" no cartão de embarque; Llama `C3|OMA|trp/ica2|0`, "Omaha's Eppley Airfield" num transcrito ATC.
- Os 24 `UNRESOLVED` inclinados ao concorrente são entidades erradas no namespace certo, construídas sobre o nome da leitura concorrente: Gemma responde "Aruba Queen Beatrix International Airport" para ARU no IATA (`C2|ARU|trp/iata|0..2`, `C3|ARU|trp/iata|0,1`), "Detroit Metropolitan Wayne County Airport" para DTE (`C2|DTE|trp/iata|0..2`, `C3|DTE|trp/iata|0..2`), "Myanmar Airways International" para MYA na ICAO (`C2|MYA|trp/ica2|0..2`), "Copper" para COP (`C3|COP|fin/tck|0,2`). Concentram-se em 4 literais e num modelo.
- Em leituras não conhecidas, `COMPETING` sobe para 18 de 540 (3,3%) e os inclinados para 35: a leitura concorrente aparece mais quando a pedida não é conhecida.
- O erro dominante em todos os modelos, condições e recortes é `OTHER_WRONG`: uma entidade que não é leitura do literal. Nos controles conhecidos a distribuição é a mesma: Gemma C2 tem 51 `OTHER_WRONG` em 102 respostas de controle.

### Namespace da leitura correta
- Em C2 e C4, quando a entidade está certa, o namespace declarado é o pedido ou equivalente em 100% dos casos nos três modelos.
- Em C3, com contexto indireto, Llama rotula a leitura certa com "ISO 3166-1 alpha-3" em 14 das 72 corretas de colidentes conhecidos, todas em contexto olímpico (BRU, MYA, OMA, VAN, VIE no COI). O modelo acerta o país e nomeia outro sistema. Qwen e Gemma deixam o namespace sem resolver em 8 e 7 casos ("Olympic medal table", "Athletics").
- Não há caso de entidade concorrente com namespace errado em leituras conhecidas; a distinção pedida existe no instrumento e fica vazia nos dados.

### E3, sem namespace (C1)
- Ambiguidade declarada, sem FORMAT: Qwen 42% em colidentes e 41% em controles; Gemma 77% e 66%; Llama 0% e 0%. A condição não distingue literal colidente de controle.
- Apresentar uma única leitura do gabarito: 6,6%, 2,2% e 10,3% dos colidentes, com intervalo superior abaixo de 22%.
- Nos controles que declaram ambiguidade, a leitura do gabarito está entre as citadas em 1 de 65 (Qwen) e 7 de 105 (Gemma). Os modelos hedgeiam com acrônimos inventados, não com as leituras reais.
- Llama: 52 das 252 respostas C1 são laços de repetição truncados; o E3 do Llama não é interpretável.

### E4, registro de autoridade (C4)
- Erro primário de 0% a 3% nos colidentes conhecidos; nenhum `COMPETING`; 2 `UNRESOLVED` em Gemma e Llama são "Text" e "Address" para registros DNS. A condição mede uso do contexto, não memória, e está resolvida.

## 5. Interpretação, separando níveis
- Observação: a escolha da leitura concorrente, sabendo a pedida, é rara (0,5%) e não cresce com a condição indireta de forma consistente.
- Observação: existe um subconjunto pequeno de erros em que a entidade errada é construída sobre o nome da leitura concorrente, no namespace certo. É pós-hoc, concentrado em 4 literais e num modelo.
- Associação estatística: a penalidade geral do colidente não é consistente entre modelos, condições, recortes de familiaridade nem regras de pontuação. Não há associação estável para reportar.
- Hipótese explicativa, não testada: os erros em literais colidentes e em controles vêm da mesma fonte, desconhecimento parcial da tabela de códigos, e a leitura concorrente só entra como material de construção quando o modelo não sabe a pedida. Nada aqui estabelece mecanismo interno.
- A familiaridade medida por P2 é reconhecimento com distrator, não conhecimento: leituras aprovadas em P2 erram de 36% a 64% em C2. P1 ficou sem campo de status utilizável. A interseção P1 ∩ P2 tem 8 a 12 pares e não sustenta inferência.

## 6. Contribuição diante da literatura
- Sedova et al. 2024 já mostram a lacuna entre saber e aplicar, com e sem tipo, e o viés de popularidade. A lacuna medida aqui é a mesma, com gabarito determinístico e controles pareados, mas sem efeito próprio da colisão.
- AmbigDocs e WhoQA cobrem a tipologia de respostas a nomes ambíguos e o efeito do contexto único; C1 e C4 reproduzem esses comportamentos sem acrescentar.
- AmbER e GLADIS, nomes ambíguos em recuperação e desambiguação de acrônimos com contexto, não foram lidos nesta auditoria; pelo que se sabe deles, cobrem a desambiguação por contexto que C3 e C4 tocam. Isso é afirmação de memória, não verificada aqui.
- O que sobra de específico é instrumental: a avaliação em três dimensões com `UNRESOLVED`, o inventário de como modelos nomeiam sistemas de códigos, a inutilidade do status em P1 e a taxa de laços de repetição. São resultados de medição, não de fenômeno.

## 7. Limitações
- Revisão assistida por LLM, não validação humana; 11 casos semânticos ficam `UNRESOLVED` (Silver Lingots, Korean People's Army, Copper, Solomon Islands Airport, TXT (Text)).
- Aliases do gabarito não cobrem o nome da cidade para aeroportos; "Brussels" e "Vienna" ficam `UNRESOLVED`, e isso pesa contra o braço colidente só quando a cidade coincide com a leitura concorrente.
- Controles são únicos apenas entre os sete namespaces elegíveis; 97,6% das strings de 3 letras pertencem a algum sistema.
- Um provedor, uma data, pesos sem precisão declarada; três modelos de 8 a 12 bilhões de parâmetros.
- Os intervalos de E1 não permitem excluir efeitos de 10 pontos em nenhum modelo; a ausência de significância não é prova de ausência.
