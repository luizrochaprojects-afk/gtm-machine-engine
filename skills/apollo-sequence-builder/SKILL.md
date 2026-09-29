---
name: apollo-sequence-builder
description: Monta a campanha de email da rodada no Apollo pelo MCP. Gera 04-apollo-import.csv (UTF-8 com BOM), confere e cria os campos custom, cria ou atualiza contas e contatos com primeira frase, segmento e trilha (fallback aplicado em variável vazia), cria o rótulo da rodada, casa as caixas do Apollo com as caixas aquecidas do cliente.yaml, calcula o volume diário e bloqueia acima do teto, cria a sequência de 4 passos inativa e grava os IDs em 04-apollo-ids.json. Só inscreve contatos depois de "H3 aprovado" no 05-qa-lancamento.md. Use na etapa E6, quando o operador disser "monta o Apollo", "cria a sequência", "sobe os contatos no Apollo", "sequência da rodada", "roda a apollo-sequence-builder", "inscreve os contatos" (esta última só depois do H3).
---

# apollo-sequence-builder

Leva a sequência aprovada no H2 e os contatos da rodada pro Apollo: campos, contas, contatos, rótulo e sequência, tudo pelo MCP, com a sequência inativa e vazia. Numa segunda chamada, depois do H3, inscreve os contatos em lotes que respeitam o teto por caixa.

A skill não sabe quem é o cliente. Caixas, limite diário, janela de envio, assinatura e donos de gate vêm do `cliente.yaml`. Copy vem do `04-sequencia-email.md` aprovado; a skill não reescreve uma palavra.

## Antes de começar: o que ler

| # | Arquivo | O que tirar dele |
|---|---|---|
| 1 | `adapters/apollo/README.md` | Ferramentas por skill e quais gastam crédito |
| 2 | `schemas/apollo-import.schema.md` | Colunas do CSV de contas e de contatos, BOM, domínio normalizado |
| 3 | `schemas/sequencia-email.schema.md` | Formato da sequência, tabela de variáveis, fallback, spintax, merge tags do Apollo |
| 4 | `cliente.yaml` | `stack.sequenciador_email`, `remetentes.caixas_email[]` (email, `limite_diario`, `aquecimento_inicio`, `aquecida_em`, `assinatura`), `remetentes.janela_envio`, `gates.H3`, `gates.pessoas` |
| 5 | `rodadas/<rodada>/04-sequencia-email.md` | Os 4 toques e a tabela de variáveis |
| 6 | `rodadas/<rodada>/03-contatos.csv` e os vereditos (`02-validacao.xlsx` ou JSON) | Contatos, `company_name`, `primeira_frase`, `segmento`, `trilha`, `veredito`, `tier` |
| 7 | `adapters/google-sheets/README.md` | Como exportar o snapshot do ledger pro anti-join |

## Pré-condições

Pare e diga ao operador o que falta se:

- `stack.sequenciador_email` não é `apollo`;
- não existe `aprendizado/diffs/<rodada>-H2-email.md` com resultado aprovado;
- `04-sequencia-email.md` não segue o schema (4 toques `## D1`, `## D4`, `## D8`, `## D13`, tabela `## Variáveis`);
- nenhuma caixa do `cliente.yaml` está aquecida (ver passo 6);
- o MCP do Apollo não responde ou devolve erro de autenticação.

Toda resposta do Apollo com bloco `mcp_credits`: mostre ao operador a estimativa antes de gastar e, depois, os créditos usados e o saldo. Resposta com bloco `apollo_plan_limit`: repasse a mensagem dele exatamente como veio e pare.

## Parte 1: montar (antes do H3)

### 1. Conferir a sequência renderizando

```bash
python scripts/render_email.py --sequencia rodadas/<rodada>/04-sequencia-email.md \
    --contatos rodadas/<rodada>/03-contatos.csv --saida rodadas/<rodada>/_render-apollo.md
```

Saída 1 (sobrou `{{`, variável não declarada ou travessão): pare e devolva pra `copy-email`. Não corrija a copy aqui.

