---
name: juiz-de-copy
description: Juiz de copy de outbound com poder de veto. Avalia cada toque da sequência de email (04-sequencia-email.md) e o prompt ou a mensagem da Syndie contra doutrina/outbound.md, doutrina/escrita.md, doutrina/ai-tells.md e a doutrina-cliente do workspace; quatro papéis críticos e o caçador de slop dão nota de 1 a 10, o caçador veta item grave; revisa até 3 rodadas, passa por uma leitura fria de olhos sem histórico e declara por escrito o que não conseguiu consertar. Use sempre depois da copy-email e da syndie-flow-builder, antes do gate H2, ou quando o operador disser "roda o juiz", "julga essa copy", "nota pro email", "avalia o prompt da Syndie", "passa no juiz". Nenhuma copy chega ao operador sem passar aqui.
---

# juiz-de-copy

A régua de qualidade da etapa E5. Existe pra que o operador não precise policiar a copy no gate H2: ele recebe um texto que já passou pela doutrina, com nota, motivo de cada reprovação e a lista honesta do que ficou ruim.

O juiz avalia forma, honestidade e aderência à doutrina, e revisa o texto. **Ele não inventa fato novo.** Toda frase da versão revisada se apoia no que a peça já tinha ou no material permitido: a `primeira_frase` e as evidências da conta, as frases autorizadas da doutrina-cliente, a oferta, o master copy e as extrações de voz do cliente. Se o conserto exige um fato que não está nesse material, o juiz não conserta: declara.

## Antes de avaliar: o que ler

- `doutrina/outbound.md`, `doutrina/escrita.md`, `doutrina/ai-tells.md` e `doutrina/producao-com-agentes.md`.
- `estrategia/doutrina-cliente.md`. Sem ela o juiz não sabe o que é número autorizado, qual é a voz do remetente nem quais fórmulas são fixas: pare e peça.
- `estrategia/ofertas/<oferta>.md` e `estrategia/master-copy/<oferta>.md`.
- `contexto/extracoes/voz-do-cliente-*.md`, se houver.
- `rodadas/<rodada>/02-validacao.xlsx` (ou os vereditos em JSON): evidências por conta e `adversarial.fatos_refutados`.
- `rodadas/<rodada>/03-contatos.csv`: pra checar as colunas das variáveis e ler frases com valores reais.
- Pra Syndie: `schemas/syndie-flow.schema.json`, `schemas/syndie-upload.schema.md` e `adapters/syndie/README.md`, se existir.

## O que se avalia

| Peça | Unidade que recebe nota | De onde vem |
|---|---|---|
| Email | Cada toque (`## D1`, `## D4`, `## D8`, `## D13`), com o assunto. Com variante por nível, `## D1 · decisor` e `## D1 · champion` são duas unidades, cada uma com a sua nota; o decisor é julgado pela régua de dono (2 a 3 frases, receita e risco, nada operacional) e o champion pela de quem opera (tempo e trabalho manual, nada de ROI abstrato) | `rodadas/<rodada>/04-sequencia-email.md`, da `copy-email` |
| Syndie | Cada nó com texto: prompt (`customGuidelines`), mensagem fixa (`message`), comentário (`customComment`) | `rodadas/<rodada>/04-syndie-flow.json` ou o rascunho entregue pela `syndie-flow-builder` |

A **peça** é a sequência inteira (email) ou o fluxo inteiro (Syndie). Alguns itens contam na peça, não no toque: negação-e-elevação, repetição de ângulo entre toques, proporção você × nós da sequência.

Fórmulas fixas da doutrina-cliente (saudação, fecho, assinatura, pedido de horário, encerramento) entram literais. O juiz confere que estão literais e no toque permitido, mas não as reescreve nem tira nota por voz nelas.

## Os papéis

Cada papel dá nota de 1 a 10 por unidade e uma crítica de 1 a 2 linhas que cita o trecho e diz o que trocar. "Ficou bom" não é crítica.

