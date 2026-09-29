# Referência: fluxo da Syndie (formato 3.0.0)

Como o JSON de importação da Syndie é montado, nó por nó. O contrato formal está em `schemas/syndie-flow.schema.json`; as regras que o JSON Schema não expressa são conferidas por `scripts/validate_syndie_flow.py`.

Os dois fluxos desta pasta (`fluxo-convite-dm.json` e `fluxo-lembrete.json`) foram derivados de dois fluxos exportados da Syndie que já rodaram. A estrutura (nós, arestas, delays, `meta`, `branches`, `position`) é a original; os textos foram trocados por exemplos de uma empresa fictícia, a Acme (plataforma de retenção para e-commerce), os ids foram renumerados e o `tagId` foi esvaziado.

## Arquivo

```json
{
  "version": "3.0.0",
  "metadata": {"exportedAt": "2026-10-01T00:00:00.000Z", "nodeCount": 20, "edgeCount": 22},
  "flow": {"nodes": [ ... ], "edges": [ ... ]}
}
```

- `version` é sempre `"3.0.0"`.
- `metadata.exportedAt` é ISO 8601 com milissegundos e `Z`.
- `metadata.nodeCount` e `metadata.edgeCount` precisam bater com o tamanho real de `flow.nodes` e `flow.edges`.

## Nó

Campos comuns a todo nó:

| Campo | O que é |
|---|---|
| `id` | `<tipo>-<número>`, ex.: `send_invite-1000000000002`. Único no fluxo. Um merge costuma repetir o número da condição que ele fecha (`is_replied_on_linkedin-1000000000011` e `merge-1000000000011`); o id inteiro continua único porque o prefixo muda. |
| `type` | Um dos 10 tipos abaixo. |
| `position` | `{x, y}` no canvas. `y` cresce para baixo. Nos fluxos de referência o ramo `yes` fica à esquerda (x negativo) e o `no` à direita. |
| `measured` | `{width, height}` do desenho: 274 × 74 em ação, 274 × 78 em condição, 15 × 15 em merge. |
| `selected` | `false`. |
| `data.meta` | Metadado de exibição do tipo (título, categoria, entradas, saídas, `styleKey`). Copiar do nó do mesmo tipo no fluxo de referência, sem mudar. |
| `data.config` | Configuração do passo: delay e parâmetros do tipo. |
| `data.mergeNodeId` | Em condição, o id do merge que fecha os dois ramos. Em ação, `null`. |
| `data.delayMode` | `fixed` em todos os nós dos fluxos de referência. As condições aceitam também `waitUntil` (ver `meta.delayModes`). |
| `data.branches` | Só em condição e merge: `[{"id": "yes", "label": "Yes", "colour": "#16a34a"}, {"id": "no", "label": "No", "colour": "#dc2626"}]`. |
| `data.animationState` | `"stable"`. |

O merge é diferente: não tem `meta`, `config`, `mergeNodeId` nem `delayMode`. Tem só `data.branches` e `data.animationState`, e leva `selectable`, `draggable` e `focusable` iguais a `false`.

## Delay

`config.delayValue` (inteiro) com `config.delayUnit` (`minutes`, `hours`, `days`). Em ação, é a espera antes de executar o passo, contada a partir do passo anterior. Em condição, é o prazo que a Syndie espera pelo evento (aceite, resposta) antes de decidir o ramo: se o evento acontece dentro do prazo, segue pelo `yes`; se o prazo vence, segue pelo `no`. Essa leitura da condição foi inferida dos fluxos exportados e dos valores usados (14 dias para aceite, 7 para resposta); confirmar na interface antes de depender de um prazo diferente.

## Tipos de nó

