---
name: voz-do-cliente
description: "Lê reuniões gravadas no Granola num período e extrai, com citação literal, data e reunião de origem, a dor nas palavras do comprador, as objeções e os motivos de não-decisão, agrupados por tema, gravando contexto/extracoes/voz-do-cliente-AAAA-MM.md no workspace. Use sempre que o operador pedir para tirar a voz do cliente ou do mercado das reuniões, levantar dores, objeções ou motivos de perda a partir de calls, preparar material para o gabarito de ICP ou a master copy com a língua do comprador, ou revisar o que prospects e clientes disseram (ex.: 'o que os prospects falaram nas calls de agosto', 'puxa as objeções do Granola', 'quero a dor nas palavras deles')."
---

# Voz do cliente

Transforma reuniões gravadas em material de estratégia: a dor como o comprador fala, as objeções que ele levanta e por que ele não decide. O valor está na citação literal. Paráfrase bonita não serve para escrever copy nem gabarito, porque perde exatamente a palavra que o mercado usa.

A skill não sabe quem é o cliente. Quem são as pessoas do lado do cliente, as ofertas e o que já existe de estratégia vêm do workspace ativo.

## Entradas

- **Período:** data de início e de fim (ex.: `2026-06-01` a `2026-09-30`). Se o operador não disser, perguntar.
- **Filtro:** `comerciais` (prospecção, discovery, demo, negociação), `clientes` (clientes atuais: onboarding, revisão, renovação, churn) ou os dois. Padrão: os dois.
- **Opcional:** pasta do Granola, lista de contas ou termos para restringir (ex.: "só e-commerce").

## Ler antes

1. `cliente.yaml` do workspace: `nome`, `ofertas[]` e `gates.pessoas` (quem é do lado do cliente: operador, aprovador, vendedor).
2. `estrategia/gabarito-icp.md`, `estrategia/hipoteses-icp.md` e as ofertas em `estrategia/ofertas/`, se existirem. Servem para dizer, em cada tema, onde ele se usa.
3. Extrações anteriores em `contexto/extracoes/voz-do-cliente-*.md`, para não repetir reunião já lida.

## Ferramentas do Granola

| Ferramenta | Pra quê |
|---|---|
| `mcp__claude_ai_Granola__get_account_info` | Qual conta do Granola está conectada e quais notas ela alcança (`personal`, `public`) |
| `mcp__claude_ai_Granola__list_meeting_folders` | Pastas do Granola, para restringir a busca |
| `mcp__claude_ai_Granola__list_meetings` | Reuniões do período: `time_range: "custom"`, `custom_start`, `custom_end`; opcional `folder_id` e `involvement` (`captured_by_me`, `listed_as_participant`) |
| `mcp__claude_ai_Granola__get_meetings` | Detalhe de até 10 reuniões por chamada: participantes, notas privadas, resumo, dono da nota |
| `mcp__claude_ai_Granola__get_meeting_transcript` | Transcrição literal de uma reunião. Única fonte aceita para citação |
| `mcp__claude_ai_Granola__query_granola_meetings` | Pergunta em linguagem natural sobre as reuniões. Só para achar reuniões, nunca como fonte de citação |

## Workflow

### 1. Conferir a conta do Granola

1. `get_account_info`. Anotar o email conectado e os escopos.
2. Comparar o email com `gates.pessoas` do `cliente.yaml`. Se não for de nenhuma pessoa do cliente, parar e perguntar ao operador se é a conta certa. Reunião de outra empresa não entra na voz deste cliente.

### 2. Listar as reuniões do período

1. `list_meeting_folders`. Se houver pasta com cara de vendas ou clientes, mostrar e perguntar se restringe a ela.
2. `list_meetings` com `time_range: "custom"`, `custom_start` e `custom_end` do período, e `folder_id` se o operador escolheu. Para períodos longos, quebrar por mês e juntar.
3. Tirar as reuniões que já aparecem numa extração anterior (mesmo id).