1. **Comprador cético.** O prospect do segmento, lendo no celular entre duas reuniões, depois de 40 emails de vendedor na semana. Eu entendi na primeira leitura? Tem alguma coisa aqui sobre a minha operação que eu não sabia que alguém sabia? A pergunta se responde com um sim barato? Eu responderia?

   **Quando houver `contexto/extracoes/voz-do-cliente-*.md`, o comprador cético é sintético: construído a partir dela, não imaginado.** Antes da primeira rodada de notas, monte um perfil curto a partir das citações (como o comprador descreve o problema, as palavras que ele usa, o que o irrita, do que ele desconfia, o que o faz adiar a decisão) e avalie cada toque em primeira pessoa, com ceticismo real. Regras:
   - toda reação do comprador aponta a citação que a sustenta (tema e reunião de origem). Reação sem fonte na extração não entra;
   - a linguagem que conta é a do comprador na extração, nunca a do material de marketing do cliente;
   - se a copy usa palavra que nenhum comprador usou pra dor, ou promete o que ele disse desconfiar, a crítica cita a fala dele;
   - com o nível do toque (`## D1 · decisor` ou `· champion`), o comprador é o daquele nível; se a extração não tem fala de decisor, diga isso na crítica em vez de inventar a voz dele;
   - extração com poucos dados (menos de 3 reuniões usadas) vira perfil fraco: declare isso no relatório e não dê veto por ele.

   Sem extração, o papel volta ao comprador imaginado do segmento, e o relatório diz que foi assim.
2. **Editor de corte.** Dá pra cortar 20% sem perder nada? Uma ideia por frase? Parágrafos de até 2 frases? Tem comentário sobre o próprio email? D1 dentro de 70 a 80 palavras? As frases variam de tamanho?
3. **Checador de fatos.** Toda frase sobrevive a "como você sabe?". Número, âncora, preço e claim estão autorizados na doutrina-cliente, na forma e no toque autorizados. Nenhum fato refutado pela verificação adversarial. Nenhum asset prometido que não existe. Nenhuma motivação atribuída. Nenhuma ausência afirmada sem evidência.
4. **Estrategista de sequência.** O toque cumpre a sua função (D1: fato, dor, valor, pergunta; D4: prova colada na dor; D8: recurso ou ângulo novo; D13: saída honesta)? Entrega valor mesmo sem resposta? Traz substância nova em relação aos anteriores? O pedido de horário está só onde a doutrina permite? Na Syndie: o gancho é o problema da pessoa, o primeiro toque só abre conversa, o CTA é um sim barato.
5. **Caçador de slop, com veto.** Audita contra `doutrina/ai-tells.md` **do Nível 4 pro Nível 1**, porque passar no léxico não prova nada. Também é dono da lista de vetos abaixo. Dá nota como os outros, e um veto reprova a unidade independente da média.

## Rubrica

Cada item é checado em cada unidade. **Veto** reprova a unidade na hora. **Reprovado** baixa a nota do papel responsável e precisa ser consertado ou declarado.

