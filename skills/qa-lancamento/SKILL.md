---
name: qa-lancamento
description: Faz a checagem final antes de qualquer envio de uma rodada de outbound e prepara o gate H3. Renderiza 3 contatos por segmento com scripts/render_email.py e confere merge, acentuação, empresa e cargo; refaz a supressão com snapshot fresco do ledger; confere duplicata contra o CRM do cliente e contra a aba contas; confere caixas aquecidas, limite diário, SPF, DKIM e DMARC do domínio remetente e emails verificados (teto de bounce de 2%); confere o fluxo importado na Syndie e a sequência pausada e vazia no Apollo; grava 05-qa-lancamento.md com cada item em verde ou vermelho, evidência, data e responsável, e bloqueia o lançamento se houver vermelho. Use na etapa E6, quando o operador disser "roda o QA", "QA de lançamento", "posso lançar?", "checa antes do H3", "go/no-go da rodada", "roda a qa-lancamento". Nunca escreve a aprovação do H3.
---

# qa-lancamento

Última checagem antes de qualquer mensagem sair. Produz `rodadas/<rodada>/05-qa-lancamento.md`, o único lugar onde o H3 é aprovado. A skill checa, registra a evidência e bloqueia; quem aprova é uma pessoa do `gates.H3`, escrevendo a linha de aprovação à mão.

A skill não sabe quem é o cliente. CRM, caixas, limites, janela e donos de gate vêm do `cliente.yaml`.

## Antes de começar: o que ler

| # | Arquivo | O que tirar dele |
|---|---|---|
| 1 | `cliente.yaml` | `crm`, `stack`, `remetentes.caixas_email[]`, `remetentes.perfil_linkedin`, `gates.H3`, `gates.pessoas` |
| 2 | `doutrina/outbound.md` | Seção "Frases banidas e QA de envio": o que olhar no email renderizado |
| 3 | `doutrina/escrita.md` | Travessão, acentuação, registro por canal |
| 4 | `adapters/google-sheets/README.md` | Leitura do ledger e snapshot |
| 5 | `adapters/syndie/README.md` e `adapters/account-guardian/README.md` (se `crm: account-guardian`) | Limites e busca de duplicata |
| 6 | Arquivos da rodada | `03-contatos.csv`, vereditos, `04-sequencia-email.md`, `04-apollo-import.csv`, `04-apollo-ids.json`, `04-syndie-upload*.csv`, `04-syndie-flow*.json`, `04-syndie-flow-exportado.json`, `04-syndie-comparacao.md` |

## Pré-condições

Pare e diga ao operador o que falta se não existirem os diffs H2 aprovados das peças que vão ao ar (`aprendizado/diffs/<rodada>-H2-email.md`, `aprendizado/diffs/<rodada>-H2-syndie.md`) ou os arquivos gerados pela `apollo-sequence-builder` (Parte 1) e pela `syndie-flow-builder` dos canais da rodada. Canal que não está no `stack` do cliente não entra no QA; o item vira "não se aplica" (verde, com a nota).

## Passos

Cada passo vira uma ou mais linhas da tabela de itens. Toda linha tem: resultado (`verde` ou `vermelho`), evidência (arquivo, comando e saída, ou chamada de ferramenta e o que voltou), data e hora, responsável (`máquina` para o que a skill conferiu; o nome da pessoa para o que ela confirmou na interface). Não existe amarelo: dúvida é vermelho até alguém resolver.

### 1. Email renderizado

```bash
python scripts/render_email.py --sequencia rodadas/<rodada>/04-sequencia-email.md \
    --contatos rodadas/<rodada>/03-contatos.csv --amostra 3 --por segmento \
    --saida rodadas/<rodada>/05-qa-render.md
```

Se a sequência tem D1 por nível (`## D1 · decisor` e `## D1 · champion`), rode também com `--amostra 3 --por papel` e salve em `05-qa-render-papel.md`: os dois níveis precisam aparecer renderizados, e cada contato precisa ter recebido a variante do seu papel (o render escreve `### D1 · <nível>` no bloco). Contato sem papel reconhecido recebe a de champion e gera aviso; aviso desses é vermelho até o papel ser preenchido no `03-contatos.csv`.

Se a amostra cair em contato que não vai pro email (canal `linkedin`), troque por um que esteja no `04-apollo-import.csv`. E confira um contato do `04-apollo-import.csv` com o valor que subiu pro Apollo (fallback já aplicado no campo custom), pra ver que o campo e o render dizem a mesma coisa.