### 3. Triar antes de ler

Classificar cada reunião só pelo título, pelos participantes e pela pasta, sem abrir conteúdo:

| Tipo | Como reconhecer | O que fazer |
|---|---|---|
| `comercial` | participante de domínio externo que não é cliente; título com discovery, demo, apresentação, proposta | ler, se o filtro pede |
| `cliente` | participante de conta que já é cliente; título com onboarding, revisão, alinhamento | ler, se o filtro pede |
| `interna` | só participantes do domínio do cliente | ignorar |
| `pessoal` | médico, família, banco, escola, entrevista de emprego pessoal, compromisso particular | ignorar sem abrir e sem registrar o título |
| `duvida` | não dá para saber pelo título | perguntar ao operador |

Mostrar ao operador a tabela das reuniões que vão ser lidas (data, título, tipo, conta) e as quantidades ignoradas por tipo. Só seguir com o ok dele. Reunião pessoal não aparece nem nessa tabela: entra só na contagem.

### 4. Conferir o autor

1. `get_meetings` em lotes de até 10 ids.
2. Para cada reunião, o dono da nota (quem gravou) tem que ser uma das pessoas de `gates.pessoas`. Nota compartilhada por alguém de fora do cliente não entra sem confirmação do operador.
3. Se o dono não confere, marcar `autor não confere`, tirar da leitura e listar no fim para o operador decidir.

### 5. Ler a transcrição

1. `get_meeting_transcript` para cada reunião que passou.
2. Separar quem fala. O áudio do microfone costuma ser de quem gravou (lado do cliente); o áudio do sistema é o outro lado e pode misturar várias pessoas. Citação só do lado do comprador (prospect ou cliente do cliente). O que o vendedor disse não é voz do mercado.
3. Quando não dá para dizer quem falou, anotar o falante como `lado do comprador, sem nome`. Quando nem o lado dá para saber, não usar como citação.
4. Avaliar a qualidade da transcrição: `boa` ou `baixa`. Baixa quando há palavras sem sentido, trechos marcados como inaudíveis, frases cortadas no meio, troca de idioma, falantes misturados ou blocos muito curtos. Transcrição baixa pode dar citação, mas cada citação dela leva a marca `[transcrição baixa]`.
5. Sem transcrição, só com nota: a nota do autor não é citação do comprador. Registrar a reunião na tabela como `sem transcrição` e não tirar citação dela.

### 6. Extrair

Três tipos, sempre com citação literal:

- **Dor:** o problema como o comprador descreve, com as palavras dele.
- **Objeção:** o que ele levanta contra comprar ou contra a proposta (preço, momento, risco, concorrente, esforço interno).
- **Não-decisão:** por que a conversa não avança (falta de dono, prioridade, orçamento, medo de trocar, "vamos ver no ano que vem").

Para cada citação, guardar: texto literal, falante (cargo e empresa quando se sabe), reunião (id do resumo, título, data) e qualidade da transcrição.

Regras da citação:

- Copiar do jeito que está na transcrição, com erro de fala, repetição e gíria. Pode cortar começo ou fim com `(...)`, nunca o meio de uma ideia.
- Nunca juntar duas falas numa citação só.
- Nunca corrigir, resumir ou traduzir dentro das aspas. A interpretação vai na linha de leitura, fora das aspas.
- Nada tirado do resumo gerado pelo Granola nem da resposta do `query_granola_meetings`. Esses textos são paráfrase de máquina.

### 7. Agrupar por tema