| Tipo | Categoria | O que faz | Campos de `config` além do delay |
|---|---|---|---|
| `profile_visit` | ação | Visita o perfil do LinkedIn do contato. Primeiro passo dos dois fluxos, 15 minutos depois da entrada. | nenhum |
| `send_invite` | ação | Envia o pedido de conexão, com nota ou sem nota. | `useAI`, `tone`, `formality`, `approach`, `focus`, `intention`, `callToAction`, `personalization` (seletores da IA da Syndie), `language` (`portuguese` ou `english`), `mentionPost`, `customGuidelines` (prompt da IA), `message` (nota base ou fallback, até 300 caracteres). `config` vazio (`{}`) = convite sem nota. |
| `linkedin_request_accepted` | condição | Pergunta se o convite foi aceito dentro do prazo. Dois ramos e `mergeNodeId`. | nenhum |
| `like_post` | ação | Curte o post recente do contato. | `useAI`, `postCount` (quantos posts), `recentPostWithin` (idade máxima do post, em dias). Pode vir só com `recentPostWithin`. |
| `comment_post` | ação | Comenta o post recente do contato. | `postCount`, `recentPostWithin`, `useAI`, `length` (ex.: `short(1 sentence)`), `commentTone`, `language`, `contentBlacklist`, `blackListCategories`, `contentType`, `priorityKeyword`, `commentStyle`, `customGuidelines` (prompt), `customComment` (comentário base ou fallback). |
| `withdraw_request` | ação | Retira o convite pendente, para poder convidar de novo depois. | nenhum |
| `send_followup` | ação | Envia DM para quem já é conexão. | `useAI`, `isFollowUp`, `messageLength` (ex.: `short`), `tone` (ex.: `casual`), `language`, `mentionPost`, `customGuidelines` (prompt), `message` (DM base ou fallback). |
| `is_replied_on_linkedin` | condição | Pergunta se o contato respondeu no LinkedIn dentro do prazo. Dois ramos e `mergeNodeId`. | nenhum |
| `add_update_tag` | ação | Troca a tag do lead na Syndie. | `tagId` (id da tag na conta; vazio no motor, a tag é criada ou escolhida na interface ao importar), `tagName`, `tagColor` (`#RRGGBB`). |
| `merge` | junção | Ponto onde os dois ramos de uma condição voltam a se encontrar. Não executa nada. | sem `config` |

Os campos de seletor da IA (`tone`, `formality` e afins) aparecem com os valores exportados (`Moderate`, `Approachable`, `Direct`, `Business`, `Networking`, `Subtle`, `Specific`); a lista completa de valores aceitos só está na interface.

## Condição, merge e ramos

- Toda condição tem exatamente duas arestas de saída: uma com `sourceHandle: "yes"` e outra com `sourceHandle: "no"`.
- Toda condição aponta, em `data.mergeNodeId`, para um merge que existe no fluxo.
- Todo merge recebe exatamente duas arestas: uma com `targetHandle: "yes"` (o fim do ramo yes) e outra com `targetHandle: "no"` (o fim do ramo no).
- Merges se encadeiam: quando uma condição está dentro do ramo de outra, o merge interno entra no merge externo como uma das duas pontas. O último merge é o fim do fluxo.

## Arestas

```json
{"id": "<source>-<target>", "source": "<id>", "target": "<id>", "type": "buttonedge",
 "sourceHandle": "yes",
 "data": {"label": "Yes", "pluscontext": {"type": "branch-yes", "sourceId": "<id>", "targetId": "<id>"}}}
```

| Aresta | `sourceHandle` | `targetHandle` | `data.label` | `data.pluscontext.type` |
|---|---|---|---|---|
| entre ações | não tem | não tem | não tem | `edge` |
| saindo de condição, ramo yes | `yes` | não tem | `Yes` | `branch-yes` |
| saindo de condição, ramo no | `no` | não tem | `No` | `branch-no` |
| entrando num merge | não tem | `yes` ou `no` | não tem | não tem: a aresta sai sem `data` nos fluxos exportados |

- `type` é sempre `buttonedge`.
- `id` é `<source>-<target>`.
- `pluscontext.sourceId` e `pluscontext.targetId` repetem `source` e `target`.

## Os dois fluxos de referência

Os dois têm o mesmo desenho, 20 nós e 22 arestas. Mudam os textos:

- `fluxo-convite-dm.json`: convite com nota curta, DM 1 que abre conversa sobre recompra e cupom, DM 2 com uma faceta nova do mesmo problema.
- `fluxo-lembrete.json`: mesmo desenho com o ângulo de lembrete de reposição (o cliente fica sem produto antes do lembrete chegar), DM 2 oferecendo uma leitura do intervalo de recompra.

