# Adaptador: Apollo (MCP)

Como as skills do motor usam o MCP do Apollo: que ferramenta cada skill chama, pra quê, se consome crédito e que limite tem. O Apollo busca, enriquece e envia; a memória da máquina continua sendo o ledger (ver `adapters/google-sheets/README.md`).

Levantado em 29/09/2026 a partir dos schemas das ferramentas do MCP (lidos via ToolSearch, sem chamar nenhuma). Quando o Apollo mudar uma ferramenta, atualizar este arquivo e o `CHANGELOG.md`.

## Regras que valem pra toda skill

1. **Nenhum crédito de enrich sem estimativa mostrada e lote aprovado.** A skill mostra quantos créditos o lote pode gastar, o saldo atual e espera o "aprovado" do operador por escrito. Lote de 20 a 40 contas.
2. **Bloco `mcp_credits`.** Toda resposta de ferramenta que consome crédito pode trazer esse bloco (custo estimado, gasto real, saldo). Quando vier, a skill mostra ao operador sem ser perguntada: antes de gastar, o custo estimado (inclusive faixa esperada e máxima dos add-ons de waterfall); depois de gastar, os créditos usados e o saldo novo. A skill também grava esses números no arquivo de créditos da rodada.
3. **Bloco `apollo_plan_limit`.** Se uma resposta trouxer esse bloco, o plano ou o saldo do Apollo bateu no limite. A resposta ao operador é o `message` do bloco, **literal e inteiro**, com o link exatamente como veio: sem resumir, sem reescrever, sem sugerir alternativa ou outra ferramenta, sem acrescentar link, sem terminar com pergunta. A skill para aí. O registro no arquivo da rodada fica pra próxima interação.
4. **Confirmação exigida pela ferramenta.** Algumas ferramentas exigem uma frase exata de confirmação antes da chamada (ver tabela de custo). A skill mostra a estimativa em português e, junto, a frase exata que a ferramenta pede.
5. **IDs só da sessão.** Todo ID (organização, pessoa, conta, contato, sequência, caixa, campo, lista) vem de uma resposta de ferramenta na sessão atual. Nunca de memória, de rodada antiga ou de suposição. ID de rodada anterior gravado em CSV serve só como pista pra buscar de novo.
6. **Filtro explícito, sem agente do Apollo.** As buscas diretas (`apollo_mixed_companies_search`, `apollo_mixed_people_api_search`) só aceitam um conjunto de filtros estruturado, sem valor inventado na hora. No motor esse conjunto é o `segmentos/<segmento>/busca-apollo.md`, aprovado pelo operador. As ferramentas `apollo_agent_*` não são usadas: a busca precisa ser reproduzível e gravada.
7. **`_conversation_ref` e `_rationale`.** Gerar um token curto aleatório na primeira chamada da sessão e repetir em todas. `_rationale` descreve a intenção em termos gerais, sem domínio, nome ou email.

## Estimar crédito antes de gastar

1. Chamar `apollo_usage_stats_credit_usage_stats` (sem parâmetro, não consome crédito): créditos usados, restantes e data de renovação do time. Pra saldo de um usuário só, `apollo_users_api_profile` com `include_credit_usage: true`.
2. Calcular o teto do lote pela tabela de custo abaixo (ex.: 30 contatos no `apollo_people_bulk_match` = até 30 créditos).
3. Mostrar ao operador, nesta forma:

```
Lote 2 de 4 · 30 contatos em 12 contas
Ferramenta: apollo_people_bulk_match (3 chamadas de até 10)
Custo máximo: 30 créditos (pessoa não encontrada não cobra)
Saldo agora: <saldo> créditos · renova em <AAAA-MM-DD>
Sem telefone, sem email pessoal, sem waterfall.
Aprova o lote?
```

