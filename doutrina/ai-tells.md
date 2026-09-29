# AI tells: checklist operacional

Taxonomia de sinais de texto de IA, convertida em checklist executável. Lida obrigatoriamente pela `copy-email` (antes de escrever) e pela `juiz-de-copy` (audita contra este arquivo).

Precedência: abaixo da `doutrina-cliente.md` do workspace e de `doutrina/outbound.md`; acima de preferência de estilo solta.

## O princípio que organiza o arquivo

Os sinais lexicais já são contornados nos dois sentidos: pessoas pararam de usar travessão pra não parecer IA, e IA é instruída a evitá-lo. Passar no Nível 1 não prova nada. Os Níveis 3 e 4 são os que não dá pra fingir, porque exigem posição de verdade, saber o que não se sabe e ter percorrido um caminho próprio pelo material.

**Por isso a auditoria começa pelo Nível 4, não pelo 1.** Um texto que passa no 4 quase sempre passa no resto. Um texto que passa só no 1 é slop bem barbeado.

## Nível 4: especificidade (o sinal mais profundo)

A ausência de particular é o sinal definitivo. Texto humano vem contaminado pelo caminho específico que o autor percorreu: uma data exata, um número não redondo, uma fala literal. Texto de IA entrega a média do corpus com os particulares lixados.

**Teste da particularidade.** Contar os elementos que só quem pesquisou aquela conta ou viveu aquela situação saberia.

- Em email e DM de outbound: **no mínimo 1 por toque**, e o toque 1 abre com ele (ver `outbound.md`, seção `primeira_frase`).
- Em peça longa (página, post, relatório): **no mínimo 3**.

Contam: data ou período exato; número não redondo (39.300 · 17 · D+15); fala literal de alguém; nome próprio verificável da conta (clube, produto, loja, vaga); detalhe que não serve ao argumento e mesmo assim é verdade.

Não contam: número redondo, exemplo genérico, categoria em vez de caso, "muitos clientes", "recentemente".

**Metáfora tem que ser estrutural, não decorativa.** Ou a imagem volta e faz trabalho, ou sai.

## Nível 3: epistêmico (o que exige ter posição)

- **Nunca crava.** Apresenta os dois lados e pousa no meio quando um lado está certo. → O texto tem que ter um lado.
- **Nunca admite ignorância.** Confiança uniforme entre o que sabe e o que confabula. → Nomear o que não se sabe ("pelo que dá pra ver de fora"), sem pedir desculpa.
- **Explica o óbvio e o não óbvio com o mesmo detalhe**, sem modelo do que o leitor já sabe. → Cortar a explicação do que o leitor da área já sabe.
- **Sem risco.** Nenhuma afirmação que custe algo ao autor se estiver errada.
- **Bajulação e validação** costuradas no texto.
- **Viés de resolução.** Ambiguidade fechada cedo demais, história terminando arrumada. → Se a fronteira é borrada na vida real, o texto diz que é borrada.

## Nível 2: estrutura e sintaxe

Reprovação automática:

- **Negação-e-elevação: "não é X, é Y".** O sinal isolado mais forte. Máximo uma por peça; duas ou mais reprovam. Vale pra todas as variantes: "não só X", "X, não Y", "a questão não é A, é B".
- **Tríade por reflexo.** Três adjetivos, três cláusulas, três exemplos sem que a realidade tenha três de nada.
- **Cauda participial que não acrescenta:** ", garantindo consistência", ", permitindo flexibilidade", ", tornando-se uma ferramenta poderosa".
- **Travessão (—)** em qualquer lugar, e o hábito de aparte entre parênteses.
- **Paralelismo limpo demais**, toda ideia com o mesmo formato.
- **Burstiness baixa.** Prosa humana solavanca: uma frase longa, depois uma de quatro palavras. IA fica entre 18 e 24 palavras por frase. Medida em peça de 8+ frases: desvio-padrão do comprimento das frases abaixo de 7, ou nenhuma frase com menos de 6 palavras e nenhuma com mais de 25, reprova. Em email de 70 a 80 palavras, conferir só que as frases não têm todas o mesmo tamanho.

Estrutura de peça:

- Bullet com lead-in em negrito como formato padrão, quando o conteúdo é argumento.
- Header em cima de pouco texto.
- Abertura que reafirma a pergunta; fechamento que reafirma o corpo.
- Seções de comprimento suspeitosamente igual.
- Floreio de conclusão sem informação nova.
- Tabela-resumo que ninguém pediu.

## Nível 1: léxico (o mais fácil e o menos confiável)

Banidos em português: mergulhar (fundo), tapeçaria, testemunho de, sublinhar, crucial, robusto, alavancar, navegar (o cenário), cenário, reino, fomentar, desbloquear, destravar, perfeito/sem atrito (seamless), meticuloso, vibrante, nuançado, intrincado, multifacetado, miríade, ressoar, vitrine, ostentar, revolucionar, transformar, empoderar, disruptivo, "no mundo acelerado de hoje", "virada de jogo".

Banidos em inglês: delve, tapestry, testament, underscore, pivotal, robust, leverage, navigate, landscape, realm, foster, harness, unlock, seamless, meticulous, vibrant, nuanced, intricate, multifaceted, myriad, resonate, showcase, boast, revolutionize, transform, game-changer, empower, disruptive, next-gen.

Hedges banidos: "vale notar que", "é importante destacar", "dito isso", "it's important to note", "it's worth noting", "that said".

Intensificadores inflados: "verdadeiramente", "incrivelmente", "notavelmente", "truly", "incredibly", "remarkably".

## De onde vêm os vícios (útil pra prever o próximo)

**Pré-treino** dá regressão à média: a saída é o centroide de tudo que já foi escrito sobre o tema, e por isso lê como competente e esquecível.

**Ajuste por preferência** dá o resto: hedge, estrutura, concordância, positividade, resolução arrumada e colapso de modo. Colapso de modo é por que os mesmos nomes fictícios, as mesmas cidades e a mesma estrutura em três partes reaparecem.

Some-se a **deriva de formalidade**: tudo escorrega pro registro médio de LinkedIn a menos que seja segurado ativamente. O registro-alvo é a fala do remetente, registrada na `doutrina-cliente.md`.

## Regra de honestidade do auditor

Quem audita comete os mesmos vícios por padrão. Por isso o juiz é obrigado a declarar o que não conseguiu consertar, não só o que consertou. Auditoria que sai limpa em tudo é, ela mesma, um sinal.
