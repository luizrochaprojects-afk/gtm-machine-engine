---
name: syndie-flow-builder
description: Monta a campanha de LinkedIn da rodada na Syndie. Escreve o prompt e as mensagens (até 1000 caracteres, só variáveis nativas), passa pela juiz-de-copy e leva ao gate H2; gera o fluxo JSON no formato de importação 3.0.0 a partir dos fluxos de referência e valida com scripts/validate_syndie_flow.py; gera o CSV de upload a partir de 03-contatos.csv com anti-join de URLs; escreve o passo a passo de importação; depois da importação, compara nó a nó o fluxo exportado da Syndie com o gerado. Use na etapa E6, quando o operador disser "monta a Syndie", "fluxo da Syndie", "prompt da Syndie", "CSV da Syndie", "campanha de LinkedIn da rodada", "compara o fluxo importado", "roda a syndie-flow-builder". A campanha fica pausada até o H3.
---

# syndie-flow-builder

Gera tudo que a campanha de LinkedIn de uma rodada precisa na Syndie: prompt e mensagens, fluxo JSON, CSV de leads e o passo a passo de importação. A Syndie não tem API conhecida: a skill entrega arquivos, o operador importa pela interface, e a skill confere depois se o que entrou na Syndie é o que foi gerado.

A skill não sabe quem é o cliente. Perfil de remetente, convites por semana, cadência, ofertas e segmentos vêm do `cliente.yaml`; voz, história do remetente e o que não pode ser dito vêm da `estrategia/doutrina-cliente.md`.

**A campanha nunca é iniciada por esta skill.** Ela fica criada e pausada até "H3 aprovado" no `05-qa-lancamento.md`, e quem inicia é o operador.

## Antes de começar: o que ler

| # | Arquivo | O que tirar dele |
|---|---|---|
| 1 | `adapters/syndie/README.md` | Limites da ferramenta, ordem do anti-join, passo a passo de importação |
| 2 | `schemas/syndie-flow.schema.json` | Formato 3.0.0, tipos de nó, `x-limites` |
| 3 | `schemas/syndie-upload.schema.md` | Colunas do CSV, nativas e de controle, regras de entrada |
| 4 | `skills/syndie-flow-builder/references/schema.md` | O que cada tipo de nó faz e quais campos de `data.config` ele usa |
| 5 | `skills/syndie-flow-builder/references/fluxo-convite-dm.json` e `fluxo-lembrete.json` | Fluxos de referência anonimizados: estrutura de nós, arestas, delays e `meta` de cada tipo |
| 6 | `estrategia/doutrina-cliente.md` | Voz do remetente, história real dele, registro no LinkedIn, o que nunca dizer |
| 7 | `doutrina/outbound.md` | Seção "LinkedIn: primeiro toque", seção "Frases banidas e QA de envio" e a regra do prompt pra IA de ferramenta (seção "Cold email") |
| 8 | `doutrina/escrita.md` e `doutrina/ai-tells.md` | Forma, verdade, travessão, acentuação |
| 9 | `estrategia/master-copy/<oferta>.md` e `segmentos/<segmento>/` | A dor e o ângulo aprovados no H0 |

E também: `cliente.yaml` (`stack.linkedin`, `remetentes.perfil_linkedin`, `cadencia.linkedin_passos`, `ofertas`, `gates.H2`, `gates.pessoas`), `rodadas/<rodada>/03-contatos.csv` e os vereditos da rodada (`02-validacao.xlsx` ou o JSON de vereditos), e os diffs H2 de Syndie de rodadas anteriores (`aprendizado/diffs/*-H2-syndie.md`): o que o operador já cortou não volta.

## Pré-condições

Pare e diga ao operador o que falta se:

- `stack.linkedin` não é `syndie`. Com `manual`, gere só o CSV de leads e as mensagens em `04-linkedin-manual.md`; com `nenhum`, não há o que fazer;
- não existe `aprendizado/diffs/<rodada>-H1-lista.md` com resultado aprovado;
- `03-contatos.csv` não existe ou não tem nenhum contato com canal `linkedin` ou `ambos`;
- `remetentes.perfil_linkedin` está vazio no `cliente.yaml`;
- os fluxos de referência em `references/` não existem (não invente o formato de `meta` de um nó: ele só sai da referência).

## Passos

### 1. Fechar a descrição do fluxo