### 2. Gerar os CSVs de import

1. Contatos que entram: canal `email` ou `ambos`, `email_status = verified`, conta com veredito `P0` ou `lista`.
2. Normalize o domínio: `python scripts/normalize_domain.py --csv <arquivo> --coluna domain`.
3. **Fallback no dado, não na sequência.** Pra cada variável da tabela `## Variáveis` que não é nativa do Apollo (`first_name`, `last_name`, `company`, `title`), preencha a coluna com o fallback da tabela quando o valor estiver vazio. O Apollo nunca pode enviar merge vazio.
4. **Anti-join.** Exporte agora as abas `supressao`, `contas`, `contatos` e `toques` pra `rodadas/<rodada>/_snapshot/<AAAA-MM-DD-HHMM>/<aba>.csv` e rode:

   ```bash
   python scripts/suppress.py --lista <contatos-bruto>.csv --ledger-dir rodadas/<rodada>/_snapshot/<AAAA-MM-DD-HHMM> \
       --saida rodadas/<rodada>/04-apollo-import.csv --removidos rodadas/<rodada>/04-apollo-removidos.csv \
       --col-dominio domain --col-email email --col-linkedin linkedin_url
   ```

   Quem recebeu toque e não respondeu sai aqui (`toque_sem_resposta`). Nunca devolva essa pessoa pra lista.
5. Grave em **UTF-8 com BOM** (`encoding="utf-8-sig"`):
   - `rodadas/<rodada>/04-apollo-import.csv`: contatos, colunas do schema (`first_name`, `last_name`, `email`, `title`, `company_name`, `domain`, `linkedin_url`, `primeira_frase`, `segmento`, `trilha`, `rodada` e as demais variáveis custom da sequência).
   - `rodadas/<rodada>/04-apollo-import-contas.csv`: uma linha por conta dos contatos que ficaram (`domain`, `company_name`, `segmento`, `trilha`, `veredito`, `tier`, `rodada`).

Esses arquivos são o registro do que subiu e o caminho alternativo pela interface (Lists → Import) se o MCP falhar.

### 3. Campos custom

1. `apollo_fields_index` com `modality: "contact"` e depois `modality: "account"` (`source: "custom"`).
2. Campos necessários:
   - contato: cada variável custom da sequência (ex.: `primeira_frase`), mais `segmento`, `trilha`, `rodada`;
   - conta: `segmento`, `trilha`, `veredito`, `tier`, `rodada`.
3. O que faltar: mostre ao operador a lista exata (modalidade, rótulo, tipo `string`, ou `textarea` pra texto acima de 255 caracteres) e **peça aprovação explícita**. Só com o sim, `apollo_fields_create` com `meta.computed_type: "manual"`. Campo custom aparece em todo registro do time; não crie campo que não será usado.
4. Rótulo do campo = nome da variável na sequência. Confira no retorno do `apollo_fields_index` o nome que o Apollo usa como merge tag; se for diferente do nome da variável, use o do Apollo no corpo do email (passo 7) e anote no `04-apollo-ids.json`.

### 4. Contas

1. Tire domínios repetidos do lote.
2. `apollo_accounts_bulk_create` com `run_dedupe: true` (no nível de cima, ao lado de `accounts`), no máximo 100 por chamada. Cada conta: `name`, `domain`, `typed_custom_fields` com os IDs dos campos de conta.
3. Guarde o `id` de cada conta criada e de cada uma devolvida em `existing_accounts`.
4. Conta existente volta sem mudança: mostre quantas são e, com o sim do operador, atualize os campos da rodada com `apollo_accounts_update`, uma por vez.

### 5. Contatos e rótulo da rodada

