---
name: validar-lista
description: "Qualifica as contas de uma rodada contra o gabarito de ICP do cliente ativo, com pesquisa web real por conta: veredito (P0, lista, nutrir, fora), score, tier, trilha de oferta, evidência com URL, tecnografia e primeira frase, mais verificação adversarial nas contas de score alto e revisão humana no gate H1. Use quando o operador pedir pra validar, qualificar, limpar, pesquisar ou dar veredito numa lista de contas, rodar a qualificação da rodada, 'quais dessas são ICP', 'roda essas empresas', 'valida o lote', 'prepara a lista pro H1' ou 'pesquisa essas contas', mesmo sem dizer 'validar'."
---

# Validar lista

Etapa E2. Transforma a lista crua da rodada numa fila de contas com veredito sustentado por evidência. O valor está em **reprovar os falsos positivos antes de gastar enrich e sequência**: decidir quem abordar, por qual trilha e com que fato.

A skill não sabe quem é o cliente. Gabarito, ofertas, personas, tecnografia alvo e regras de voz vêm do workspace ativo (`clientes/<slug>/`). O score, o veredito, o tier e a trilha saem de um cálculo fixo no script do workflow a partir dos critérios que os agentes marcaram; o agente pesquisa e marca, não dá nota.

## Ler antes

1. `cliente.yaml`: `ofertas`, `personas`, `tecnografia_alvo`.
2. `estrategia/gabarito-icp.md` (formato em `schemas/gabarito.schema.md`). Sem as quatro seções obrigatórias, ou com critério sem `id`, `papel`, `como verificar` ou `fonte aceita`, parar e avisar.
3. `estrategia/ofertas/<id>.md` e `estrategia/roteamento.md`, se existirem: o que cada oferta resolve e como se escolhe a trilha.
4. `estrategia/doutrina-cliente.md`: proibidos, números autorizados, o que não pode ser dito.
5. `doutrina/outbound.md` (seções "A linha de abertura personalizada" e "Sinais e listas") e `doutrina/producao-com-agentes.md`.
6. `aprendizado/diffs/*-H1-lista.md` das rodadas anteriores: vereditos que o operador mudou e por quê. Viram exemplos de calibração no prompt.
7. `references/workflow-validacao.js` e `references/verificacao-vaga-linkedin.md`.

## Entradas

- `rodadas/<rodada>/01-lista-crua.csv` (da `montar-tam`) ou qualquer CSV com `domain` e `company_name`. Lista solta de nomes sem domínio: resolver o domínio antes (busca no site ou `apollo_organizations_lookup`, gratuita) e marcar `obs` "domínio resolvido na validação".
- O lote: linhas da lista a validar (20 a 40 contas; o primeiro é o piloto de 10).
- Gatilho da rodada, se houver (ex.: sequência de vaga). Define se a verificação de vaga no LinkedIn roda.

## Passos

### 1. Montar os dados do workflow

Montar o objeto `DADOS` descrito no topo de `references/workflow-validacao.js` e gravar em `rodadas/<rodada>/02-dados-workflow.json` (sem o campo `items`, que muda por lote):

- **`gabarito`**: uma entrada por critério da tabela do gabarito, com `id`, `nome`, `papel`, `oferta` (id da oferta pros critérios de `#### Oferta <id>`; `null` pra audiência comum), `como_verificar`, `fonte_aceita`, `peso`, `validade`. `faixas`, `teto_sinais` e `limiar_adversarial` do gabarito ou o padrão do motor (80/60/40, +20, 60). `tier`: a regra do gabarito traduzida em lista ordenada de `{tier, vereditos, exige_dimensiona}`; sem regra, o padrão do script. `regra_trilha`: o texto do gabarito.
- **`cliente`**: `definicao_icp` = a definição em uma frase do gabarito; `o_que_vende` = uma frase do que o cliente vende (das ofertas).
- **`ofertas`**: `id`, `nome`, `porta_de_entrada` do `cliente.yaml` e um resumo de uma linha do arquivo da oferta.
- **`tecnografia_alvo`**: `nome`, `categoria`, `leitura` do `cliente.yaml`.
- **`regras_abertura`**: as regras da seção "A linha de abertura personalizada" de `doutrina/outbound.md`, as frases banidas, e os proibidos da `doutrina-cliente.md`.
- **`exemplos_reprovados`**: até 5 casos dos diffs H1 e H2 anteriores do workspace (linha reprovada, por quê, reescrita aprovada). Um exemplo reprovado com o erro nomeado calibra mais que dez regras. Os casos saem do workspace e voltam pra ele; nada disso entra no motor.
- **`hoje`**: a data de hoje, `AAAA-MM-DD` (o script não consegue ler o relógio).
- **`teto_busca`**: `{ "websearch": 2, "tool_calls": 10 }`.