Entrada: a descrição do fluxo dada pelo operador (etapas, delays, ramos por aceite e por resposta). Se ele não der, proponha a partir de `cadencia.linkedin_passos` e da referência mais próxima:

- `fluxo-convite-dm.json`: visita ao perfil, convite, espera pelo aceite; aceitou → DM 1, espera resposta; não respondeu → DM 2; não aceitou → retira o convite depois do prazo.
- `fluxo-lembrete.json`: estrutura de lembrete descrita em `references/schema.md`.

Mostre a descrição como tabela (ordem, tipo de nó, delay, ramo sim, ramo não, texto usado) e peça confirmação antes de seguir. Regras de desenho que não se negociam:

- No máximo 2 DMs depois do aceite; depois disso, nutrir pelo feed (curtir, comentar), sem mensagem nova (`doutrina/outbound.md`).
- Follow-up entre 4 e 6 dias depois da DM anterior.
- Nenhum ramo reenvia mensagem a quem recebeu e não respondeu além da DM 2. Ramo "não respondeu" termina em tag ou em nó de feed, nunca em DM 3.
- Um fluxo por grupo de segmento e oferta. Se `03-contatos.csv` tiver mais de um grupo, cada grupo ganha seu fluxo e seu CSV.

### 2. Escrever o prompt e as mensagens

Se já existe `aprendizado/diffs/<rodada>-H2-syndie.md` com resultado aprovado, use a versão aprovada e pule pro passo 4. Senão, escreva aqui, nó a nó, pra cada nó que tem texto (`send_invite`, `send_followup`, `comment_post`):

- **`customGuidelines`** (prompt da IA): até 1000 caracteres. Descreve o que a mensagem precisa ser (o problema que a pessoa vive, a pergunta de sim ou não barato, o registro), não referencia campo de CSV e não manda pesquisar a pessoa ou a empresa: a Syndie só enxerga 1 post recente, quando existe. Se usar o post (`mentionPost: true`), mande reagir ao detalhe concreto, nunca à tese, e mande não mencionar post quando não houver detalhe concreto.
- **`message`**: texto fixo ou de fallback. No convite, até 300 caracteres. Prefira mensagem fixa escrita à mão com só `{{first_name}}` e deixe pra IA o menor vão possível.
- **Variáveis:** só `{{first_name}}`, `{{last_name}}`, `{{company}}`, `{{title}}`. Nada de `{{primeiro_nome}}`, `{{empresa}}` ou `{{primeira_frase}}`: coluna custom não é populada.
- **Registro de LinkedIn:** contração informal aceita ("pra", "tá"), nunca corporativo. Sem travessão. Acentuação completa.
- **Sem detalhe concreto, convite sem nota** é uma opção válida (`[hipótese]` da doutrina). Proponha quando o segmento não tiver fato que sustente a nota.
- História do remetente só se estiver escrita na `doutrina-cliente.md`. Nunca inventar biografia.

Conte os caracteres com `len()` em Python sobre o texto final (com as variáveis como estão escritas), não a olho. Grave o rascunho em `rodadas/<rodada>/04-syndie-mensagens.md`, uma seção por nó com: id previsto do nó, campo, texto, contagem de caracteres.

### 3. Juiz e gate H2

1. Passe `04-syndie-mensagens.md` pela `juiz-de-copy`. Máximo 3 rodadas de revisão. O que o juiz não conseguiu consertar vai numa seção `## Notas do juiz` no fim do arquivo.
2. Confira de novo limite de caracteres e variáveis depois de cada revisão.
3. Apresente ao dono do gate H2 (`gates.H2`): as mensagens por nó, a contagem e as notas do juiz. Espere a aprovação ou a versão editada.
4. Salve o diff em `aprendizado/diffs/<rodada>-H2-syndie.md` no formato de `schemas/diff.template.md`: peça `syndie`, bloco "Versão da máquina" com o texto que chegou ao gate, bloco "Versão aprovada" com o que foi aprovado (ou "igual à versão da máquina"), notas do operador uma linha por mudança. Sem diff salvo, não siga.

### 4. Montar o JSON