4. Depois da primeira chamada, ler o `mcp_credits` da resposta. Se o gasto real por item passar 20% do estimado, parar e mostrar a estimativa corrigida antes da próxima chamada.
5. Gravar estimativa, aprovação (quem e quando), gasto real e saldo final no arquivo de créditos da rodada.

## Custo e limites por ferramenta

| Ferramenta | Consome crédito | Limite conhecido | Observação |
|---|---|---|---|
| `apollo_mixed_companies_search` | Sim, segundo a documentação pública do Apollo pra Organization Search; o trecho de custo da descrição do MCP não estava visível na leitura. Conferir no `mcp_credits` da primeira página. | `per_page` até 100; paginar com `page` | Resposta em dois grupos: `organizations` (ID da organização em `id`) e `accounts` (já salvas no time; ID da organização em `organization_id`, o `id` é da conta). Não tem filtro de exclusão por palavra-chave nem por lista: exclusão é local. Tecnologia com `_` no lugar de espaço e ponto (`google_analytics`). Porte como `"51,200"`. |
| `apollo_organizations_lookup` | Não (gratuita) | `per_page` livre; paginar | Mesmos filtros de firmografia, tecnologia e palavra-chave, mas devolve só `id`, `name`, `domain`, `website_url`. Serve pra contar o TAM e achar o ID de organização. |
| `apollo_organizations_enrich` | 1 crédito se achar, 0 se não | 1 domínio por chamada | Frase exigida: "Enriching [domain] will consume 1 credit (no charge if not found). Do you want to proceed?" |
| `apollo_organizations_bulk_enrich` | 1 crédito por empresa encontrada | até 10 domínios por chamada | Frase exigida: "This will enrich [N] companies and consume up to [N] credits (1 credit per match, no charge for unmatched). Do you want to proceed?" Busca seguida de enrich: confirmar o escopo total com o saldo antes da primeira chamada. |
| `apollo_organizations_job_postings` | 1 crédito por chamada | 1 organização por chamada | Precisa do ID de `apollo_organizations_lookup`. Frase exigida: "This will consume 1 credit. Do you want to proceed?" Em lote, confirmar total e custo antes. |
| `apollo_mixed_people_api_search` | Não, segundo a documentação pública do Apollo pra People API Search; conferir no `mcp_credits`. Não devolve email nem telefone. | `per_page` até 100 | Filtrar por `q_organization_domains_list` ou `organization_ids` (ID de organização, nunca de conta). `person_locations` filtra onde a pessoa mora; `organization_locations` filtra a sede. |
| `apollo_people_bulk_match` | Sim, por pessoa encontrada. Telefone e waterfall custam à parte e variam por plano. | até 10 pessoas por chamada | Antes de oferecer revelar email: `apollo_users_api_profile` com `include_waterfall_capability: true`. O motor usa `reveal_phone_number: false`, `reveal_personal_emails: false`, `run_waterfall_email: false`, `run_waterfall_phone: false`, salvo aprovação separada. Waterfall e telefone são assíncronos e só podem ser lidos com `apollo_webhook_result_show`; sem essa ferramenta, não ligar. |
| `apollo_usage_stats_credit_usage_stats` | Não | sem parâmetro | Saldo e janela de renovação do time. |
| `apollo_users_api_profile` | Não | | `include_credit_usage`, `include_waterfall_capability`. |
| `apollo_accounts_bulk_create` | Não | até 100 contas por chamada | Sem deduplicação por padrão: passar `run_dedupe: true` no nível de cima (conta existente volta em `existing_accounts`, intacta). Colapsar domínio repetido antes de enviar. Não dá pra desfazer. |
| `apollo_contacts_bulk_create` | Não | até 100 contatos por chamada; limite diário por time definido pelo admin | Deduplica sozinho e **sobrescreve** o contato existente com os valores enviados, sem volta. Contato com `person_id` ou `organization_id` nulo foi salvo sem casar com a base do Apollo: resumir a contagem, não enriquecer sozinho. |
| `apollo_labels_index` | Não | | Lista as listas (labels) com `id`, `modality` e `app_url`. |
| `apollo_labels_create` | Não | nome único por modalidade | `modality`: `contacts` ou `accounts`. |
| `apollo_labels_add_entity_ids_to_label_names` | Não | | Cria a lista se o nome não existir. Registro repetido é ignorado. |
| `apollo_fields_index` | Não | | Passar `modality` (`contact`, `account`) e `source: custom`. O `id` do campo é a chave de `typed_custom_fields`. |
| `apollo_fields_create` | Não | rótulo único por modalidade | Mudança de modelo de dados do time: mostrar modalidade, rótulo e tipo e pedir aprovação explícita. Campo de abertura: tipo `textarea`, `computed_type` omitido (manual). |
| `apollo_sequences_create` | Não, se `has_personalized_opener` ficar `false` (abertura por IA do Apollo consome crédito) | até 25 passos; até 3 variantes por passo | Nasce `active: false`. Antes: `apollo_emailer_campaigns_search` com `q_name` pra não duplicar. `wait_time` do passo 1 = 0. Passo seguinte na mesma thread: `type: reply_to_thread`. |
| `apollo_sequences_update` | Não | | Diff declarativo: o `emailer_steps` enviado é o estado final; passo existente que não vier no payload é **apagado**. `label_names` substitui a lista inteira. `active` é obrigatório: repetir o valor atual. Ler antes com `apollo_emailer_campaigns_show`. |
| `apollo_email_accounts_index` | Não | | IDs das caixas de envio; `default: true` é a caixa principal do usuário. |
| `apollo_emailer_campaigns_search` | Não | | Acha a sequência por nome; mais de um resultado = perguntar ao operador. |
| `apollo_emailer_campaigns_show` | Não | resposta grande | Passos, toques e texto de cada email da sequência, com os IDs que o update precisa. |
| `apollo_emailer_campaigns_add_contact_ids` | Não, mas **envia email de verdade** e não tem volta depois do disparo | | Só com H3 aprovado no `05-qa-lancamento.md`. Antes: `apollo_emailer_campaigns_search` e `apollo_email_accounts_index`, e um resumo (caixa, sequência, número de contatos, status) confirmado pelo operador. Manter `sequence_unverified_email`, `sequence_no_email`, `sequence_active_in_other_campaigns` e `sequence_finished_in_other_campaigns` em `false`. |

