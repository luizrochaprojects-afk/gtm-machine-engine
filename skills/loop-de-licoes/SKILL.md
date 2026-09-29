---
name: loop-de-licoes
description: Fecha o aprendizado de uma rodada de outbound (versão manual). Lê os diffs de gate da rodada em aprendizado/diffs/, mede o % mantido sem edição, classifica cada mudança (cosmética, erro da máquina, preferência nova), extrai o princípio, marca cliente, ofício ou skill, pergunta "gravo essas lições?" e grava as aprovadas no lugar certo, editando a regra existente; atualiza aprendizado/ciclos.md, propõe consolidação da doutrina-cliente e lista as lições de ofício prontas pra subir pro motor. Use no fim de cada rodada ou quando o operador disser "roda o loop de lições", "fecha a rodada", "o que aprendemos na r1", "grava as lições", "atualiza o ciclos". Nada roda sozinho: só quando o operador chama, e nada é gravado sem a resposta dele.
---

# loop-de-licoes

O que faz a máquina melhorar a cada rodada. A edição que o operador faz em silêncio antes de aprovar é o feedback mais honesto que existe; esta skill transforma esse diff em regra no lugar certo, pra que a rodada seguinte já saia com ela.

Versão manual: a skill roda quando o operador chama, mostra tudo antes de gravar e não agenda nada.

## Antes de começar: o que ler

- `doutrina/_protocolo.md` inteiro. Ele manda: força das regras, procedência, editar no lugar, silêncio, esquecimento, consolidação e promoção.
- `cliente.yaml`: `versao_motor` e donos dos gates.
- `estrategia/doutrina-cliente.md`: onde a maioria das lições vai parar, e as `[hipótese]` abertas.
- `doutrina/outbound.md`, `doutrina/escrita.md`, `doutrina/ai-tells.md`, `doutrina/producao-com-agentes.md`: pra saber se a lição já existe como regra do motor.
- `aprendizado/ciclos.md` e `aprendizado/licoes-candidatas-motor.md`.
- Os relatórios do juiz da rodada (`rodadas/<rodada>/04-juiz-*.md`), pra saber quais regras a máquina aplicou de propósito.

Pergunte ao operador, uma vez por sessão: **"você também é mantenedor do motor nesta sessão?"** A resposta decide se lição de ofício pode ir direto pro motor (passo 6).

## Passo 1: inventário dos diffs

Liste `aprendizado/diffs/<rodada>-*.md` e monte:

| diff | gate | peça | skill de origem | resultado | tem versão aprovada? |
|---|---|---|---|---|---|

- Cada gate da rodada (H0 a H3) deveria ter pelo menos um diff. Gate sem diff: avise.
- Diff com `## Versão aprovada` vazia: peça ao operador, com as palavras do protocolo: "me manda a versão que foi aprovada ou enviada". Sem ela, o diff fica fora desta passada e é listado no fim como pendente.
- "Igual à versão da máquina" é um diff válido: é silêncio (passo 5).

## Passo 2: medir

Preencha o bloco `## Métrica` de cada diff. É o único bloco que se escreve num diff fechado.

**Peças de texto** (estratégia, email, Syndie):

- Unidade = frase. Separe por `.`, `?`, `!` e quebra de linha. O assunto conta como uma frase.
- Não conte as fórmulas fixas da doutrina-cliente (saudação, fecho, assinatura): elas sempre ficam e inflariam o número.
- Frase preservada = aparece idêntica na versão aprovada, ignorando espaços. Uma palavra trocada já é frase editada.
- `% mantido = frases preservadas ÷ frases da máquina`.

**Listas** (H1): unidade = veredito revisado pelo operador. `% mantido = vereditos mantidos ÷ vereditos revisados`. Conta só o que ele revisou (P0 e incertas), não a lista inteira.

**Outras peças** (ex.: QA do H3): declare a unidade no próprio bloco (ex.: item do checklist cujo status o humano não mudou) e use sempre a mesma nas rodadas seguintes.

## Passo 3: classificar cada mudança

Leia a versão da máquina contra a aprovada e as `## Notas do operador`. Cada mudança cai numa classe:

| Classe | O que é | O que fazer |
|---|---|---|
| **Cosmética** | Troca equivalente, sem princípio ("tem" por "possui" sem motivo) | Ignorar. Só contar |
| **Erro da máquina** | A máquina violou algo que já estava escrito numa doutrina, na doutrina-cliente ou na skill | Candidata. A regra já existe: a lição é sobre por que a skill ou o juiz não pegou |
| **Preferência nova** | A máquina seguiu as regras e o operador mudou mesmo assim | Candidata, marcada como preferência. É regra nova ou refinamento de uma existente |

Fato corrigido (número errado, nome de conta, cargo) é erro da máquina. A lição é sobre de onde o fato veio.

## Passo 4: extrair o princípio e o endereço

