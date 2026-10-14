# Protocolo da auditoria v3

Estado: congelado antes da pontuação v3. Toda a avaliação v3 é pós-hoc: foi especificada depois de ver os resultados v1 e v2 e por isso não substitui os critérios do `docs/PROTOCOL.md`; ela mede o que os dados já coletados permitem demonstrar.

## Contrato
- Entrada: `data/gold.csv` (sha256 9048f3d7), `runs/calls.jsonl`, `runs/*.jsonl`. Nenhum é alterado.
- Nenhuma chamada nova a modelo. Nenhuma alteração de `results/` e `results_v2/`.
- Saídas: `results_v3/`, `audit/`, `docs/AUDIT_REPORT.md`, `docs/DECISION.md`, `src/score_v3.py`, `tests/`.
- Uma especificação do avaliador, uma rodada de correção instrumental no máximo, uma reavaliação integral, um relatório.
- Resposta definitiva por call_id: o último registro com http 200; se não houver, o último registro (ver `audit/INTEGRITY.md`).

## Unidade de identidade
Uma identidade é o par (namespace, entidade). Nome de entidade coincidente não basta: a resposta "Oman" para o código OMA é correta no namespace do COI e concorrente no namespace de designadores da ICAO, onde OMA é a Oman Air.

## Três dimensões, avaliadas de forma independente

### 1. Entidade, por leitura devolvida
Valores: `CORRECT`, `COMPETITOR`, `OTHER`, `UNRESOLVED`.

Aliases ativos de uma leitura do gabarito: label mais aliases, excluídos os que não são nomes:
- alias cuja forma normalizada é o próprio literal;
- alias com até 3 caracteres normalizados, salvo palavra de 3 letras com inicial maiúscula e resto minúsculo (Lek, Jay);
- alias só com maiúsculas e até 4 caracteres alfanuméricos (códigos ISO, ICAO, IATA, símbolos de moeda);
- a string `null` e os genéricos `peso`, `dollar`, `dollars`, que casariam com qualquer moeda da família.
A lista aplicada a cada linha do gabarito sai em `audit/alias_policy_applied.csv`.

Normalização: NFKD sem marcas combinantes, casefold, tudo que não é letra ou dígito vira espaço, espaços colapsados.

Casamento forte de uma string de entidade `e` com um conjunto de aliases:
- exato: `e` igual a um alias;
- frase: um alias com 2 ou mais tokens aparece em `e` como sequência contígua de tokens;
- frase curta: um alias de 1 token aparece em `e` e os demais tokens de `e` estão todos na lista de envoltório `WRAPPER` ou são o próprio literal. `WRAPPER` tem artigos e qualificadores de país (the, of, a, an, republic, state, sultanate, kingdom, nation, country, island, islands), rótulos de tipo (currency, code, record, type, dns) e sufixos societários (inc, incorporated, corp, corporation, co, company, ltd, limited, plc, llc). Palavras que mudam o tipo da entidade, como airport, airlines, airline ou air, ficam fora: "Aruba Airlines" nunca casa com Aruba.
Casamento parcial: `e` compartilha ao menos um token não genérico com um alias, sem casamento forte. Tokens genéricos: os 12 do protocolo original (airport, international, airlines, airline, inc, corporation, corp, company, co, ltd, plc, the) mais of, record, dns, currency, code, dollar, peso.

Decisão por leitura:
- forte com a pedida e nenhum forte com concorrente: `CORRECT`;
- forte com um concorrente e nenhum forte com a pedida: `COMPETITOR`, com o namespace concorrente registrado;
- forte com os dois lados, ou só parciais de qualquer lado: `UNRESOLVED`, com a evidência (`both`, `partial_target`, `partial_competitor`, `partial_both`);
- entidade vazia, igual ao código ou com até 3 caracteres: `UNRESOLVED`, evidência `no_entity`;
- nenhum token compartilhado: `OTHER`.
Nunca se reduz um alias a um subconjunto de palavras: "Aruba Airlines" não casa com Aruba, "Oman Air" não casa com Oman, "Brussels" não casa com Brussels Airport.

### 2. Namespace, por leitura devolvida
Valores: `CORRECT`, `EQUIVALENT`, `INCORRECT`, `UNRESOLVED`.
- O valor original de `system` é preservado em `system_raw`; `system_norm`, `ns_canon`, `ns_rule` e `ns_confidence` ficam em colunas separadas.
- A canonização usa as regras ordenadas de `data/namespace_canon.json`; a primeira que casa vence; sem regra, `UNRESOLVED`. O mapa aplicado a todas as strings observadas está em `audit/system_map_applied.csv`.
- `CORRECT`: canônico igual ao pedido com confiança alta. `EQUIVALENT`: canônico igual ao pedido com confiança média ou baixa, ou nome de organização (`org/iata`, `org/icao`) que neste estudo só possui o sistema pedido. `INCORRECT`: canônico diferente do pedido. `UNRESOLVED`: sem canônico.
- Sistemas relacionados nunca colapsam: ISO 3166-1 alpha-3 pedido COI é `INCORRECT`; IATA pedido ICAO é `INCORRECT`; alpha-2 pedido alpha-3 é `INCORRECT`; NYSE e Nasdaq pedido "US stock ticker" é `EQUIVALENT`, porque são bolsas dentro da lista da SEC, não outro sistema de códigos.
- Em C1 não há namespace pedido: o namespace de cada leitura é avaliado contra o namespace da leitura do gabarito com que a entidade casou.

