# Adaptador de CRM: Account Guardian

Como a máquina copia contas e contatos de uma rodada do ledger pro Account Guardian, quando o `cliente.yaml` tem `crm: account-guardian`. Quem roda: a `registrar-ledger`, depois do lançamento. A `qa-lancamento` usa a busca do Guardian pra conferir duplicata antes do H3.

Regras que valem sempre:

- **Direção só ledger → CRM na v0.1.** Mudança feita no Guardian (estágio, dono, contato novo) não volta pro ledger. Sincronização de volta é S2.
- **Não bloqueia o lançamento.** Se o Guardian estiver fora, recusar a escrita ou não tiver acesso, a rodada segue; o adaptador gera os CSVs e o passo a passo, e a pendência vai pro relatório da `registrar-ledger`.
- **O banco impõe o framework de vendas.** O Guardian recusa escrita que pula etapa ou deixa item de qualificação sem resposta. Erro desse tipo é o processo funcionando: registrar, corrigir o dado de origem ou devolver pro operador. Nunca procurar outro caminho de escrita, nunca passar `allow_duplicate: true` sem o operador pedir, nunca mover estágio além de `working`.
- **No Guardian a conta é o negócio.** Não existe tabela de oportunidades separada: estágio de pipeline, dono e checklist de qualificação moram na conta.

## O que o Account Guardian aceita

- Import em lote de **contas** só pela interface, e só pra quem tem papel de fundador. O import leva nome, segmento e notas; domínio e site são descartados.
- **Contatos** entram um a um, pela interface ou pela ferramenta `guardian_create_contact` do MCP. Não existe import em lote de contatos.
- A checagem de duplicata é por **nome**, com similaridade aproximada. Não usa domínio.
- Estágios válidos do pipeline: `target`, `working`, `paused`, `disqualified`, `discovery_call`, `qualified_opportunity`, `business_case`, `sign_off`, `closed_lost`, `closed_won`, e os estágios de cliente.

Consequências:

1. A conta no Guardian **não guarda domínio**. O único jeito de casar conta do ledger com conta do Guardian é pelo nome. Homônimo e nome escrito diferente ("Acme" e "Acme Comércio") são o risco principal. Toda correspondência ambígua passa pelo operador.
2. O import pela interface leva nome, segmento e notas. O domínio, a rodada e a trilha vão dentro das notas, pra que o time ache a conta e saiba de onde ela veio.
3. Contatos entram pelo MCP (um a um) ou à mão.

## Caminho A: CSV de contas + passo a passo (padrão, sem risco)

A `registrar-ledger` gera, em `rodadas/<rodada>/crm/`:

### `account-guardian-contas.csv`

UTF-8 com BOM, separador vírgula. Uma linha por conta lançada na rodada (estágio `Working` no ledger).

| Coluna do CSV | Vem do ledger (aba `contas`) | Observação |
|---|---|---|
| `name` | `empresa` | Nome canônico, sem "Ltda" ou "S.A." |
| `segment` | `segmento` | Slug do segmento |
| `notes` | montado | `dominio: <dominio> · rodada: <rodada> · trilha: <trilha> · veredito: <veredito> · tier: <tier> · fato: <fato_abordagem> · fonte: <fonte_url>` |

Sem coluna `arr`: a máquina não sabe receita de conta em prospecção.

### `account-guardian-contatos.csv`

UTF-8 com BOM. Uma linha por contato lançado na rodada. Serve pro cadastro manual ou de referência pro caminho B.

| Coluna do CSV | Vem do ledger (aba `contatos`) | Campo no Guardian |
|---|---|---|
| `conta` | `empresa` da conta (aba `contas`, pelo `dominio`) | conta onde o contato entra |
| `dominio` | `dominio` | só referência |
| `name` | `nome` | `name` |
| `role` | `cargo` | `role` (cargo) |
| `email` | `email` | `email` |
| `linkedin_url` | `linkedin_url` | `linkedin_url` |
| `role_in_deal` | `papel`: `decisor` → `decision_maker`, `champion` → `champion`, `influenciador` → `influencer` | `role_in_deal` |
| `deal_engagement` | `approached` quando já houve toque enviado; `identified` antes disso | `deal_engagement` |