**O princípio, não o caso.** Lição boa evita uma classe de erro futura.

- Ruim: "trocou 'faz sentido conversar?' por 'hoje isso sai de planilha?'".
- Bom: "a pergunta do D1 é sobre a operação dele e se responde com sim ou não; pergunta sobre conversar é pedido de reunião disfarçado".

Teste: a frase vale na próxima rodada, em outra conta, sem o caso? Se não, reescreva.

**O endereço**, um por lição:

| Endereço | Quando | Destino |
|---|---|---|
| `cliente` | Mercado, marca, número autorizado, âncora, pricing, voz ou gosto do aprovador | `estrategia/doutrina-cliente.md` |
| `ofício` | Como escrever, qualificar ou operar, e o princípio sobrevive sem nome, número e vertical identificável | Passo 6 |
| `skill` | Uma skill ou a rubrica do juiz deveria ter feito ou pegado isso (passo que falta, checagem que falta, item de rubrica) | Proposta de mudança, passo 6 |

Na dúvida entre cliente e ofício: `cliente`. É mais barato promover depois do que tirar do motor.

## Passo 5: silêncio e hipóteses

- **Diff aprovado sem edição:** confirma as regras e hipóteses que a peça aplicava. Não pergunte nada; registre no `ciclos.md` e use no passo seguinte.
- **Frases preservadas que aplicavam uma `[hipótese]`** (veja o relatório do juiz e a própria hipótese na doutrina-cliente): a hipótese sobreviveu intacta a um diff. Proponha promovê-la a `[regra]`, com "promovida em <data>: sobreviveu ao diff <rodada>-<gate>-<peça>".
- **Hipótese não confirmada** nesta rodada: some 1 à contagem dela. Na 3ª rodada sem confirmação, marque pra sair na próxima consolidação.

## Passo 6: apresentar e perguntar

Mostre uma tabela só:

| # | diff | mudança (trecho curto) | classe | princípio proposto | endereço | destino | regra que edita (ou "nova") |
|---|---|---|---|---|---|---|---|

Embaixo: quantas mudanças cosméticas foram ignoradas, quais hipóteses propõe promover por silêncio e quais estão perto de expirar.

Pergunte: **"gravo essas lições?"** O operador pode aprovar tudo, aprovar por número, reformular (grave a formulação dele, palavra por palavra) ou recusar (não grave nada daquela linha).

**Sem resposta** sobre uma linha (ele respondeu outras, disse "depois" ou encerrou a sessão): grave como `[hipótese]` com "diff não confirmado", no destino de workspace, e reapresente na próxima vez. Hipótese sem resposta nunca vai pro motor.

## Passo 7: gravar

**Formato da linha** (o mesmo das doutrinas):

```markdown
- [regra] **<princípio em uma frase>** <detalhe, se precisar>. Procedência: <AAAA-MM-DD>, <rodada>, diff <gate>-<peça>: <o que aconteceu, em uma linha>.
- [hipótese] **<princípio>** <detalhe>. Procedência: <AAAA-MM-DD>, <rodada>, diff <gate>-<peça>, diff não confirmado.
```

**Editar no lugar, nunca regra paralela.** Antes de gravar, procure no destino (e em `doutrina/`) uma regra sobre o mesmo ponto:

- existe e a lição refina: reescreva a regra existente e acrescente "(atualizada em <data>: <o que mudou>)";
- existe e a lição contradiz: reescreva; se o erro antigo for sedutor o bastante pra voltar, deixe lápide de uma linha ("não fazer X; valeu até <data> porque Y");
- existe no motor e a máquina violou: a regra não muda. A lição é do endereço `skill` (por que não pegou), e a regra ganha a procedência nova no workspace, se fizer sentido;
- não existe: crie na seção do assunto.

**Por endereço:**

- **`cliente`** → `estrategia/doutrina-cliente.md`, na seção do assunto.
- **`ofício`** →
  1. aplicada no workspace, pra rodada seguinte já usar: `estrategia/doutrina-cliente.md`, com a marca `(ofício, candidata ao motor)` no fim da linha;
  2. copiada pra `aprendizado/licoes-candidatas-motor.md` (formato abaixo);
  3. na `doutrina/<ofício>.md` do motor **só** se o operador for também mantenedor e decidir promover agora. Nesse caso siga o passo 9, registrando o motivo da promoção antecipada.
- **`skill`** →
  1. proposta escrita em `aprendizado/licoes-candidatas-motor.md` com tipo `skill`: a skill ou o item da rubrica, e o texto proposto;
  2. enquanto não é promovida, compense no workspace quando der: uma `[regra]` na doutrina-cliente que a skill ou o juiz já leem ("o juiz reprova pergunta sobre conversar no D1");
  3. o workspace nunca edita uma `SKILL.md`. Mudança de skill é mudança do motor: só o mantenedor, pelo passo 9.