Desenho (delay entre parênteses; condição termina em `?`):

```
profile_visit (15 min)
└─ send_invite, nota com IA (1 dia)
   └─ linkedin_request_accepted? (espera 14 dias) ............ fecha em merge M1
      ├─ yes: like_post (2 dias)
      │       └─ comment_post (15 min)
      │          └─ send_followup DM 1 (1 dia)
      │             └─ is_replied_on_linkedin? (espera 7 dias) .... fecha em merge M2
      │                ├─ yes: add_update_tag "Follow Up Required" (15 min) → M2 [yes]
      │                └─ no:  like_post (3 dias)
      │                        └─ send_followup DM 2 (1 dia)
      │                           └─ is_replied_on_linkedin? (espera 7 dias) .... fecha em merge M3
      │                              ├─ yes: add_update_tag "Follow Up Required" (15 min) → M3 [yes]
      │                              └─ no:  add_update_tag "Cold Lead" (15 min) → M3 [no]
      │                              M3 → M2 [no]
      │                M2 → M1 [yes]
      └─ no:  like_post (2 dias)
              └─ withdraw_request (1 dia)
                 └─ send_invite sem nota (config vazio)
                    └─ like_post, posts de até 14 dias (1 dia) → M1 [no]
M1 = fim do fluxo
```

Leitura: quem não aceita em 14 dias recebe uma curtida, tem o convite retirado e ganha um segundo convite sem nota, seguido de outra curtida, e o fluxo termina ali. Quem aceita recebe curtida, comentário e até duas DMs; quem responde ganha a tag de acompanhamento humano, e quem não responde a nenhuma das duas ganha a tag de lead frio. Depois da DM 2 sem resposta o fluxo para: nada mais é enviado àquele contato.

Ids nos arquivos: `fluxo-convite-dm.json` usa `1000000000001` a `1000000000018`; `fluxo-lembrete.json`, `2000000000001` a `2000000000018`. A numeração segue a dos exportados de origem, que não é estritamente a ordem do fluxo (a DM 1 tem número maior que a condição que vem depois dela). Para um fluxo novo, qualquer sequência serve desde que os ids sejam únicos e as arestas, o `mergeNodeId` e o `pluscontext` sejam atualizados juntos.

## Limites

- `customGuidelines`: até 1000 caracteres, em qualquer nó (`send_invite`, `send_followup`, `comment_post`).
- `message` do `send_invite` (nota de convite): até 300 caracteres.
- Variáveis: só as nativas `{{first_name}}`, `{{last_name}}`, `{{company}}`, `{{title}}` em `message`, `customGuidelines` e `customComment`. Coluna custom do CSV de upload não é populada pela Syndie (ver `schemas/syndie-upload.schema.md`). Chave simples como `{first_name}` também é erro.
- Os limites e a lista de variáveis moram em `x-limites` do schema; o validador lê de lá.

**A confirmar na interface:** nos fluxos exportados de origem, os dois `send_followup` do primeiro fluxo tinham `customGuidelines` bem acima de 1000 caracteres (mais de 4000) e mesmo assim foram exportados. Ou a Syndie aceita prompt maior do que o limite documentado, ou corta o excedente sem avisar. Até alguém confirmar na interface, o motor trata 1000 como limite duro.

## Regras para gerar um fluxo novo

1. Partir de um dos dois fluxos de referência e mudar só `customGuidelines`, `message`, `customComment`, delays e tags. Mudar o desenho (acrescentar ou remover nó) exige atualizar arestas, `mergeNodeId`, `pluscontext` e as contagens em `metadata`.
2. Deixar `tagId` vazio e escolher ou criar a tag na interface ao importar.
3. Escrever os textos seguindo `doutrina/outbound.md` (seção de LinkedIn): convite sem pitch, uma pergunta só, sem "Vi que" e afins.
4. Rodar `python scripts/validate_syndie_flow.py <fluxo.json>` antes de importar. Sai com 0 quando o fluxo está pronto.