1. Juntar as citações que falam da mesma coisa. Dar ao tema um nome curto nas palavras do comprador, não no jargão do cliente.
2. Contar em quantas reuniões diferentes o tema aparece (não quantas citações). Tema em 2 ou mais reuniões é `padrão`; em uma só, `isolado`.
3. Tema que só aparece em transcrição baixa não pode ser `padrão`: fica `isolado` até aparecer em transcrição boa.
4. Ordenar: padrões primeiro, pelo número de reuniões.
5. Para cada tema, uma linha de leitura (o que isso quer dizer para a estratégia) e onde usar:
   - `gabarito`: vira critério de fit, sinal, pergunta de discovery ou desqualificador (dizer qual);
   - `master copy`: vira a dor ou a frase de abertura de uma oferta (dizer qual);
   - `objeções`: vira resposta pronta a uma objeção.

### 8. Gravar

Arquivo: `contexto/extracoes/voz-do-cliente-AAAA-MM.md`, com o ano e o mês do fim do período. Se o arquivo já existe, perguntar: acrescentar uma seção nova com o período, ou gravar com sufixo (`-2`). Nunca sobrescrever.

Formato:

```markdown
# Voz do cliente · <AAAA-MM>

Período: <AAAA-MM-DD> a <AAAA-MM-DD> · filtro: <comerciais, clientes>
Gerado em <AAAA-MM-DD> pela voz-do-cliente · motor <x.y.z> · conta do Granola: <email>
Reuniões lidas: <n> (<n> comerciais, <n> clientes) · ignoradas: <n> pessoais, <n> internas, <n> autor não confere, <n> sem transcrição

## Reuniões lidas

| ref | data | reunião | tipo | conta | falantes do comprador | transcrição |
|---|---|---|---|---|---|---|
| R1 | 2026-08-12 | Discovery Acme | comercial | acme.com.br | Head de CRM | boa |

## Temas

### T1 · <nome do tema nas palavras do comprador>

Tipo: dor · aparece em 3 reuniões (R1, R4, R7) · padrão

> "<citação literal>"
> <cargo>, <conta> · R1 · 2026-08-12

> "<citação literal>" [transcrição baixa]
> lado do comprador, sem nome, <conta> · R4 · 2026-08-20

**Leitura:** <uma linha: o que isso quer dizer para a estratégia>
**Onde usar:** gabarito (discovery, pergunta sobre X) · master copy (dor da oferta <id>) · objeções

## Citações fortes fora dos temas

Citações boas demais para perder que não formaram tema. Mesmo formato.

## Lacunas

O que não apareceu e devia aparecer (ex.: nenhuma objeção de preço em 12 reuniões comerciais). Cada lacuna vira pergunta para a próxima reunião ou para o workshop.

## Para o operador decidir

- Reuniões marcadas `duvida` ou `autor não confere`, com data e título.
```

### 9. Apresentar

Resumir para o operador em poucas linhas: quantas reuniões lidas, os 3 a 5 temas padrão com uma citação cada, as lacunas e o que ficou para ele decidir. Mostrar o caminho do arquivo.

## Armadilhas

- **Paráfrase entre aspas.** É o erro que mata a skill. Se não dá para copiar literal, não é citação: vai para a leitura, sem aspas.
- **Voz do vendedor como voz do mercado.** Quem vende repete a própria tese e ela volta como "dor do cliente". Citação só do lado do comprador.
- **Resumo do Granola como fonte.** O resumo e o `query_granola_meetings` são texto de máquina. Servem para achar reunião, nunca para citar.
- **Reunião pessoal.** Não abrir, não citar, não registrar título. Só contar.
- **Conta errada do Granola.** Operador com mais de uma empresa pode estar com outra conta conectada. Conferir no passo 1.
- **Nome de prospect fora do workspace.** Nome de pessoa e de conta fica só em `contexto/extracoes/` do workspace. Se um tema virar lição de ofício, ele sobe anonimizado, pelo `loop-de-licoes`, nunca com a citação.
- **Tema inflado por uma reunião só.** Dez citações de uma call longa são um tema `isolado`, não um padrão.
- **Transcrição baixa tratada como boa.** Palavra trocada pela transcrição vira "língua do mercado" errada na copy. Marcar sempre.