Mostrar ao operador um resumo do gabarito lido: critérios por papel, soma dos pesos de fit por oferta (se não der 100, o script normaliza; avisar), faixas e limiar. Seguir só com o "ok".

### 2. Não pesquisar de novo

Juntar os `02-validacao.json` de rodadas anteriores. Conta com veredito de menos de 90 dias, mesmo gabarito (versão) e sem sinal novo na lista crua: reaproveitar o veredito, marcar `obs` "reaproveitado de <rodada>" e tirar do lote. Veredito mais velho ou de gabarito anterior: pesquisar de novo.

### 3. Piloto de 10 contas

Na primeira rodada de um segmento, ou com gabarito em versão nova, rodar os passos 4 a 8 em 10 contas e parar. Mostrar ao operador o placar, 3 vereditos completos (um alto, um fora, um incerto) e o que o piloto sugere mudar (critério que ninguém consegue verificar, peso que joga tudo pra nutrir, negativo que falta na busca). Mudança no gabarito é do operador, no H0. Escalar só com o "segue" do operador.

### 4. Tecnografia antes do veredito

Chamar a skill `detectar-tecnografia` sobre os domínios do lote. Ela grava `rodadas/<rodada>/02-tecnografia.csv`. Converter as linhas de cada domínio no formato do campo `tecnografia` do `schemas/veredito.schema.json` e pôr em `items[].tecnografia`.

### 5. Workflow de validação

Montar `items` do lote, um por conta: `domain`, `company_name`, `website` (`https://<domain>`), `linkedin_url`, `employees`, `industry`, `seed` (keywords, technologies e `short_description` da lista crua, mais conflitos suspeitos anotados, ex.: "palavras-chave de autopeças com descrição de moda") e `tecnografia`.

Copiar `references/workflow-validacao.js`, colar o `DADOS` com `modo: "validacao"` entre os marcadores `DADOS_EMBUTIDOS` e invocar o Workflow tool. Lotes de até ~120 contas por workflow; acima de ~16 agentes simultâneos o WebFetch devolve 429. Sem o Workflow tool, rodar um subagente por conta com o mesmo prompt e o mesmo schema de saída (`AVAL` no script) e aplicar o cálculo da seção "Como o veredito sai", marcando `obs` "calculado fora do workflow".

Gravar a saída em `rodadas/<rodada>/tmp/validacao-lote<n>.json`.

### 6. Verificação adversarial, em workflow separado

Com a saída do passo 5, rodar o mesmo script com `modo: "adversarial"` e `items = [{ veredito, website, seed }]` de todas as contas do lote. O script só manda pro agente as contas com score igual ou acima do `limiar_adversarial` e que não estão fora; as outras voltam como vieram, com `adversarial.rodou = false`.

O agente adversarial tenta derrubar cada gate e cada desqualificador duro, e aponta evidências falsas, exageradas ou de outra empresa. O script aplica:

- desqualificador duro confirmado ou gate ausente ⇒ `fora` (`derrubado`);
- gate incerto ⇒ um nível abaixo (`rebaixado`);
- evidência refutada vai pra `adversarial.fatos_refutados` e deixa de sustentar critério; critério que ficou sem evidência volta a `incerto` e o score é recalculado;
- `primeira_frase` apoiada em fato refutado é apagada e a conta vai pro H1.

Fato refutado é bloqueio: a `copy-email` e a `mapear-comite` não usam fato que esteja em `fatos_refutados`.

Gravar em `rodadas/<rodada>/tmp/adversarial-lote<n>.json`.

### 7. Vaga no LinkedIn (só com gatilho de vaga)

WebFetch no LinkedIn é bloqueado; "incerto" da pesquisa web não significa "não". Se o gatilho da rodada for vaga e o Chrome do operador estiver conectado, seguir `references/verificacao-vaga-linkedin.md` pra converter cada "incerto" do critério de vaga em sim ou não, com título, link e data. Atualizar no veredito o critério de vaga e a evidência (título, URL, data da checagem) e recalcular score e veredito pela seção "Como o veredito sai", anotando em `obs` "vaga checada no LinkedIn em <data>". Não rodar a adversarial de novo pra isso: ela pesquisaria a conta inteira outra vez. Sem Chrome, manter "incerto", avisar e oferecer a verificação depois.

### 8. Abertura

