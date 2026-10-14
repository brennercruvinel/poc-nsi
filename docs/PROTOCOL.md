# Protocolo da POC: Same Code, Different Worlds

Estado: congelado antes da amostragem. Mudanças depois deste commit entram em "Desvios", com motivo.

## Pergunta
Quando o mesmo literal denota entidades diferentes em namespaces diferentes, o modelo erra a leitura pedida mais do que erra códigos sem leitura concorrente, mesmo conhecendo a leitura pedida?

## Natureza
POC exploratória, com 30 a 50 literais. Não testa hipótese confirmatória. Não atribui mecanismo interno: tudo é comportamental.

## Namespaces elegíveis
- trp/iata, trp/ica2, lng/i31, lng/ioc, fin/i42, fin/tck, cmp/dns.
- O literal precisa ser idêntico byte a byte nos dois namespaces; diferença de caixa exclui o par.
- Código repetido dentro do próprio namespace exclui o literal.
- Leituras de i31 e ioc que apontam o mesmo país contam como uma entidade.

## Itens
- Literal colidente: duas ou mais entidades distintas entre os namespaces elegíveis.
- Leitura: o par (namespace, entidade) de um literal colidente.
- Controle: literal com uma única entidade entre os namespaces elegíveis.
- Sistemas inelegíveis que contêm o literal ficam registrados na coluna other_systems.

## Popularidade estimada
- Pageviews da Wikipedia em inglês do artigo da entidade, 12 meses de 2025-09 a 2026-08, acesso de usuário.
- O artigo vem do Wikidata pela propriedade do namespace: P238, P230, P298, P984, P498 e P5531 para ticker via CIK.
- DNS não tem propriedade; o artigo é atribuído à mão e registrado.
- Código com mais de um item no Wikidata, ou sem artigo, fica fora.

## Amostragem, definida antes de ver popularidade
- Cinco estratos de pares: país contra transporte, moeda contra transporte ou ticker, ticker contra aeroporto, aeroporto contra companhia aérea, DNS contra outro.
- Alvo de 8 literais por estrato, 40 no total, por sorteio com semente 20261014.
- Pré-sorteio de até 60 literais por estrato para buscar popularidade; a seleção final usa só os pré-sorteados.
- Regra de elegibilidade final: toda leitura pontuada tem artigo com pelo menos 1.000 pageviews no período.
- Dentro do estrato, metade equilibrada (razão de pageviews entre as duas leituras mais vistas menor que 3) e metade dominada (razão de 10 ou mais), quando houver.
- No máximo 3 leituras pontuadas por literal, as mais vistas.

## Pareamento dos controles
- Um controle por leitura colidente: mesmo namespace, mesmo comprimento de código.
- Popularidade mais próxima em log10, dentro de fator 2; se não houver, fator 4, marcado.
- Sem reposição; empate resolvido pela semente.
- Leitura sem controle possível segue na análise descritiva e fica fora do contraste principal.

## Gabarito
- Colunas: literal, namespace, entidade, aliases aceitos, qualificadores, fonte, versão do 3char, artigo e pageviews.
- Aliases aceitos: label e aliases do 3char, label e altLabels em inglês do Wikidata, título do artigo.
- Revisão manual de cada linha; sai todo caso sem interpretação segura.
- O arquivo é congelado com sha256 antes da primeira chamada de modelo.

## Condições
- C1, sem namespace: "What does the code X refer to?"
- C2, namespace explícito: "In the <namespace>, what does the code X refer to?"
- C3, contexto indireto: uma frase de uso típico do namespace, sem nomeá-lo, como cartão de embarque, MRZ de passaporte, fatura, cotação, quadro de medalhas ou arquivo de zona DNS.
- C4, registro de autoridade: o registro correto é dado e a pergunta não traz namespace.
- Cada condição tem o texto base e duas paráfrases fixas.
- Todas as condições oferecem as mesmas três saídas: resposta, ambíguo e não sei.

## Sondas de familiaridade, por leitura
- P1, entidade para código: "What is the <namespace> code for <entidade>?", com qualificador de cidade ou país quando preciso.
- P2, código para entidade por reconhecimento: "In the <namespace>, does X denote <entidade>?", junto com um distrator do mesmo namespace.
- P2 passa com "sim" no verdadeiro e "não" no distrator.
- As duas direções são reportadas separadamente, com a concordância entre elas.
- Conhecida no primário quer dizer P2 aprovada; P1 entra como análise secundária.