1. Rótulo = nome da rodada. Se ainda não existe, `apollo_labels_create` com `modality: "contacts"` e de novo com `modality: "accounts"` (o nome é único por modalidade).
2. Antes de subir, pra cada email: `apollo_contacts_search` com `q_keywords` = email. Contato que já existe no Apollo e está ou esteve em outra sequência: tire do lote, anote no relatório. O `apollo_contacts_bulk_create` **sobrescreve** os campos de contato existente e não dá pra desfazer.
3. `apollo_contacts_bulk_create`, no máximo 100 por chamada. Cada contato: `first_name`, `last_name`, `email`, `title`, `organization_name`, `website_url` (o domínio), `account_id` (do passo 4), `label_names: ["<rodada>"]`, `typed_custom_fields` com primeira frase, segmento, trilha, rodada e as demais variáveis, já com fallback.
4. O bulk create não aceita URL de LinkedIn: ela fica no CSV e no ledger.
5. Contato com `person_id` ou `organization_id` nulo no retorno: diga quantos foram salvos sem casar com a base do Apollo. Não é falha. Não enriqueça por conta própria; se o operador quiser, mostre a estimativa de crédito antes.
6. Contas no rótulo: `apollo_labels_add_entity_ids_to_label_names` com `modality: "accounts"`, os IDs do passo 4 e `label_names: ["<rodada>"]`.

### 6. Caixas de envio

1. `apollo_email_accounts_index`.
2. Case pelo email com `remetentes.caixas_email` do `cliente.yaml`. Entra só caixa **aquecida**: `aquecida_em` preenchido e menor ou igual a hoje, ou `aquecimento_inicio` menor ou igual a hoje menos 14 dias.
3. Caixa do Apollo que não está no `cliente.yaml`: não usar, nem se for a padrão do usuário. Caixa do `cliente.yaml` que não aparece no Apollo: avisar (não está conectada).
4. Limite por caixa = `limite_diario` do `cliente.yaml`, nunca acima de 30. Se o `cliente.yaml` disser mais de 30, use 30 e avise.

### 7. Volume diário

Com `N` contatos, `P` passos de email (4), `C` caixas aquecidas e `L` limite por caixa:

- capacidade por dia = `C × L`;
- dias pra escoar a rodada = `ceil(N × P ÷ (C × L))`;
- lote máximo de inscrição por dia = `floor(C × L ÷ P)` (com inscrição diária constante, cada dia soma o D1 do lote do dia, o D4, o D8 e o D13 de lotes anteriores).

Bloqueie e não crie a sequência se: `C = 0`; alguma caixa com `L > 30`; o operador pedir pra inscrever num dia mais que o lote máximo. Mostre a conta e o calendário de lotes (dia útil × contatos). Grave no `04-apollo-ids.json`.

### 8. Sequência

1. `apollo_emailer_campaigns_search` com `q_name` = nome da rodada. Se já existir sequência com o nome: mostre e pergunte (atualizar com `apollo_sequences_update` ou parar). Nunca crie duplicada.
2. Janela de envio: `apollo_emailer_schedules_index` e procure um agendamento que bata com `remetentes.janela_envio` (dias, início, fim, fuso). Achou: use o `id`. Não achou: o MCP não cria agendamento. Peça ao operador que crie na interface (Settings → Schedules, com dias, horário e fuso do `cliente.yaml`) e liste de novo.
3. Traduza cada toque:

   | No `04-sequencia-email.md` | No `emailer_steps` |
   |---|---|
   | `## D1` | `type: "auto_email"`, `wait_time: 0`, `wait_mode: "day"` |
   | `## D4`, `## D8`, `## D13` | `wait_time` = dia do toque menos dia do anterior (3, 4, 5) |
   | `Assunto: <texto>` | touch `type: "new_thread"`, `emailer_template.subject` = texto |
   | `Assunto: (mesma thread)` | touch `type: "reply_to_thread"`, sem assunto |
   | Corpo | `body_html`: cada parágrafo num `<p>`, texto sem outra marcação, URL crua |
   | `{{first_name}}`, `{{company}}`, `{{title}}`, `{{last_name}}` | merge tag nativa do Apollo, igual |
   | Outra variável | merge tag com o nome do campo custom (passo 3) |
   | Spintax `{a\|b}` | só a primeira opção, igual ao render do QA. Variante A/B só se o operador pedir |