Rodar o script com `modo: "abertura"` e `items = [{ veredito, vertical }]` (vertical = `industry` da lista crua, ou a vertical que o gabarito usa). O script agrupa as contas P0 e lista por vertical (até 8 por grupo, pra forçar diferença entre contas parecidas), aplica os 5 testes da `doutrina/outbound.md` (intercambiabilidade, "e daí?", culpa, "como você sabe?", voz), reescreve o que reprovar e passa cada linha por uma leitura fria (agente que vê só a linha e a evidência). Linha que falha no QA mecânico (120 a 230 caracteres, 2 frases, sem travessão, sem "Vi que", acentuação) fica vazia; linha reprovada na leitura fria fica, com o problema em `obs` e `revisar_no_h1 = true`.

### 9. Validar e consolidar

1. Validar cada objeto contra `schemas/veredito.schema.json` com Python:

```python
import json
from jsonschema import Draft202012Validator
schema = json.load(open("<motor>/schemas/veredito.schema.json", encoding="utf-8"))
v = Draft202012Validator(schema, format_checker=Draft202012Validator.FORMAT_CHECKER)
for conta in vereditos:
    erros = [e.message for e in v.iter_errors(conta)]
    assert not erros, (conta["domain"], erros)
```

   Objeto inválido não entra: corrigir a causa (quase sempre agente que devolveu campo fora do formato) e rodar de novo só aquela conta.
2. Casar cada veredito com a linha canônica da lista pela chave `domain` normalizada; `company_name` é sempre o da lista, nunca o que o agente devolveu.
3. Acrescentar ao `rodadas/<rodada>/02-validacao.json` (lista de vereditos; conta repetida é substituída pela mais nova).
4. Conferir com regex antes de entregar: nenhuma `primeira_frase` com travessão, com "Vi que", fora de 120 a 230 caracteres ou sem acento onde deveria ter. QA mecânico verde é pré-condição, não aprovação.

### 10. Planilha de auditoria

Gerar `rodadas/<rodada>/02-validacao.xlsx` com openpyxl (fundo branco, texto preto, cabeçalho em negrito, primeira linha congelada, filtro ligado).

**Aba `contas`**: todas as contas validadas, inclusive `fora`, uma linha por conta, ordenadas por veredito (P0, lista, nutrir, fora) e score:

`domain`, `company_name`, `veredito`, `score`, `tier`, `trilha`, `is_anti_icp`, `motivo_anti_icp`, `hipotese` e `fonte` (da lista crua), um par de colunas por critério do gabarito (`<id>` com sim, não ou incerto; `<id>_fonte` com as URLs), `evidencias` (uma por linha na célula: `[i] fato · URL · confiança · data`), `tecnografia` (`ferramenta (tipo, confiança, leitura)`), `primeira_frase`, `fato_da_frase`, `adversarial` (resultado), `fatos_refutados`, `revisar_no_h1`, `obs`.

**Aba `resumo`**:

- Placar: quantas P0, lista, nutrir e fora, no total e por hipótese de ICP.
- Taxa de anti-ICP (contas com `is_anti_icp` ÷ total) e os motivos mais comuns.
- Resultado da adversarial: mantidos, rebaixados, derrubados, fatos refutados.
- Trilhas: quantas por oferta, `ambas` e `incerta`.
- **Diagnóstico**, quando "fora" passar de 40%: por que as contas caíram (gate ausente, qual desqualificador duro), e a proposta de ajuste na busca, escrita como mudança em `segmentos/<segmento>/busca-apollo.md` (negativo novo, porte, palavra-chave que troca, hipótese que sai). A proposta não altera a busca sozinha: vai pro operador aprovar na próxima `montar-tam`.

### 11. Revisão H1

1. Mostrar ao operador só as contas P0 e as com `revisar_no_h1 = true`, numa tabela curta: domínio, veredito, score, trilha, fato principal com URL, `primeira_frase`, motivo da revisão (`obs`). As outras seguem como estão.
2. O operador aprova, muda veredito ou trilha, reescreve a frase ou marca `fora`. A skill aplica no `02-validacao.json` mantendo o objeto válido no schema: conta levada a `fora` fica com score no máximo 39, `tier` nulo e `primeira_frase` vazia; conta promovida a `lista` sem frase roda de novo o passo 8 só pra ela; `obs` ganha "H1: <veredito da máquina> → <veredito aprovado> por <papel> em <AAAA-MM-DD>".
3. Gravar `aprendizado/diffs/<rodada>-H1-lista.md` no formato de `schemas/diff.template.md`: bloco da máquina com a tabela das linhas revisadas (domínio, veredito, score, trilha, `primeira_frase`) como chegou ao gate; bloco aprovado com a mesma tabela depois da revisão (ou "igual à versão da máquina"); notas com uma linha por veredito alterado (`domínio · veredito da máquina → aprovado · motivo`); resultado `aprovado sem edição`, `aprovado com edição` ou `reprovado`.
4. Gerar de novo o `02-validacao.xlsx` com os vereditos aprovados.