## Saída e pontuação
- JSON com status (answer, ambiguous ou unknown) e lista de leituras (namespace, entidade).
- A normalização faz casefold, remove acentos e pontuação, e retira termos genéricos de uma lista fixa.
- Os termos genéricos são: airport, international, airlines, airline, inc, corporation, corp, company, co, ltd, plc, the.
- Há casamento quando os tokens centrais de um alias estão todos na resposta.
- Resposta que casa com duas leituras é marcada como casamento ambíguo e revisada.

## Categorias de resposta em C2, C3 e C4
- CORRECT: casa com a leitura pedida.
- COMPETING: casa com outra leitura do mesmo literal.
- AMBIG_FLAG: status ambíguo, mesmo com contexto suficiente.
- UNKNOWN: status não sei.
- OTHER_WRONG: não casa com nenhuma leitura.
- FORMAT: JSON inválido.

## Categorias em C1
- MULTI: marca ambiguidade e lista duas ou mais leituras do gabarito.
- PARTIAL: marca ambiguidade com uma leitura ou nenhuma.
- SINGLE: apresenta uma leitura como única; registra se é a mais vista.
- UNKNOWN, WRONG e FORMAT.
- Em controles, marcar ambiguidade é alarme falso.

## Rótulos interpretativos, só comportamentais
- Desconhecimento: erro em leitura que falhou na sonda.
- Possível interferência: COMPETING em leitura conhecida.
- Erro não atribuído: OTHER_WRONG em leitura conhecida.
- Ambiguidade legítima: só em C1.

## Modelos e execução
- Três famílias: Qwen3 8B, Gemma 3 12B e uma terceira a fixar antes de rodar.
- Temperatura 0, semente 7, modo de raciocínio desligado, saída restrita por esquema JSON quando o provedor aceitar.
- Registro por chamada: modelo, provedor, data, prompt completo e resposta bruta, em JSONL.
- A consulta determinística ao registro resolve 100% de C2 por construção e entra só como referência trivial.

## Análise
- E1: diferença na taxa de erro entre colidente e controle, em leituras conhecidas, para C2 e C3, por modelo.
- E2: proporção de COMPETING entre os erros das leituras colidentes conhecidas.
- E3: em C1, taxa de SINGLE nos colidentes e de alarme falso nos controles.
- E4: em C4, taxa de COMPETING mesmo com o registro.
- Incerteza: bootstrap de 10.000 reamostragens por literal, semente 20261014, intervalo de 95%.
- As paráfrases são medidas repetidas do item; a pontuação do item é a média, e a variação entre paráfrases é reportada.
- Todos os erros saem por categoria, com tamanho de efeito e intervalo.

## Critérios de decisão, exploratórios
- O menor efeito de interesse é 10 pontos percentuais em E1.
- Aprofundar: em pelo menos 2 de 3 modelos E1 é de 10 pontos ou mais na mesma direção, e COMPETING é a maior categoria de erro em E2.
- Reformular: há efeito, mas ele se explica por desconhecimento, por AMBIG_FLAG ou por inconsistência entre modelos.
- Encerrar: em todos os modelos, o limite superior do intervalo de E1 fica abaixo de 10 pontos em C2 e em C3.
- Nos outros casos, inconclusivo.
- Ausência de significância nunca vira rejeição.

## Desvios
Registrados depois do commit do protocolo e antes da primeira chamada de modelo.

1. Terceiro modelo fixado: Llama 3.1 8B Instruct. O OLMo 2 7B não tem provedor no Hugging Face; segue como candidato para uma etapa posterior.
2. Os três modelos rodam no mesmo provedor, featherless-ai, pelo roteador do Hugging Face, para reduzir diferença de motor.
3. Alias que é só o próprio código, ou tem até 3 caracteres, não conta como nome de entidade. Sem isso, repetir o código contaria como acerto.
4. O estrato de país ficou sem literal equilibrado: em todos os elegíveis o país domina em pageviews.
5. Os estratos aeroporto contra companhia aérea e DNS tinham só 5 literais elegíveis cada; depois da revisão ficaram 4 e 3.
6. A revisão manual excluiu 5 leituras de companhia aérea em que o Wikidata aponta outra empresa com o mesmo código; os motivos estão em src/finalize_gold.py.
7. Leituras de DNS receberam aliases manuais, porque o rótulo da IANA é uma descrição.
8. O pedido de pageviews passou a usar um User-Agent com URL de contato, exigido pela Wikimedia; o período e a métrica não mudaram.
