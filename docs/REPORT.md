# Relatório da POC: Same Code, Different Worlds

Exploratória. Protocolo congelado no commit 02d6bb5 e gabarito no commit 6197b9e (sha256 9048f3d7), ambos antes da primeira chamada de modelo.

## Casos
- 31 literais colidentes, 67 leituras colidentes e 53 controles pareados, em 5 estratos.
- Estratos: país (8), moeda (8), ticker contra aeroporto (8), aeroporto contra companhia aérea (4) e DNS (3).
- Os controles têm o mesmo namespace e o mesmo comprimento, com popularidade dentro de fator 2; dois usaram fator 4.
- A revisão manual excluiu 5 leituras em que o Wikidata aponta outra empresa com o mesmo código.

## Execução
- Modelos: Qwen3 8B, Gemma 3 12B Instruct e Llama 3.1 8B Instruct, no provedor featherless-ai via roteador do Hugging Face.
- 1.692 chamadas por modelo, temperatura 0, sem falhas de provedor no fim.
- Ficaram cortadas, por laço de repetição: Qwen3 com 4, Gemma com 31 (todas em P1) e Llama com 59 (52 delas em C1).

## Correção do instrumento, feita depois de ver os resultados
- A categoria BOTH só podia ocorrer no braço colidente e inflava o erro dele; a revisão manual prevista no protocolo resolveu 52 de 53 como CORRECT.
- A regra de alias descartava nomes curtos reais, como "Lek"; a v2 descarta só aliases com cara de código.
- As versões v1 e v2 estão em results e results_v2. A decisão usa a v2.

## Resultados, pontuação v2
| Modelo | P1 | P2 | Concordância P1/P2 | E1 em C2 | E1 em C3 |
|---|---:|---:|---:|---:|---:|
| Qwen3 8B | 29,2% | 36,7% | 80,8% | -2,8 [-39,4; 28,6] | -2,8 [-33,3; 23,8] |
| Gemma 3 12B | 24,2% | 65,8% | 46,7% | 14,7 [-2,8; 32,1] | 8,0 [-8,0; 24,2] |
| Llama 3.1 8B | 58,3% | 59,2% | 67,5% | 7,9 [-3,6; 21,1] | 11,1 [-1,6; 25,0] |

E1 é a diferença de erro, em pontos percentuais, entre colidente e controle, só em pares conhecidos pela P2. Os pares conhecidos foram 12, 25 e 21, em 11, 17 e 16 literais.

| Modelo | COMPETING em leituras conhecidas, C2 | idem, C3 | COMPETING em leituras não conhecidas, C2 | idem, C3 |
|---|---:|---:|---:|---:|
| Qwen3 8B | 0/75 | 2/75 | 11/126 | 10/126 |
| Gemma 3 12B | 7/135 | 3/135 | 2/66 | 0/66 |
| Llama 3.1 8B | 1/123 | 3/123 | 9/78 | 9/78 |

- A maior categoria de erro, em todos os modelos e condições, é OTHER_WRONG: entidade errada que não é leitura do literal.
- C4, com o registro correto: erro de 0%, 1,5% e 5,7% nos colidentes, e 0% nos controles; nenhum COMPETING.
- C1: o modelo marca ambiguidade com a mesma frequência em colidentes e controles. Qwen3 marca 41% e 41%; Gemma, 77% e 66%; Llama, 0% e 0%.
- C1: apresentar uma leitura como única foi raro, de 3% a 11% das respostas nos colidentes.
- Paráfrase: a forma "X is a code in the NS. What does it denote?" é a pior nos três modelos.

## Exemplos
- C2, COMPETING, Qwen3: pedido o COI, BRU virou "Belgium" e "Brussels"; o gabarito é Brunei.
- C3, AMBIG_FLAG, Qwen3: num MRZ de passaporte, JEY foi tratado como número de passaporte ambíguo; o gabarito é Jersey.
- C2, UNKNOWN, Qwen3: ARU no COI virou "não sei"; o gabarito é Aruba.
- C1, SINGLE, Qwen3: BRU sem contexto virou só "Brussels Airlines".
- C2, OTHER_WRONG, Llama: LYB no IATA virou "Lybia International Airport"; o gabarito é Edward Bodden Airfield.
- C4, OTHER_WRONG, Gemma: com o registro "A is a host address", respondeu "Address", que a regra não aceita.

## Análise posterior, exploratória
- Hipótese: as respostas erradas são montadas a partir das letras do código.
- Resultado: não se sustentou. A coerência com as letras foi de 25%, 19% e 48% nas erradas, contra 37%, 36% e 44% nas certas.

## Limitações
- O critério de conhecimento é fraco: leituras aprovadas na P2 ainda erram de 36% a 64% em C2.
- Os intervalos de E1 têm cerca de 20 pontos de meia largura; só efeitos grandes seriam detectáveis.
- Os controles não são únicos no mundo: 97,6% das strings de 3 letras já pertencem a algum sistema. Por isso, marcar ambiguidade num controle não prova alarme falso.
- A remoção de termos genéricos faz o nome da cidade casar com o aeroporto, como Brussels.
- O DNS ficou com 3 literais, sem controle e com pontuação frágil.
- O provedor não declara a precisão dos pesos; o resultado vale para esse provedor nessa data.
- O OLMo 2 não rodou, porque não tem provedor no Hugging Face.

## Parecer
- Pelos critérios congelados, o resultado não é "aprofundar": nenhum modelo tem COMPETING como erro principal, e só um modelo por condição passa de 10 pontos em E1.
- Também não é "encerrar": os limites superiores de E1 passam de 10 pontos em Gemma e Llama.
- A decisão é reformular. O efeito é inconsistente entre modelos, e a leitura concorrente aparece mais quando o modelo não conhece a leitura pedida (Qwen3 e Llama), o que aponta desconhecimento, não interferência.
- A escolha da leitura concorrente sabendo a pedida existe, mas é rara: de 0 a 5% das respostas em leituras conhecidas.
- O que sobra de sinal é uma possível penalidade geral de erro em literais colidentes, de 8 a 15 pontos em dois modelos, não explicada por leitura concorrente.

## Próximo passo
Reformular a pergunta para "literais colidentes têm uma penalidade geral de acerto, e por quê?" e calcular o tamanho de amostra para um intervalo de 5 pontos, antes de qualquer nova chamada. Pela largura atual, isso exige cerca de 13 vezes mais pares conhecidos.