A `mapear-comite` só roda com esse diff gravado.

## Como o veredito sai

Cálculo fixo do script (`pontuar` em `references/workflow-validacao.js`), igual pra todo cliente; o gabarito só muda os números.

1. **Fit por oferta:** soma dos pesos dos critérios `gate`, `qualifica` e `dimensiona` marcados `sim` (audiência comum + os da oferta), dividida pela soma dos pesos do mesmo conjunto, vezes 100. Vale a oferta de fit mais alto entre as possíveis (nenhum gate da oferta ausente). `incerto` não soma.
2. **Bônus de sinais:** peso de cada `sinal` marcado `sim` com evidência datada dentro da `validade`, até o `teto_sinais`. Sinal sem data ou vencido não soma e fica anotado.
3. **Score** = fit + bônus, até 100. **Veredito** pelas faixas.
4. **Regras duras:** desqualificador `duro` confirmado ⇒ `fora` com `is_anti_icp`; `gate` comum ausente ⇒ `fora`; nenhuma oferta com gates atendidos ⇒ `fora`; `gate` incerto ⇒ no máximo `lista` e revisão no H1; cada desqualificador de `validacao` confirmado ⇒ um nível abaixo. O score é cortado no teto da faixa do veredito final (`fora` fica no máximo 39).
5. **Tier:** primeira regra de `tier` que casa com o veredito (e com todos os `dimensiona` em `sim`, quando a regra exige). `fora` ⇒ `null`.
6. **Trilha:** cliente com uma oferta ⇒ essa oferta. Com mais: uma só oferta com todos os gates em `sim` ⇒ ela; as duas de um cliente de duas ofertas ⇒ `ambas`; senão a sugestão do agente, se estiver entre as elegíveis; senão `incerta`.
7. **`revisar_no_h1`:** P0, gate incerto, domínio que talvez não seja da empresa, qualquer mudança na adversarial, abertura reprovada.

## O que grava e onde

| Arquivo | Conteúdo |
|---|---|
| `rodadas/<rodada>/02-dados-workflow.json` | Gabarito, ofertas e regras injetados no workflow (a foto do que a máquina usou) |
| `rodadas/<rodada>/02-tecnografia.csv` | Saída da `detectar-tecnografia` |
| `rodadas/<rodada>/tmp/*.json` | Saída crua de cada workflow, por lote |
| `rodadas/<rodada>/02-validacao.json` | Lista de vereditos no formato de `schemas/veredito.schema.json` |
| `rodadas/<rodada>/02-validacao.xlsx` | Auditoria: aba `contas` e aba `resumo` |
| `aprendizado/diffs/<rodada>-H1-lista.md` | Diff do gate H1 |

## Armadilhas

- **O Apollo mente.** Descrição colada na empresa errada, setor errado, homônimo, domínio de outra empresa. Resolver o negócio real antes de confiar na semente; `dominio_confere` diferente de `sim` vai pro H1.
- **Agência é o falso positivo nº 1** em lista com sinal de ferramenta ou de vaga: contrata pra entregar ao cliente dela. Se o gabarito não tiver o desqualificador, o piloto mostra; propor no H0.
- **Marca forte que só vende pra distribuidor** passa por lookalike e cai na validação (sem checkout próprio não há base própria).
- **Enterprise com sinal perfeito** continua fora do padrão se o gabarito diz que decisão por comitê desqualifica.
- **"incerto" não é "não".** Principalmente em LinkedIn, que bloqueia fetch. Incerto vira revisão no H1, nunca reprovação automática de critério.
- **Fato sem URL não entra.** Nem em evidência, nem em primeira frase.
- **Verificação adversarial dentro do mesmo pipeline** é a primeira coisa cortada quando o orçamento de busca acaba. Sempre workflow separado.
- **Orçamento de busca:** cerca de 200 WebSearch por sessão, compartilhado entre os agentes. Estourou no meio: parar, consolidar pelo journal de cada run, marcar em `obs` o que ficou sem verificação e nunca misturar linha degradada com linha pesquisada.
- **Agente devolve nome de conta modificado.** Casar sempre por `domain`.
- **Copy de agente sai sem acento.** O QA mecânico do script pega os casos comuns; conferir por regex no fim.
- **Script do workflow:** `Date.now()`, `Math.random()` e `new Date()` sem argumento não existem, por isso `hoje` vai nos dados. Se os dados forem por `args` e chegarem como texto, o script faz `JSON.parse`.
- **Resposta grande de ferramenta:** salvar em arquivo e ler com Python, não reler inteira no contexto.