### 3. Comportamento, por resposta
Valores: `SINGLE` (status answer, 1 leitura), `MULTI` (status answer, 2 ou mais), `AMBIGUOUS` (status ambiguous), `ABSTAIN` (status unknown), `FAILURE` (falha de geração).
- `FAILURE` tem subtipo: `TRUNCATED` (finish_reason length e JSON inválido), `INVALID_JSON`, `SCHEMA` (status fora do enum ou readings fora de lista).
- As 94 respostas definitivas truncadas são `FAILURE/TRUNCATED`. Entram nas métricas principais como erro e saem numa análise de sensibilidade, reportada à parte, com atenção a C1 do Llama (52 das 252).

## Categoria derivada por resposta, para comparação com v1 e v2
C2, C3 e C4: `FORMAT`, `UNKNOWN`, `AMBIG_FLAG`, `CORRECT` (toda leitura `CORRECT`), `COMPETING` (alguma `COMPETITOR`, nenhuma `CORRECT`), `MIXED` (alguma `CORRECT` com alguma `COMPETITOR`, `OTHER` ou `UNRESOLVED`), `UNRESOLVED` (nenhuma `CORRECT` nem `COMPETITOR`, alguma `UNRESOLVED`), `OTHER_WRONG` (só `OTHER`).
- Leituras de respostas `AMBIGUOUS` e `ABSTAIN` são avaliadas e registradas, mas a categoria é `AMBIG_FLAG` ou `UNKNOWN`.
- `ns_of_correct`: namespace da leitura correta, quando existe. Permite separar entidade correta com namespace errado de entidade concorrente com namespace errado.

C1: `MULTI` (2 ou mais leituras do gabarito casadas fortemente), `PARTIAL` (status ambiguous com menos de 2), `SINGLE` (status answer com exatamente 1 casada), `UNRESOLVED` (nenhuma casada, alguma parcial), `WRONG`, `UNKNOWN`, `FORMAT`. Em controles, declarar ambiguidade é registrado como `AMBIG_DECLARED`, não como alarme falso: o controle é único só entre os sete namespaces elegíveis.

P1 e P2 ficam como na v1: P1 passa quando o código devolvido é o literal; P2 passa com "yes" no verdadeiro e "no" no distrator.

## Métricas
- Acerto primário: categoria `CORRECT`. Sensibilidades: (a) estrito, `CORRECT` com namespace `CORRECT` ou `EQUIVALENT`; (b) leniente, `CORRECT` ou `MIXED` ou `AMBIG_FLAG` com leitura correta; (c) sem `FORMAT` no denominador; (d) `UNRESOLVED` contado como acerto, limite superior.
- E1: erro colidente menos erro controle, por par, em pontos percentuais, bootstrap de 10.000 reamostragens por literal, semente 20261014. Três recortes de familiaridade: P2, P1 e P1 ∩ P2, cada um exigindo os dois membros do par conhecidos. Pares e literais efetivos sempre reportados.
- E2: distribuição de categorias nas leituras colidentes conhecidas, separando `COMPETING`, `UNRESOLVED` com evidência de concorrente, `OTHER_WRONG`, `UNKNOWN`, `AMBIG_FLAG` e `FORMAT`.
- E3: distribuição de categorias de C1 em colidentes e controles, com `FORMAT` à parte.
- E4: categorias em C4; o registro está no prompt, então E4 mede uso do contexto, não memória.
- Sensibilidade às três paráfrases: erro por variante, por modelo e condição.

## Conjuntos de desenvolvimento e validação
- Desenvolvimento: tudo que foi usado para escrever as regras: os inventários, os casos de `data/both_adjudication.json`, os exemplos citados em `docs/REPORT.md` e as respostas inspecionadas durante a especificação. Isso cobre os literais ARU, OMA, BRU, JEY, LYB, A, ALL, JMD, FIJ, MYA, VAN e DTE. Toda chamada cujo item ou literal pertence a esse conjunto é de desenvolvimento.
- Validação: amostra estratificada sorteada entre as demais chamadas, registrada com hash antes da revisão. A revisão é assistida por LLM e não é validação humana independente.
- A revisão não vê a categoria automática. Depois da concordância, cabe no máximo uma rodada de correção, testada no conjunto de desenvolvimento; a amostra de validação não é reutilizada para ajuste.

## Limites
- Sem v4, sem chamadas novas, sem ampliação do gabarito, sem novas hipóteses.
- Casos que não se resolvem com estas regras ficam `UNRESOLVED` e entram nas limitações.

## Critérios de aceitação
- Testes determinísticos passando, com casos positivos e negativos.
- As 5.076 respostas com categoria ou estado `UNRESOLVED`.
- Transições v1 → v2 → v3 rastreáveis por call_id com a regra responsável.
- `results_v3/` reconstruível do zero com hashes idênticos.