## Ferramentas por skill

### `montar-tam`

| Ferramenta | Pra quê | Crédito |
|---|---|---|
| `apollo_organizations_lookup` | Contar o TAM de cada hipótese sem custo; achar o ID de organização das contas âncora | não |
| `apollo_mixed_companies_search` | Rodar a busca de `busca-apollo.md` paginando (100 por página) e trazer firmografia, palavras-chave e tecnologias; buscar as âncoras por `q_organization_domains_list` | ver tabela |
| `apollo_organizations_enrich` / `apollo_organizations_bulk_enrich` | Só quando a busca por domínio não trouxer palavras-chave ou tecnologias de uma âncora | sim, com aprovação |
| `apollo_usage_stats_credit_usage_stats` | Saldo antes de paginar | não |

### `validar-lista`

Não chama o Apollo diretamente: usa os dados da `01-lista-crua.csv` como semente e pesquisa na web. Chama a `detectar-tecnografia`, que pode usar o Apollo (abaixo).

### `detectar-tecnografia`

| Ferramenta | Pra quê | Crédito |
|---|---|---|
| `apollo_organizations_lookup` | ID de organização pra consultar vagas | não |
| `apollo_organizations_job_postings` | Vagas abertas que citam as ferramentas da `tecnografia_alvo` | 1 por conta, com aprovação do lote |

O campo `technologies` que a `montar-tam` gravou na lista crua entra como evidência `apollo`, sempre com confiança baixa.

### `mapear-comite`