1. Copie a referência mais próxima como ponto de partida. **Nunca edite o arquivo em `references/`**; trabalhe numa cópia.
2. Monte o fluxo com um script Python curto (`json.dump(..., ensure_ascii=False, indent=2)`), nunca editando JSON como texto solto.
3. Pra cada nó:
   - `id` = `<tipo>-<número>`, números únicos na ordem do fluxo.
   - `data.meta` copiado da referência do mesmo tipo de nó, sem mudar nada.
   - `data.config` com o delay (`delayValue`, `delayUnit`) e os campos do tipo (ver `references/schema.md`); `language: "portuguese"`; os textos aprovados no H2 exatamente como aprovados.
   - `data.delayMode` como na referência.
   - Condição (`linkedin_request_accepted`, `is_replied_on_linkedin`): `data.branches` com `yes` e `no` e `data.mergeNodeId` apontando pro `merge` que fecha os ramos. Nos outros nós, `mergeNodeId: null`.
   - `add_update_tag` com tag nova: `tagId` vazio e `tagName` preenchido; anote a tag no passo a passo pra ser criada na interface.
   - `position` seguindo o desenho da referência (colunas por ramo), pra o fluxo abrir legível.
4. Pra cada aresta: `id` = `<source>-<target>`, `type: "buttonedge"`; saindo de condição, `sourceHandle` `yes` ou `no`, `data.label` `Yes` ou `No` e `data.pluscontext.type` `branch-yes` ou `branch-no`; entrando num `merge`, `targetHandle` com o ramo de origem; nas outras, `pluscontext.type: "edge"`.
5. `version: "3.0.0"`; `metadata.exportedAt` = agora em ISO 8601 com milissegundos e `Z`; `metadata.nodeCount` e `edgeCount` recontados do próprio arquivo.
6. Grave em `rodadas/<rodada>/04-syndie-flow.json` (ou `04-syndie-flow-<grupo>.json`).

### 5. Validar até passar

```bash
python scripts/validate_syndie_flow.py rodadas/<rodada>/04-syndie-flow.json
```

- Saída 0: segue.
- Saída 1: leia cada erro (aresta quebrada, nó solto, prompt acima de 1000, variável não nativa), corrija no script de montagem, gere de novo e valide de novo. Texto aprovado no H2 que estoura limite não é cortado por conta própria: volta pro operador.
- Saída 2: arquivo ilegível. Gere de novo.
- Três tentativas sem passar: pare e mostre os erros ao operador.

### 6. Gerar o CSV de upload

1. De `03-contatos.csv`, fique só com canal `linkedin` ou `ambos`, `linkedin_url` preenchida e `entra_na_cadencia` diferente de `nao` (quando a coluna existir).
2. Normalize a URL: `https://www.linkedin.com/in/<slug>`, sem barra final, sem parâmetros. URL de Sales Navigator (`/sales/`) ou de empresa (`/company/`) não entra; vai pro removidos com motivo `url_invalida`.
3. Monte as colunas nativas na ordem do schema (`first_name`, `last_name`, `linkedin_url`, `company`, `title`) e as de controle que houver dado (`dominio`, `papel`, `trilha`, `tier`, `veredito_conta`, `score_conta`, `email`, `email_status`, `fonte`, `ordem_na_conta`, `cargo_checado_em`). `company` sai do `company_name` do veredito, sem "Ltda", "S.A.", "Eireli". `first_name` com acento, sem sobrenome.
4. **Anti-join com snapshot fresco do ledger.** Exporte agora as abas `supressao`, `contas`, `contatos` e `toques` (regras de leitura em `adapters/google-sheets/README.md`) pra `rodadas/<rodada>/_snapshot/<AAAA-MM-DD-HHMM>/<aba>.csv` e rode:

   ```bash
   python scripts/suppress.py --lista <upload-bruto>.csv --ledger-dir rodadas/<rodada>/_snapshot/<AAAA-MM-DD-HHMM> \
       --saida rodadas/<rodada>/04-syndie-upload.csv --removidos rodadas/<rodada>/04-syndie-removidos.csv \
       --col-dominio dominio --col-email email --col-linkedin linkedin_url
   ```

5. Um arquivo por grupo de segmento e oferta. Conta com trilha `incerta` não entra: volta pro H1.
6. Confira: UTF-8 sem BOM; nenhuma URL repetida; no máximo 3 contatos por conta; total de linhas cabe em `convites_por_semana` do perfil (se não couber, avise quantas semanas a campanha leva).

### 7. Escrever o passo a passo de importação