- Saída diferente de 0: vermelho (sobrou `{{`, variável não declarada ou travessão).
- Leia os 4 toques de cada contato renderizado e confira, linha a linha:
  - nenhuma merge tag crua ou vazia ("Oi ,", "na , vocês");
  - fallback lendo bem na frase;
  - acentuação completa (procurar por regex palavras comuns sem acento: `voce`, `nao`, `esta `, `ja `, `e ` no lugar de "é", `sao`, `tambem`, `ate`, `proprio`, `negocio`, `operacao`);
  - nome da empresa igual ao `company_name` do veredito e cargo igual ao `cargo` do `03-contatos.csv` daquele contato;
  - primeira frase é da conta certa (o fato cita a empresa ou algo só dela);
  - uma pergunta por email, sem link no D1, sem travessão.
- Uma linha da tabela por segmento, com os contatos conferidos na evidência. Qualquer erro num contato: vermelho, e o erro descrito.

### 2. Supressão com snapshot fresco

1. Exporte agora as abas `supressao`, `contas`, `contatos` e `toques` pra `rodadas/<rodada>/_snapshot/<AAAA-MM-DD-HHMM>/<aba>.csv`. Não reaproveite snapshot anterior: o ledger pode ter mudado desde a montagem.
2. Rode o `suppress.py` em cada lista que vai ao ar:

   ```bash
   python scripts/suppress.py --lista rodadas/<rodada>/04-apollo-import.csv --ledger-dir <snapshot> \
       --saida <snapshot>/qa-apollo-filtrado.csv --removidos <snapshot>/qa-apollo-removidos.csv \
       --col-dominio domain --col-email email --col-linkedin linkedin_url
   python scripts/suppress.py --lista rodadas/<rodada>/04-syndie-upload.csv --ledger-dir <snapshot> \
       --saida <snapshot>/qa-syndie-filtrado.csv --removidos <snapshot>/qa-syndie-removidos.csv \
       --col-dominio dominio --col-email email --col-linkedin linkedin_url
   ```

3. Verde só com 0 removidos em cada lista. Removido: vermelho, com o contato e o motivo. Correção: tirar do lote do Apollo (não inscrever) e da campanha da Syndie, atualizar os arquivos da rodada e rodar o QA de novo.

### 3. Duplicata

**Dentro da rodada:** email repetido, URL de LinkedIn repetida, mais de 3 contatos na mesma conta, a mesma pessoa em duas campanhas da Syndie. Qualquer caso: vermelho.

**Contra a aba `contas` do ledger:** domínio da rodada que já está em `contas` com `rodada` diferente da atual e `estagio` `Working`, `Respondeu`, `Reuniao`, `Oportunidade` ou `Cliente`: vermelho (a conta está em outra rodada ou em conversa). `Perdida` ou `Nutrir`: verde com nota, desde que a conta tenha passado pelo H1 desta rodada.

**Contra o CRM do `cliente.yaml`:**

| `crm` | O que fazer |
|---|---|
| `account-guardian` | `guardian_search_accounts` com `query` = `company_name` de cada conta da rodada. Candidato que é a mesma empresa em estágio de venda (`discovery_call` em diante) ou de cliente: vermelho. Mesma empresa em `target`, `working`, `paused`, `disqualified` ou `closed_lost`: verde com nota do estágio. Nome parecido de outra empresa: verde com nota. O Guardian não guarda domínio: a correspondência é por nome e, se ambígua, vai pro operador decidir. |
| `hubspot` | Fora do escopo da v0.1. Pedir ao operador um export de empresas e negócios abertos e comparar por domínio. Sem export: vermelho "duplicata no CRM não conferida". |
| `nenhum` | Pula. Linha verde "não se aplica: cliente sem CRM". |

### 4. Caixas e volume

1. Pra cada caixa em `04-apollo-ids.json`: está em `remetentes.caixas_email`; aquecida (`aquecida_em` menor ou igual a hoje, ou `aquecimento_inicio` menor ou igual a hoje menos 14 dias); `limite_diario` até 30.
2. `apollo_email_accounts_index`: cada caixa ainda aparece conectada.
3. O lote do primeiro dia no calendário da `apollo-sequence-builder` é no máximo `floor(C × L ÷ 4)`, e o `max_emails_per_day` da sequência é no máximo `C × L`.
4. LinkedIn: número de leads da campanha cabe em `convites_por_semana`, ou o calendário em semanas está escrito no `04-syndie-importacao.md`.