**Formato de `aprendizado/licoes-candidatas-motor.md`** (se o arquivo já tiver outro formato, siga o dele):

```markdown
| data | rodada | diff | tipo | princípio anonimizado | destino no motor | status |
|---|---|---|---|---|---|---|
| 2026-10-05 | 2026-10-01-r1-varejo-plataforma | H2-email | ofício | A pergunta do D1 é sobre a operação e se responde com sim ou não | doutrina/outbound.md, Cold email | candidata |
```

`tipo` é `ofício` ou `skill`. `status`: `candidata`, `vista em 2 clientes`, `promovida vX.Y.Z` ou `recusada pelo mantenedor`. O princípio já entra anonimizado (sem conta, pessoa, número, preço ou vertical identificável); se não sobrevive sem o caso, a lição é de cliente e não entra aqui.

## Passo 8: ciclos.md

Acrescente uma linha por skill e gate da rodada em `aprendizado/ciclos.md`:

```markdown
| rodada | skill | gate | % mantido sem edição | data |
|---|---|---|---|---|
| 2026-10-01-r1-varejo-plataforma | copy-email | H2 | 71% | 2026-10-05 |
```

- `skill` vem do cabeçalho do diff (`Skill de origem`); `%` vem do bloco `## Métrica`.
- Se o arquivo não tiver a tabela, crie com esse cabeçalho e, acima dela, a regra de cálculo do passo 2.
- Mostre ao operador a tendência de cada skill contra as rodadas anteriores. A tendência importa mais que o valor.
- Diff aprovado sem edição entra com 100% e a nota "silêncio: confirma <regras aplicadas>".

## Passo 9: consolidação e promoção

**Consolidação da doutrina-cliente.** Proponha (não faça sem aprovação) reescrever `estrategia/doutrina-cliente.md` inteira quando:

- ela acumular 3 ou mais `[hipótese]`;
- houver duas regras que se contradizem;
- estiver inchada (regras repetidas, seção que ninguém consegue ler de uma vez).

Na consolidação: juntar regras sobre o mesmo ponto, tirar hipóteses com 3 rodadas sem confirmação, deixar lápide só pra erro sedutor, manter a procedência de cada regra. Mostre o antes e o depois e pergunte.

**Lições de ofício prontas pra promoção.** Leia `clientes/*/aprendizado/licoes-candidatas-motor.md` dos outros workspaces que existirem nesta máquina. Compare princípios, não palavras: duas formulações diferentes do mesmo princípio contam como a mesma lição. Liste as que aparecem em 2 clientes como **prontas pra promoção**, mostrando só o princípio anonimizado (nada de outro workspace entra neste). Nenhuma sobe sem o mantenedor. O passo a passo que ele segue, do `_protocolo.md`:

1. **Anonimizar:** tirar nome de cliente, conta, pessoa, número, preço e vertical identificável; exemplo vira empresa fictícia (Acme) ou categoria.
2. **Gravar no motor:** na `doutrina/<ofício>.md`, com a força que tem e procedência anonimizada ("2 clientes, rodadas de 2026-10"), ou como mudança numa `SKILL.md` ou na rubrica da `juiz-de-copy`. Editar no lugar.
3. **CHANGELOG:** entrada no `CHANGELOG.md` do motor com versão, data, mudança e origem ("cliente zero + cliente 2", nunca o nome).
4. **Conferir:** `python scripts/check_sanitize.py` na raiz do motor, e `python -m pytest scripts/` se mexeu em script. Os dois passam antes de fechar.
5. **Marcar** a linha como `promovida vX.Y.Z` no `licoes-candidatas-motor.md` de cada workspace de origem.

## Fechamento

Mostre ao operador, curto:

- % mantido por skill nesta rodada e a tendência;
- lições gravadas (quantas `[regra]`, quantas `[hipótese]`, onde);
- hipóteses promovidas e expiradas;
- candidatas ao motor novas e as prontas pra promoção;
- diffs pendentes (sem versão aprovada) e gates sem diff.

## Armadilhas

- **Gravar o caso em vez do princípio.** Vira regra que só vale pra uma conta e polui a doutrina.
- **Regra paralela.** Duas regras sobre o mesmo ponto em lugares diferentes: a próxima skill segue a errada. Procure antes de criar.
- **Subir cliente pro motor.** Número autorizado, âncora, pricing e voz do aprovador nunca sobem, mesmo "anonimizados".
- **Tratar erro da máquina como regra nova.** Se a regra já existia, reescrevê-la não resolve: o que falhou foi a skill ou o juiz.
- **Gravar sem aprovação.** Regra errada na doutrina contamina todas as rodadas seguintes. Sem resposta, é hipótese no workspace, nunca regra.
- **% inflado.** Contar saudação e fecho fixos, ou contar a lista inteira no H1, faz a máquina parecer melhor do que está.
- **Copiar dado de outro workspace.** Pra achar lição em 2 clientes basta comparar princípios anonimizados.