4. `apollo_sequences_create` com: `name` = rodada; `active: false`; os 4 passos; `emailer_schedule_id`; `max_emails_per_day` (o do nível de cima) = `C × L`; `mark_finished_if_reply: true`; `mark_finished_if_interested: true`; `mark_paused_if_ooo: true`; `label_names: ["<rodada>"]`. Um touch por passo, `status: "approved"`, `template_type: "default"`. `include_signature: false` quando o corpo já traz a assinatura do remetente; `true` só se a assinatura estiver configurada na caixa e não no corpo.
   **D1 por nível.** Se o `04-sequencia-email.md` tem `## D1 · decisor` e `## D1 · champion`, crie **duas sequências**, `<rodada>-decisor` e `<rodada>-champion`, iguais em tudo menos no D1, que vem da variante do nível. Contato com `papel = decisor` vai pra primeira; `champion` e `influenciador`, pra segunda. As duas dividem as mesmas caixas, então a soma dos `max_emails_per_day` das duas não passa de `C × L`: reparta em proporção ao número de contatos de cada nível (arredondando pra baixo). Contato sem papel reconhecido não entra em nenhuma: vai pra `fora_do_lote` com o motivo.
5. **Não use** `has_personalized_opener`, `generation_options` nem `prompt_template`: reescrevem a copy aprovada e gastam crédito.
6. As caixas **não** são campo da sequência no MCP: entram na inscrição (Parte 2). Se o time tiver a trava de domínio ativa, `allowed_send_from_domains` com os domínios das caixas aquecidas.
7. `apollo_emailer_campaigns_show` com o `id` criado e compare com o `04-sequencia-email.md`: número de passos, intervalos, assunto, thread, corpo sem corte, merge tags, `active: false`, nenhum contato. Qualquer diferença: corrija com `apollo_sequences_update` (mandando o estado inteiro dos passos com os IDs e `active: false`).

**Se o `apollo_sequences_create` recusar um campo ou não tiver onde pôr** (janela, caixa, thread, limite): crie a sequência com o que o MCP aceita e escreva `rodadas/<rodada>/04-apollo-interface.md` com o passo a passo na interface pro que faltou. Sequences → abrir a sequência → Settings (agendamento, limite diário, marcar como terminado ao responder) e, em cada passo, o editor do email (assunto, "reply in same thread"). Se nem a criação passar: sequência inteira pela interface (Sequences → New sequence → From scratch, 4 passos "Automatic email" com os intervalos e textos do arquivo), deixada inativa, e o `id` lido com `apollo_emailer_campaigns_search` pro `04-apollo-ids.json`.

### 9. Registrar os IDs

Grave `rodadas/<rodada>/04-apollo-ids.json`:

```json
{
  "rodada": "<rodada>",
  "criado_em": "AAAA-MM-DD HH:MM",
  "sequencia": {"id": "...", "nome": "...", "ativa": false, "passos": [{"id": "...", "dia": "D1", "wait_time": 0}]},
  "_comentario": "com D1 por nível, troque 'sequencia' por 'sequencias': {\"decisor\": {...}, \"champion\": {...}}, cada uma com id, nome, ativa, max_emails_per_day e passos; e em 'contatos' acrescente \"nivel\"",
  "agendamento_id": "...",
  "rotulos": {"contacts": "<id>", "accounts": "<id>"},
  "campos_custom": {"contact": {"primeira_frase": {"id": "...", "merge_tag": "..."}}, "account": {}},
  "caixas": [{"email": "...", "id": "...", "limite": 25}],
  "volume": {"contatos": 0, "passos": 4, "caixas": 0, "limite": 0, "capacidade_dia": 0, "lote_max_dia": 0, "dias_para_escoar": 0},
  "contas": {"<dominio>": {"id": "...", "criada": true}},
  "contatos": {"<email>": {"id": "...", "dominio": "..."}},
  "fora_do_lote": [{"email": "...", "motivo": "..."}],
  "inscricoes": []
}
```

Fim da Parte 1: diga ao operador o que foi criado, o que ficou fora e por quê, os créditos gastos (se houver) e que a sequência está inativa e vazia esperando o QA e o H3.