Qualquer caixa fora: vermelho. Uma linha por caixa.

### 4b. Autenticação do domínio remetente

Uma linha por domínio das caixas (a parte depois do `@`). Consulta de DNS, só leitura, no servidor público do Google:

```bash
nslookup -type=TXT <dominio> 8.8.8.8                    # SPF
nslookup -type=TXT _dmarc.<dominio> 8.8.8.8             # DMARC
nslookup -type=TXT <seletor>._domainkey.<dominio> 8.8.8.8   # DKIM
```

- **SPF:** um registro `v=spf1` que inclui o provedor da caixa (Google Workspace: `include:_spf.google.com`; Microsoft 365: `include:spf.protection.outlook.com`) e termina em `-all` ou `~all`. Sem registro, dois registros `v=spf1` ou provedor ausente: vermelho.
- **DMARC:** um registro `v=DMARC1` com `p=none`, `p=quarantine` ou `p=reject`. Ausente: vermelho.
- **DKIM:** registro `v=DKIM1` com chave `p=` não vazia no seletor do provedor (Google Workspace: `google`; Microsoft 365: `selector1` e `selector2`). Seletor desconhecido: pedir ao operador o cabeçalho `DKIM-Signature` (campo `s=`) de um email enviado pela caixa. Sem DKIM: vermelho.
- Caixa no domínio principal do cliente (o mesmo do site): a linha fica verde se as três passarem, mas leva nota "envio pelo domínio principal: o teto de bounce de 2% protege a reputação do domínio que o cliente usa com os clientes dele".

Evidência: o registro devolvido, copiado na linha. Nunca alterar DNS: correção é do cliente, e o item vira pendência dele.

### 4c. Qualidade dos emails da lista

O teto de bounce da rodada é **2%**. Ele só se protege antes do envio:

- todo contato no `04-apollo-import.csv` tem `email_status = verified`. Qualquer outro status: vermelho;
- nenhum email de caixa genérica (`contato@`, `vendas@`, `sac@`, `atendimento@`, `comercial@`, `faleconosco@`) na lista: vermelho.

Depois do lançamento, bounce acima de 2% pausa a sequência (regra em `doutrina/outbound.md`). O QA registra o teto no `05-qa-lancamento.md` pra quem acompanha o envio.

### 5. Syndie

1. `04-syndie-flow-exportado.json` existe. Sem ele: vermelho "fluxo importado não conferido"; peça ao operador que exporte.
2. Rode o passo 8 da `syndie-flow-builder` (comparação nó a nó). Verde só com 0 divergências que bloqueiam no `04-syndie-comparacao.md`.
3. Número de leads na campanha igual às linhas do `04-syndie-upload.csv`, e a campanha **pausada, não iniciada**: confirmados pelo operador na interface. Responsável = o nome dele.

### 6. Apollo

1. `apollo_emailer_campaigns_show` com o `id` de cada sequência do `04-apollo-ids.json` (uma por nível quando o D1 tem variante; confira que o D1 de cada uma é a variante do nível certo e que cada contato está no lote da sequência do seu papel).
2. Verde só se: `active` falso; 4 passos com os intervalos do arquivo; assuntos e corpos iguais ao `04-sequencia-email.md` (sem corte, merge tags certas); **nenhum contato inscrito**. Se a resposta não trouxer a contagem de contatos, o operador confere na interface e a linha leva o nome dele.
3. Contatos e contas da rodada existem no Apollo com o rótulo da rodada (conferir por amostra com `apollo_contacts_search`).

### 7. Ledger e diffs

- Contas e contatos da rodada no ledger e a linha da rodada na aba `rodadas` (feitos pela `registrar-ledger`, fase 1). Ledger pendente: vermelho.
- Diffs H2 salvos e aprovados pra cada peça que vai ao ar.

### 8. Gravar o arquivo de QA

Grave `rodadas/<rodada>/05-qa-lancamento.md`. Rodar o QA de novo reescreve o arquivo inteiro, e qualquer aprovação anterior deixa de valer: o bloco "Decisão H3" volta vazio.