### Passo a passo pro operador (fundador no Guardian)

1. Abrir o Guardian em Contas → Importar (`/accounts/import`).
2. Subir `account-guardian-contas.csv`. Conferir que `name`, `segment` e `notes` foram reconhecidas; nenhuma outra coluna deve aparecer.
3. Estágio inicial: `working` (corresponde ao `Working` do ledger). Dono: quem vai cuidar das contas. Fonte: `gtm-machine`.
4. Na tela de duplicatas, pra cada candidato: se for a mesma empresa, **usar a existente** (não criar outra); se for outra empresa com nome parecido, criar; se a existente estiver em estágio de venda ou de cliente, **pular** e avisar a máquina (a conta não devia estar na rodada; a `qa-lancamento` deveria ter pego).
5. Importar e anotar o resumo (inseridas, puladas, casadas, erros) no relatório da `registrar-ledger`.
6. Contatos: cadastrar pelo caminho B, ou à mão a partir de `account-guardian-contatos.csv`.

## Caminho B: criação uma a uma pelo MCP do Guardian

Mais lento, mas leva os contatos e não depende da tela de import, que é restrita a fundador (se o papel do usuário pode criar conta pelo MCP, o `guardian_whoami` e a primeira chamada dizem). A máquina age como o usuário logado, com as permissões dele. Mostrar o lote ao operador e pedir confirmação antes da primeira escrita: é o CRM do cliente.

1. `guardian_whoami`: conferir organização e papel. Se a organização não for a do cliente, parar.
2. `guardian_list_pipeline_stages`: conferir que `working` existe. Se não existir, parar e avisar (o enum mudou).
3. Pra cada conta do CSV:
   1. `guardian_search_accounts` com `query` = `name`. Candidato com nome igual ou quase igual: mostrar ao operador (nome, estágio, dono) e pedir decisão. Sem candidato: seguir.
   2. Conta nova: `guardian_create_account` com `name`, `segment`, `pipeline_stage: "working"`, `source: "gtm-machine"`, `tags: ["<rodada>", "<trilha>"]`. Se o banco recusar `working` na criação, criar em `target` e registrar no relatório; não tentar transição.
   3. Conta existente em `target`, `working`, `paused` ou `closed_lost`: usar o `id` dela, sem mudar estágio. Em estágio de venda ou de cliente: não tocar e avisar.
4. Pra cada contato da conta:
   1. `guardian_list_contacts` com o `account_id`: se já houver contato com o mesmo email ou a mesma URL de LinkedIn, não criar outro.
   2. `guardian_create_contact` com `account_id`, `name`, `role`, `email`, `linkedin_url`, `role_in_deal`, `deal_engagement`.
5. Erro de qualificação ou de estágio devolvido pelo banco: anotar conta, ferramenta e mensagem, seguir pra próxima. Não repetir a chamada com outro parâmetro pra contornar.
6. Gravar `rodadas/<rodada>/crm/account-guardian-ids.json` com `{ "dominio": { "account_id": "...", "criada": true, "contatos": { "<contato_id>": "<uuid>" } } }` e a lista de erros. É o que evita duplicar numa próxima rodada.

## O que nunca fazer

- Escrever no banco do Guardian por outro caminho (SQL, API REST, chave de serviço). Só a interface ou o MCP.
- Criar conta com `allow_duplicate: true` por conta própria.
- Mudar estágio de conta existente, dono ou valor.
- Levar pro Guardian conta com `veredito` `nutrir` ou `fora`, ou contato que não foi lançado.

## Pendências a confirmar

- Se o Guardian passar a guardar domínio na conta (o código marca como adiado), trocar a busca por nome pela busca por domínio neste adaptador e na `qa-lancamento`.
- Se aparecer import de contatos em lote, trocar o caminho B pelo import.
