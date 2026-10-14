# Revisão de originalidade (fase 0)

Fontes lidas nas versões originais: Sedova et al. 2024, WhoQA 2024, UA-Bench 2026 e AmbigDocs 2024.
Hier 2025, Smith 2026, AmbER 2021 e GLADIS 2023 foram lidos antes, nas notas 01, 02, 07 e 12.
Não encontrar um benchmark equivalente não prova novidade; a busca foi dirigida, não exaustiva.

## O que já está feito
| Trabalho | O que cobre | Sobreposição com a POC |
|---|---|---|
| Sedova 2024 | 49 nomes ambíguos com duas leituras (empresa e outro tipo); saber contra aplicar; prompt subespecificado contra prompt com tipo; viés para a leitura popular medido por pageviews | Alta: as condições 2 e 3 equivalem ao prompt com tipo e ao prompt por propriedade |
| WhoQA 2024 | Homônimos do Wikidata com contextos conflitantes; até 8 respostas; contexto único dá 91% a 98% | Média: a condição 4 é o caso de contexto único |
| AmbigDocs 2024 | Mesmo nome, documentos diferentes; tipologia completa, parcial, ambígua, fundida e sem resposta | Média: a tipologia serve para pontuar a condição 1 |
| UA-Bench 2026 | Separar incerteza da entrada e do modelo, com tokens de recusa distintos | Média: o formato de saída serve para a condição 1 |
| AmbER 2021, GLADIS 2023 | Viés de popularidade em recuperação; acrônimos | Baixa |

## Limites dos trabalhos, verificados no texto
- Sedova seleciona entidades por intuição, sem controles não ambíguos; o teto é o prompt com tipo.
- Sedova julga só a leitura adotada, por anotação manual; não avalia a identidade factual.
- Sedova usa temperatura 1,0 e uma execução, sem intervalo de confiança.
- WhoQA e AmbigDocs medem raciocínio sobre documentos, não conhecimento paramétrico.
- UA-Bench não usa ambiguidade de entidade; os itens ambíguos vêm de SelfAware e de matemática.

## O que a POC pode acrescentar, a verificar e não a afirmar
1. O literal é um código sem significado lexical; as leituras são pertencimento a registros, não sentidos de palavra.
2. O gabarito de identidade é determinístico, vindo do arquivo da autoridade.
3. Os erros se separam em leitura concorrente, outro erro e abstenção, sem juiz humano nem LLM.
4. Há controles pareados por namespace, comprimento e popularidade, ausentes em Sedova.
5. A familiaridade é medida nas duas direções, por leitura.

## Parecer
- Não é "mesmo desenho, outro domínio" puro: os itens 2 a 4 mudam o que pode ser medido.
- O risco é real: um revisor pode ler como "Sedova para códigos".
- A POC só justifica continuar se mostrar algo que o desenho de Sedova não separa: erro de leitura concorrente acima dos controles, em itens que o modelo conhece.
