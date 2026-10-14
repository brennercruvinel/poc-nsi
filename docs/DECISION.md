# Decisão: ENCERRAR

Esta linha experimental, "modelos de linguagem apresentam erros específicos ao interpretar o mesmo identificador em namespaces diferentes, mesmo conhecendo a leitura pedida", é encerrada com os dados existentes.

## Evidências auditadas
1. Confusão específica com a leitura concorrente, em leituras conhecidas: 3 de 666 respostas nos três modelos (0,5%). Com a contagem mais generosa, incluindo entidades erradas construídas sobre o nome do concorrente, 27 de 666 (4,1%), concentradas em 4 literais e num modelo. Não é o erro dominante em nenhuma célula; o dominante é uma entidade que não pertence a nenhuma leitura do literal, nos colidentes e nos controles.
2. Penalidade geral do colidente: muda de sinal ou some ao trocar o recorte de familiaridade dentro do mesmo modelo, a condição dentro do mesmo recorte e a regra de pontuação. Metade do efeito da v1 no Llama em C2 era artefato de casamento por subconjunto; o efeito do Qwen em C3 depende só de como se pontua resposta com leituras mistas. Nada se repete em dois modelos na mesma direção com intervalo fora de zero.
3. Os comportamentos que se repetem entre modelos e paráfrases já estão na literatura: lacuna entre reconhecer e aplicar (Sedova), hedging indiferente à ambiguidade real (AmbigDocs, WhoQA), resolução total com o registro no contexto (C4).
4. Com o material existente, a investigação é inviável: 8 a 25 pares conhecidos por modelo, intervalos de 25 a 60 pontos, sonda P1 sem status utilizável e 21% de C1 do Llama truncado. Ampliar a amostra não é justificado por ausência de significância, e foi excluído do escopo.

## Por que não APROFUNDAR
Não há sinal relevante, interpretável e robusto às correções. O único padrão novo, erro construído sobre o nome da leitura concorrente no namespace certo, é pós-hoc, pequeno e de um modelo.

## Por que não REFORMULAR
A reformulação proposta na sessão anterior, "literais colidentes têm penalidade geral de acerto", foi testada aqui com o avaliador corrigido e três recortes de familiaridade e não se sustenta. Os comportamentos relevantes que sobraram são instrumentais, não uma pergunta científica sobre o fenômeno.

## O que permanece válido e reutilizável
- O censo de colisões do 3char é independente desta POC e não é afetado.
- O avaliador em três dimensões com estado `UNRESOLVED`, a tabela de canonização de nomes de sistemas e os inventários servem para qualquer avaliação futura de códigos curtos.
- Os achados de medição: status de P1 inutilizável sob esquema JSON, laços de repetição em C1, e o peso das respostas com leituras mistas na métrica.
- A observação exploratória de contaminação pelo nome do concorrente fica registrada como possibilidade, com os call_ids, sem virar tese.

## Implicações
- Nenhuma afirmação de interferência entre namespaces deve ser feita a partir destes dados.
- Qualquer retomada exige outra pergunta, outro desenho de familiaridade e um gabarito com aliases revisados antes de qualquer chamada, e não está autorizada por esta decisão.