## Parte 2: inscrever (só depois do H3)

1. Leia `rodadas/<rodada>/05-qa-lancamento.md`. Só siga se:
   - o bloco "Decisão H3" tem uma linha no formato exato `H3 aprovado AAAA-MM-DD HH:MM por <nome>`, com data e hora reais;
   - `<nome>` é uma das pessoas de `gates.H3` no `cliente.yaml`;
   - a tabela de itens não tem nenhum vermelho;
   - a data da aprovação é igual ou posterior à data do QA.
   Qualquer falha: pare e diga qual. A skill nunca escreve essa linha.
2. Monte o lote do dia a partir do calendário do passo 7 e do `04-apollo-ids.json` (nunca IDs de memória). Confira de novo contra o snapshot fresco do ledger (`suppress.py`): quem recebeu toque sem resposta desde a Parte 1 sai.
3. `apollo_emailer_campaigns_search` pra confirmar o `id` da sequência nesta sessão.
4. Mostre o resumo e **espere confirmação explícita**: caixas de envio (emails), nome da sequência, número de contatos do lote, status da inscrição, dia do lote no calendário.
5. `apollo_emailer_campaigns_add_contact_ids` com `id` e `emailer_campaign_id` = id da sequência, `contact_ids` do lote, `send_email_from_email_account_id` = lista das caixas aquecidas (rodízio). Deixe **falsos** `sequence_active_in_other_campaigns`, `sequence_finished_in_other_campaigns`, `sequence_unverified_email`, `sequence_no_email`, `contact_verification_skipped` e `contacts_without_ownership_permission`: são eles que impedem inscrever quem já está ou esteve em outra sequência. Deixe **verdadeiro** `sequence_same_company_in_same_campaign`: falso, o Apollo recusa o segundo e o terceiro contato da mesma conta na mesma sequência, e a rodada perde o comitê (até 3 contatos por conta) sem avisar. Quem protege a conta de ser abordada duas vezes em rodadas diferentes é o ledger e o `suppress.py`, não essa trava. Com D1 por nível, inscreva cada contato na sequência do seu nível, um `apollo_emailer_campaigns_add_contact_ids` por sequência.
6. Contatos recusados pelo Apollo: liste com o motivo. Não force.
7. Sequência inativa não envia. Ativar é decisão do operador: mostre de novo o resumo e, com o sim dele, `apollo_emailer_campaigns_approve`. Anote data e hora no bloco "Lançamento" do `05-qa-lancamento.md`.
8. Acrescente o lote em `inscricoes` do `04-apollo-ids.json` (data, contatos, caixas, recusados) e chame a `registrar-ledger` pros toques.

Lotes dos dias seguintes: repetir a Parte 2 a partir do passo 2, um lote por dia útil.

## Gates

- **H2** antes da Parte 1: sem sequência aprovada, nada sobe.
- **H3** antes da Parte 2: sem a linha de aprovação no QA, nenhum contato é inscrito e nenhuma sequência é ativada.

## Armadilhas

- **Sequência criada ativa.** Sempre `active: false`. Conferir no `emailer_campaigns_show`.
- **Caixa padrão do usuário.** A ferramenta de inscrição sugere a caixa padrão; aqui vale só a lista aquecida do `cliente.yaml`.
- **Bulk create de contato sobrescreve.** Contato que já existe no Apollo perde os valores antigos. Buscar antes.
- **Contas sem deduplicação.** Sem `run_dedupe: true`, cada linha vira conta nova.
- **Merge vazio.** Fallback aplicado no campo antes de subir, não confiado ao Apollo.
- **Nome do campo custom diferente da variável.** O merge tag é o nome do campo no Apollo; conferir no `fields_index`.
- **ID de memória.** Todo ID vem de uma resposta desta sessão ou do `04-apollo-ids.json` desta rodada.
- **Inscrever tudo no dia 1.** O D1 de todos cai junto e estoura o teto. Lotes diários.
- **CSV sem BOM** quebra acento no import pela interface.