| Ferramenta | Pra quê | Crédito |
|---|---|---|
| `apollo_mixed_people_api_search` | Pessoas da conta pelos cargos da persona do porte | ver tabela |
| `apollo_users_api_profile` | Conferir se o time tem waterfall (exigido antes de revelar email) | não |
| `apollo_usage_stats_credit_usage_stats` | Saldo pra estimativa | não |
| `apollo_people_bulk_match` | Email, status do email, LinkedIn e cargo atual dos escolhidos, em chamadas de até 10 | sim, com aprovação do lote |

### `apollo-sequence-builder`

| Ferramenta | Pra quê | Crédito |
|---|---|---|
| `apollo_fields_index` | Achar os campos custom (`primeira_frase`, `segmento`, `trilha`) de conta e de contato | não |
| `apollo_fields_create` | Criar o campo custom que faltar, com aprovação explícita | não |
| `apollo_labels_index` | Ver se a lista da rodada já existe | não |
| `apollo_labels_create` | Criar a lista da rodada (contas e contatos) | não |
| `apollo_accounts_bulk_create` | Criar as contas da rodada com `run_dedupe: true` e os campos custom | não |
| `apollo_contacts_bulk_create` | Criar os contatos de canal `email` ou `ambos`, com `label_names` da rodada e campos custom preenchidos (fallback já aplicado) | não |
| `apollo_labels_add_entity_ids_to_label_names` | Pôr na lista da rodada as contas e contatos que já existiam | não |
| `apollo_emailer_campaigns_search` | Conferir que não existe sequência com o mesmo nome; depois, achar o ID da criada | não |
| `apollo_sequences_create` | Criar a sequência pausada, com os 4 passos de `04-sequencia-email.md`, intervalos e teto diário | não |
| `apollo_emailer_campaigns_show` | Ler passos e IDs da sequência criada | não |
| `apollo_sequences_update` | Corrigir passo depois do H2 ou do QA, mandando o estado completo | não |
| `apollo_email_accounts_index` | IDs das caixas do `cliente.yaml` | não |
| `apollo_emailer_campaigns_add_contact_ids` | Inscrever os contatos, só com H3 aprovado | não, mas envia email |

### `qa-lancamento`

| Ferramenta | Pra quê | Crédito |
|---|---|---|
| `apollo_emailer_campaigns_search` / `apollo_emailer_campaigns_show` | Conferir que a sequência está pausada e que assunto, corpo e intervalos batem com `04-sequencia-email.md` | não |
| `apollo_email_accounts_index` | Conferir que as caixas da sequência são as do `cliente.yaml`, aquecidas | não |
| `apollo_fields_index` | Conferir que os campos custom usados no texto existem | não |
| `apollo_contacts_search` | Conferir que cada contato da rodada existe no Apollo com os campos custom preenchidos e não está em outra sequência | não |

## Armadilhas conhecidas

- **Porte no formato certo.** O `cliente.yaml` guarda porte como `51-200` (como a interface mostra); a API espera `"51,200"`.
- **Conta × organização.** Na busca de empresas, linha do grupo `accounts` tem ID de conta em `id`; o filtro de pessoas precisa do `organization_id` dela.
- **Exclusão é local.** A API não exclui por palavra-chave nem por lista. Os negativos de palavra-chave e a supressão rodam depois da busca, sobre o CSV (`scripts/suppress.py`).
- **Dado do Apollo erra.** Descrição colada na empresa errada, setor errado, homônimo, `technologies` desatualizado. Tudo que vem do Apollo é semente, não evidência forte.
- **`contacts_bulk_create` sobrescreve.** Contato que já existe no Apollo tem os campos trocados pelos enviados. Antes de subir, buscar com `apollo_contacts_search` e não mandar campo vazio por cima de campo preenchido.
- **`sequences_update` apaga o que não vier.** Sempre mandar o estado completo, com os IDs lidos no `apollo_emailer_campaigns_show` da mesma sessão.