| # | Item | Fonte | Papel | Tipo |
|---|---|---|---|---|
| R1 | **Particularidade:** pelo menos 1 elemento que só quem pesquisou a conta ou o segmento saberia (data, número não redondo, nome próprio verificável, expressão literal do comprador). No D1 vem da `primeira_frase` | ai-tells, Nível 4 | caçador | reprovado |
| R2 | **Teste da intercambiabilidade:** trocar a empresa por outra da mesma vertical. Frase que continua valendo sai ou é reescrita. O fallback de `primeira_frase` é avaliado como abertura de segmento, não de conta | outbound | caçador | reprovado |
| R3 | **Nível 3:** o texto tem um lado; nomeia o que não sabe com no máximo um hedge honesto; sem bajulação; sem resolução arrumada demais | ai-tells | caçador | reprovado |
| R4 | **Frase banida de abertura** ("Vi que", "Notei que", "Percebi que", "Reparei que", "<nome> aqui", "espero que esteja tudo bem", "passando pra", "vi seu perfil", "dei uma olhada no site") | outbound | caçador | **veto** |
| R5 | **Frase banida no corpo** ("a gente ajuda empresas como a sua", "somos uma startup que", "trocar uma ideia" quando é pitch, "grande fã do trabalho de vocês"), comentário meta, P.S. que se desculpa | outbound | caçador | reprovado |
| R6 | **Uma pergunta só, e o toque termina nela.** Conta como pergunta toda frase interrogativa e todo pedido de resposta ("me diz se faz sentido"). Mais de uma é veto; uma só que não fecha o toque é reprovado | outbound | estrategista | **veto** (mais de uma) |
| R7 | **Você > nós:** contar as frases sobre o prospect (a operação, a dor, o time, os números dele) e as frases sobre o remetente (nós, a gente, o produto, os clientes do remetente). Frases neutras não contam. No toque: prospect ≥ remetente (o D4 pode empatar). Na sequência: prospect > remetente. Registrar a contagem como `P:R` | outbound | comprador | reprovado |
| R8 | **Valor no próprio toque:** o email vale algo sem resposta. Toque que só retoma o anterior reprova | outbound | estrategista | reprovado |
| R9 | **Fallback legível:** ler cada frase com cada fallback da tabela. Variável usada sem linha na tabela, fallback vazio ou frase que quebra com o fallback é veto | sequencia-email.schema | checador | **veto** |
| R10 | **Número, âncora, preço, claim ou asset** só se autorizado na doutrina-cliente, na forma e no toque autorizados. Fato refutado pela adversarial ou sem fonte entra aqui | escrita, outbound | checador | **veto** |
| R11 | **Pedido de horário** só nos toques finais e na fórmula da doutrina-cliente. A embalagem de vendedor ("call rápida de 15 minutos", "faz sentido a gente conversar?") reprova em qualquer toque | outbound | estrategista | reprovado |
| R12 | **Sem link no D1**, sem Markdown no corpo | copy-email | editor | reprovado |
| R13 | **Pitch por negação:** a ausência descrita é exatamente o que o remetente vende | outbound | caçador | **veto** |
| R14 | **Motivação atribuída** a uma decisão do prospect | outbound | checador | **veto** |
| R15 | **Alfinetada** na escolha recente do prospect, case do fornecedor dele devolvido, tensão com tom de auditoria, culpa no time em vez da ferramenta, máxima de palestra | outbound, escrita | comprador | reprovado |
| R16 | **Negação-e-elevação** ("não é X, é Y" e variantes) duas ou mais vezes na peça | ai-tells, Nível 2 | caçador | **veto** |
| R17 | **Nível 2:** tríade por reflexo, cauda participial vazia, paralelismo limpo demais, frases todas do mesmo tamanho | ai-tells | editor | reprovado |
| R18 | **Travessão (U+2014)** em qualquer lugar: assunto, corpo, spintax, fallback, prompt | escrita | caçador | **veto** |
| R19 | **Nível 1:** léxico banido, hedges, intensificadores, jargão de SaaS | ai-tells, escrita | caçador | reprovado |
| R20 | **Registro:** email sem "pra" e "tá" (salvo doutrina-cliente); nunca corporativo; saudação e fecho literais da doutrina-cliente | escrita | editor | reprovado |
| R21 | **Acentuação completa** | escrita | editor | reprovado |
| R22 | **Spintax** só em saudação e transições; cada opção passa em todos os itens sozinha | sequencia-email.schema | editor | reprovado |
| R23 | **Sequência:** D4, D8 e D13 não repetem ângulo nem pergunta de toques anteriores | outbound | estrategista | reprovado |
| R24 | **Syndie:** `customGuidelines` com mais de 1000 caracteres, ou qualquer variável fora de `first_name`, `last_name`, `company`, `title`, ou referência a campo de CSV (`primeira_frase`, "se o campo estiver vazio") | syndie-flow.schema, outbound | checador | **veto** |
| R25 | **Syndie:** nota de convite dentro do limite do schema; prompt descreve o que a mensagem precisa ser (fato específico + tensão) e deixa a IA achar o fato; o gancho é o problema, nunca o produto; nada de demo ou call no primeiro contato | outbound, LinkedIn | estrategista | reprovado |

### A lista de vetos

Qualquer um destes reprova a unidade, com qualquer média:

1. travessão (R18);
2. frase banida de abertura (R4);
3. mais de uma pergunta no toque (R6);
4. número, âncora, preço, claim ou asset não autorizado, ou fato refutado (R10);
5. merge sem fallback ou que quebra com o fallback (R9);
6. pitch por negação (R13);
7. motivação atribuída (R14);
8. prompt da Syndie acima de 1000 caracteres ou com variável não nativa (R24);
9. negação-e-elevação 2 ou mais vezes na peça (R16).

Os vetos 1, 3, 5 e 8 são mecânicos: o juiz sempre consegue consertar e nunca entrega com eles abertos. Os outros são editoriais: se o conserto exigir fato novo, a unidade sai com **veto aberto**, declarado, e o operador decide no H2.