Grave `rodadas/<rodada>/04-syndie-importacao.md` a partir do passo a passo de `adapters/syndie/README.md`, preenchido com os valores desta rodada: nome da campanha, perfil de envio, arquivo do fluxo, número de nós e arestas, arquivo do CSV, número de leads, tags a criar, removidos no anti-join por motivo. Termine com o lembrete: campanha pausada até o H3, e o fluxo exportado volta pra comparação.

### 8. Comparar o fluxo importado com o gerado

Depois que o operador importar, peça o JSON exportado da Syndie e salve em `rodadas/<rodada>/04-syndie-flow-exportado.json`. A `qa-lancamento` também chama este passo.

1. Rode `validate_syndie_flow.py` no exportado. Erro no exportado é divergência.
2. **Não compare por `id`**: a importação pode renumerar. Percorra os dois fluxos a partir do nó sem aresta de entrada, seguindo as arestas em ordem (ramo `yes` antes do `no`), e emparelhe os nós pela posição no percurso.
3. Compare cada par:

   | O quê | Divergência bloqueia? |
   |---|---|
   | Tipo do nó | sim |
   | `delayValue`, `delayUnit`, `delayMode` | sim |
   | Ramos da condição e destino de cada ramo | sim |
   | `customGuidelines`, `message`, `customComment` (texto inteiro, caractere a caractere) | sim |
   | `language`, `mentionPost`, `useAI`, `tagName` | sim |
   | Contagem de nós e de arestas | sim |
   | Outros campos de `config` (tom, tamanho, foco) | sim, se diferente do gerado |
   | `id`, `position`, `measured`, `selected`, `exportedAt`, `tagId`, `animationState` | não (só anota) |

4. Grave `rodadas/<rodada>/04-syndie-comparacao.md`: data, arquivos comparados, resumo (nós e arestas de cada lado, divergências que bloqueiam, divergências anotadas) e uma tabela por divergência com posição no percurso, tipo, campo, valor gerado, valor exportado. Texto cortado aparece com os últimos 40 caracteres de cada lado.
5. Com divergência que bloqueia: diga ao operador o que corrigir na interface (ou reimportar) e repita este passo com o novo export.

## O que gravar e onde

| Arquivo | Quando |
|---|---|
| `rodadas/<rodada>/04-syndie-mensagens.md` | Passo 2 |
| `aprendizado/diffs/<rodada>-H2-syndie.md` | Passo 3 |
| `rodadas/<rodada>/04-syndie-flow.json` (ou `-<grupo>`) | Passo 4 |
| `rodadas/<rodada>/_snapshot/<AAAA-MM-DD-HHMM>/*.csv` | Passo 6 |
| `rodadas/<rodada>/04-syndie-upload.csv` (ou `-<grupo>`) e `04-syndie-removidos.csv` | Passo 6 |
| `rodadas/<rodada>/04-syndie-importacao.md` | Passo 7 |
| `rodadas/<rodada>/04-syndie-flow-exportado.json` e `04-syndie-comparacao.md` | Passo 8 |

Fim da execução: diga ao operador o que foi gerado, quantos leads entraram e saíram (por motivo), o resultado do validador e o próximo passo (importar, ou mandar o export pra comparação).

## Gates

- **H2:** nenhum JSON final sem o prompt e as mensagens aprovados e o diff salvo.
- **H3:** a campanha fica pausada. A skill nunca inicia, ativa ou retoma campanha, nem pelo navegador.

## Armadilhas

- **Prompt que manda pesquisar.** A Syndie não pesquisa. "Cite a notícia recente da empresa" gera invenção.
- **Variável custom.** `{{primeiro_nome}}` e `{{empresa}}` aparecem em fluxos antigos e em CSVs legados. Não funcionam na mensagem.
- **Limite de 1000 ainda não confirmado.** Fluxos exportados que já rodaram tinham prompts maiores. Até a confirmação registrada no `adapters/syndie/README.md`, 1000 é teto.
- **Texto em ASCII.** Copy de agente sai sem acento. Conferir por regex antes do juiz e antes de gravar o JSON.
- **Travessão** no texto ou no nome da campanha. Nunca.
- **URL de LinkedIn fora do padrão** não casa no anti-join e deixa passar quem já foi tocado.
- **Misturar grupos** numa campanha só: a mensagem de um segmento chega no outro.
- **Tag nova com `tagId` inventado.** Deixar vazio e criar na interface.
- **Montar o fluxo à mão por cima de uma importação que falhou.** Corrigir o JSON e reimportar; senão o export não bate com nada.