```markdown
# QA de lançamento · <rodada>

QA rodado em: AAAA-MM-DD HH:MM · versão do motor: <x.y.z> · snapshot: rodadas/<rodada>/_snapshot/<AAAA-MM-DD-HHMM>/

## Itens

| # | Item | Resultado | Evidência | Data | Responsável |
|---|---|---|---|---|---|
| 1 | Render D1 a D13, segmento <x>, 3 contatos | verde | 05-qa-render.md; render_email.py saiu 0 | AAAA-MM-DD HH:MM | máquina |
| ... | | | | | |

## Vermelhos e o que fazer

Um bloco por item vermelho: o que está errado, onde, e a correção. "Nenhum" quando não houver.

## Decisão H3

Itens vermelhos: <n>
Situação: <liberado para decisão | bloqueado>

Quem pode aprovar: <nomes de gates.H3>. A aprovação é uma linha escrita à mão por essa pessoa, logo abaixo, no formato `H3 aprovado AAAA-MM-DD HH:MM por <nome>`. Com item vermelho, a decisão possível é `H3 bloqueado AAAA-MM-DD HH:MM por <nome>`.

## Lançamento

Preenchido pelo operador: data e hora em que a sequência foi ativada no Apollo e em que a campanha foi iniciada na Syndie.
```

Com vermelho: situação `bloqueado`. Diga ao operador que o lançamento está bloqueado, liste os vermelhos e as correções, e pare. Sem vermelho: diga que está liberado para decisão e peça que a pessoa do `gates.H3` escreva a linha de aprovação no arquivo e a decisão na coluna `decisao_h3` da aba `rodadas` do ledger (coluna humana).

**A skill nunca escreve a linha "H3 aprovado", nem sugerida em texto pronto pra copiar com data e nome preenchidos.**

### 9. Diff H3

Salve `aprendizado/diffs/<rodada>-H3-qa.md` no formato de `schemas/diff.template.md`, peça `qa`:

- **Versão da máquina:** a tabela de itens da primeira execução do QA desta rodada, com os vermelhos que ela pegou.
- **Versão aprovada:** a tabela da execução que foi aprovada (ou bloqueada), mais a linha de decisão escrita pela pessoa.
- **Notas do operador:** uma linha por vermelho que o QA pegou, com a causa (qual skill deixou passar) e a correção. É o que o `loop-de-licoes` usa pra corrigir a skill de origem. Linha extra se o operador achou algo que o QA não pegou.

Se o QA rodar várias vezes, o diff é completado a cada execução até a decisão; depois da decisão, não se edita.

## O que gravar e onde

| Arquivo | Conteúdo |
|---|---|
| `rodadas/<rodada>/05-qa-render.md` | Emails renderizados da amostra |
| `rodadas/<rodada>/_snapshot/<AAAA-MM-DD-HHMM>/` | Snapshot do ledger e saídas do `suppress.py` |
| `rodadas/<rodada>/04-syndie-comparacao.md` | Atualizado pelo passo 5 |
| `rodadas/<rodada>/05-qa-lancamento.md` | Itens, vermelhos, bloco de decisão, bloco de lançamento |
| `aprendizado/diffs/<rodada>-H3-qa.md` | O que o QA pegou |

## Gate

H3. Nada é enviado, nenhum contato é inscrito e nenhuma campanha é ativada ou iniciada sem a linha `H3 aprovado AAAA-MM-DD HH:MM por <nome>` escrita por uma pessoa do `gates.H3` neste arquivo, sem nenhum vermelho na tabela. A `apollo-sequence-builder` confere essa linha antes de inscrever.

## Armadilhas

- **QA sobre o template, não sobre o renderizado.** Merge vazio só aparece renderizado.
- **Snapshot velho.** Alguém respondeu, pediu optout ou foi marcado `nao_abordar` desde a montagem. Sempre snapshot novo.
- **Amostra só do primeiro segmento.** São 3 contatos por segmento, e de preferência contatos com campo vazio (onde o fallback entra).
- **Aprovar com vermelho "pequeno".** Não existe. Corrige e roda de novo.
- **Confiar que a campanha está pausada** sem alguém olhar na interface.
- **Aprovação antiga depois de mudança.** Mudou lista, copy ou fluxo depois da aprovação: roda o QA de novo e a aprovação cai.
- **Duplicata por nome no CRM.** "Acme" e "Acme Comércio" podem ser a mesma empresa. Ambíguo vai pro operador.