## Limiar de aprovação

**Uma unidade é aprovada quando a média das 5 notas é ≥ 8, nenhum papel dá menos de 6 e não há veto.** A nota da sequência (a que vai pra linha de versão do arquivo) é a média das unidades.

Por que 8 e não o 9 que a base usava pra post:

- **Tem gate humano logo depois.** O post saía do conselho direto pra publicação; aqui o operador lê tudo no H2 e o `ciclos.md` mede o quanto ele mexe. O juiz não precisa ser a última palavra.
- **Email curto satura a nota.** Em 70 a 80 palavras há pouco onde ganhar ponto; exigir 9 de cinco papéis em quatro toques faz quase toda sequência gastar as 3 rodadas em ajuste cosmético, e reescrita cosmética é onde a copy de agente piora.
- **O grave não passa pela média.** Tudo que queima a sequência está na lista de vetos, que vale com qualquer nota.
- **O mercado é o juiz final.** A regra de copy se confirma por reply positivo (`_protocolo.md`), não por nota interna.

O piso de 6 por papel impede que quatro notas altas escondam um papel que acha o toque ruim de verdade.

O limiar é `[hipótese]`. A `loop-de-licoes` o recalibra: se o operador mantiver 80% ou mais das frases sem edição em 2 rodadas seguidas, ele fica; se editar muito do que o juiz aprovou, o candidato é subir pra 8,5.

## Mecânica

### Rodada 0: checagem mecânica

Antes de qualquer papel ler, confira e corrija direto (não conta como rodada):

- travessão (U+2014) em qualquer lugar;
- `{{variável}}` fora da tabela `## Variáveis`, ou linha da tabela sem fallback;
- número de `?` por toque e posição do último;
- palavras do D1 (com uma `primeira_frase` real de tamanho mediano) e URL no D1;
- palavras sem acento (voce, nao, esta, sao, tambem, ja, ate, entao, operacao);
- "pra" e "tá" no email;
- Syndie: caracteres de cada `customGuidelines` e de cada nota de convite; variáveis usadas. Se o JSON existir, rode `python scripts/validate_syndie_flow.py rodadas/<rodada>/04-syndie-flow.json`; saída diferente de 0 é conserto obrigatório.

### Rodadas 1 a 3: avaliação e revisão

1. O caçador de slop lê primeiro, do Nível 4 pro 1, e marca os vetos. Depois os outros quatro papéis.
2. Para cada unidade: 5 notas, média, vetos, itens reprovados com o trecho e o motivo.
3. **Tudo aprovado:** encerre as rodadas.
4. **Alguma unidade reprovada:** revise só as reprovadas. Unidade aprovada não se mexe, a menos que a revisão de outra crie repetição com ela.
5. **Regras da revisão:**
   - só material permitido; nenhum fato, número, nome ou asset novo;
   - fórmulas fixas da doutrina-cliente ficam literais;
   - cada unidade revisada volta por todos os itens da rubrica, não só pelo que motivou a revisão;
   - se o conserto precisa de matéria-prima que não existe (prova autorizada, particularidade do segmento, asset), não escreva em volta: anote em "Não consegui consertar" o que falta e onde isso deveria estar (doutrina-cliente, master copy, extrações).
6. **Depois da 3ª rodada sem aprovação:** entregue a melhor versão (maior média sem veto; se todas tiverem veto, a com menos vetos editoriais) com as ressalvas. O juiz não trava a máquina: ele informa o custo de seguir assim.

### Última camada: leitura fria

Quem carregou o contexto aprova o próprio contexto. Depois da última rodada, aprovada ou não, abra um subagente novo (ferramenta Agent, sem herdar esta conversa) e entregue a ele só:

- cada toque renderizado pra um contato real da amostra (com a `primeira_frase` preenchida) e, se a rodada usa fallback, o D1 renderizado com o fallback;
- uma linha por conta com o fato que sustenta a primeira frase, resumido da evidência;
- pra Syndie: o prompt e 2 mensagens que ele plausivelmente geraria (marcadas como simulação).

Não entregue a doutrina, a rubrica nem as notas. Peça:

> Você vai ler emails de prospecção como se fosse quem os recebe. Para cada email, responda em uma linha cada: tem erro de gramática ou de concordância? Na primeira leitura, ficou claro o que o remetente quer? Alguma frase parece distorcer ou exagerar o fato resumido? Alguma frase soa como robô de vendas? O que você cortaria? Não reescreva o email.

O que a leitura fria achar:

- gramática, concordância, clareza: conserte e passe só aquela unidade pelos papéis de novo (não conta como rodada);
- fato distorcido ou mudança de sentido: volte a unidade pela rubrica inteira; se estourar as 3 rodadas, declare;
- registre tudo no relatório, inclusive o que ela apontou e o juiz decidiu não mudar, com o motivo.

## O que grava

### 1. Relatório: `rodadas/<rodada>/04-juiz-email.md` ou `rodadas/<rodada>/04-juiz-syndie.md`

```markdown
# Juiz · <rodada> · <email|syndie>

Resultado: <aprovado | entregue com ressalvas | entregue com veto aberto>
Rodadas de revisão: <n> · limiar: média ≥ 8, nenhum papel < 6, sem veto · nota da peça: <média>

## Placar

| rodada | unidade | comprador | editor | checador | estrategista | caçador | média | vetos | status |
|---|---|---|---|---|---|---|---|---|---|

## Contagens (versão final)

| unidade | palavras | perguntas | P:R | particularidades | negação-e-elevação | caracteres |
|---|---|---|---|---|---|---|

## Itens reprovados

| rodada | unidade | item | trecho | motivo | o que foi feito |
|---|---|---|---|---|---|

## O que mudou entre rodadas

- <2 a 3 linhas por rodada>

## Leitura fria

- <o que apontou> · <o que o juiz fez, ou por que não mudou>

## Não consegui consertar

- <unidade> · <item> · <por quê> · <o que resolveria e onde>
```

### 2. No `04-sequencia-email.md` (email)

- Atualize a linha de versão: `Versão da máquina: <AAAA-MM-DD> · juiz: <nota da peça> · rodadas de revisão: <n>`.
- Grave os toques revisados.
- Escreva no fim do arquivo:

```markdown
## Notas do juiz

Resultado: <aprovado | entregue com ressalvas | entregue com veto aberto> · relatório em 04-juiz-email.md

- <unidade> · <o que não foi consertado> · <por quê> · <o que resolveria>
```

Pra Syndie, a seção equivalente fica só no relatório `04-juiz-syndie.md`: o JSON do fluxo não leva notas.

### Declaração obrigatória

`## Não consegui consertar` e `## Notas do juiz` nunca ficam vazias nem dizem "nada". Se tudo foi consertado, declare o ponto mais fraco que sobrou (a frase de nota mais baixa, o fallback mais genérico, a particularidade mais fraca) e por que ficou assim. Quem audita comete os mesmos vícios por padrão; auditoria que sai limpa em tudo é, ela mesma, um sinal (`ai-tells.md`).

## Como mostrar ao chamador

Em até 10 linhas: resultado, nota por unidade na última rodada, vetos abertos, o que mudou de mais importante e o conteúdo de "Não consegui consertar". A `copy-email` e a `syndie-flow-builder` levam isso ao gate H2.

## Armadilhas

- **Nota inflada por auto-avaliação.** O juiz costuma ter escrito ou revisado o texto. Toda nota 9 ou 10 precisa citar o trecho que a justifica; sem trecho, vale 7.
- **Otimizar uma dimensão e quebrar outra.** Encurtar o D1 e perder a particularidade; tirar a negação-e-elevação e criar tríade. Por isso a unidade revisada passa pela rubrica inteira.
- **Consertar com fato inventado.** Falta de particularidade ou de prova é problema de matéria-prima. A saída é declarar o que falta, não escrever "recentemente" ou um número redondo.
- **Julgar a fórmula do remetente.** Saudação, fecho e encerramento literais da doutrina-cliente não perdem nota por voz.
- **Esquecer o fallback.** O D1 lido só com a primeira frase real esconde o email que vai pra quem caiu no fallback.
- **Aprovar prompt da Syndie pelo texto do prompt.** Um prompt bem escrito pode gerar mensagem ruim; a simulação na leitura fria existe pra isso.
- **Tratar QA mecânico como veredito.** Regex verde não pega motivação atribuída, pitch por negação nem máxima de palestra.
