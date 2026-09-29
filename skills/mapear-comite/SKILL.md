---
name: mapear-comite
description: "Mapeia o comitê de compra das contas aprovadas no H1: busca no Apollo as pessoas pelos cargos da persona do porte de cada conta, escolhe até 3 por conta (decisor, champion, influenciador), mostra o custo de crédito do lote e só enriquece com aprovação, classifica o email, define o canal (email, LinkedIn ou ambos), aplica a supressão e grava os contatos da rodada. Use quando o operador pedir contatos, comitê, decisores, 'acha as pessoas dessas contas', 'quem abordar em cada conta', 'enriquece os contatos', 'puxa os emails' ou 'monta a lista de contatos da rodada'."
---

# Mapear comitê

Etapa E3. Pra cada conta aprovada, até 3 pessoas com papel definido, email verificado quando houver, LinkedIn e o canal por onde cada uma vai ser abordada. É a única etapa do motor que gasta crédito de enrich em volume: **nenhum crédito sai sem estimativa mostrada e lote aprovado**.

A skill não sabe quem é o cliente. Personas, portes e cargos vêm do `cliente.yaml` do workspace ativo.

## Ler antes

1. `cliente.yaml` → `personas` (`porte`, `cargos`, `papel`, `maximo_por_conta`), `ofertas`, `ledger_id`.
2. `estrategia/gabarito-icp.md`, seção "Persona por porte": exceções (ex.: conta sem título de CRM detectável não é desqualificada; o alvo vira o decisor).
3. `rodadas/<rodada>/02-validacao.json` e `aprendizado/diffs/<rodada>-H1-lista.md`. **Sem o diff H1 gravado, parar**: a lista não foi aprovada.
4. `rodadas/<rodada>/01-lista-crua.csv` (porte e ID de organização de cada conta).
5. `adapters/apollo/README.md` (custo e limite de cada ferramenta) e `schemas/contato.schema.json`.

## Entradas

Contas com veredito `P0` ou `lista` no `02-validacao.json` depois do H1. Lote de 20 a 40 contas por aprovação de crédito.

## Passos

### 1. Porte e persona de cada conta

1. Porte da conta: `employees` da lista crua. Sem número, usar a faixa do Apollo da conta; sem nada, perguntar ao operador ou tratar como a menor faixa das personas e anotar.
2. Casar com a faixa `porte` das `personas` (`51-200` = de 51 a 200 funcionários). As personas daquele porte, na ordem em que aparecem no `cliente.yaml`, são a ordem de prioridade dos papéis.
3. Montar a tabela de busca e mostrar ao operador: conta, porte, papéis e cargos buscados.

### 2. Buscar pessoas

Uma chamada de `apollo_mixed_people_api_search` por conta, com todos os cargos das personas daquele porte:

```json
{
  "q_organization_domains_list": ["acme.com.br"],
  "person_titles": ["ceo", "founder", "sócio", "head de crm", "gerente de crm"],
  "include_similar_titles": true,
  "per_page": 25,
  "page": 1
}
```

- Com o `apollo_org_id` da lista crua, preferir `organization_ids` (é mais exato que o domínio). O ID tem que vir de uma resposta da sessão: se a lista crua é de outro dia, buscar a conta de novo com `apollo_organizations_lookup` (gratuita) antes.
- Se o `cliente.yaml` ou o gabarito disser onde as pessoas precisam morar, usar `person_locations`; `organization_locations` filtra a sede, não a pessoa.
- Conta sem resultado: repetir uma vez com `include_similar_titles: true` e `person_seniorities` do papel (ex.: `c_suite`, `director`, `head`, `manager`) no lugar dos cargos.
- Gravar a resposta crua em `rodadas/<rodada>/tmp/comite/<domain>.json`.

### 3. Escolher até 3 por conta

Classificar cada pessoa encontrada num papel: o papel da persona cujo cargo casa com o título dela (sem acento, caixa baixa, cargo contido no título). Pessoa que casa com mais de um papel fica no de maior prioridade.

**Regra de prioridade:**

1. Um contato por papel, na ordem das personas do porte (ex.: decisor, depois champion, depois influenciador), até 3 no total e respeitando `maximo_por_conta` de cada persona.
2. Papel sem candidato fica vazio. Não completar com uma segunda pessoa de outro papel, salvo se o `maximo_por_conta` daquele papel permitir.
3. Exceção do gabarito (ex.: conta sem ninguém de CRM): aplicar como o gabarito diz e anotar no `fonte` (`apollo_search; excecao_gabarito`).

**Desempate dentro do mesmo papel**, nesta ordem:

1. Título que casa exatamente com um cargo da persona ganha de título parecido.
2. Cargo mais acima na lista de `cargos` da persona (a lista está em ordem de preferência).
3. Senioridade maior (`c_suite` > `vp` > `director` > `head` > `manager` > `senior`).
4. Tem `linkedin_url`.
5. O Apollo indica email disponível.
6. Nome em ordem alfabética (pra a escolha ser reproduzível).

Os que não foram escolhidos ficam guardados como reserva em `rodadas/<rodada>/tmp/comite/reservas.csv`, na ordem do desempate.

### 4. Estimar e aprovar o crédito

1. `apollo_usage_stats_credit_usage_stats` pra saldo e renovação.
2. `apollo_users_api_profile` com `include_waterfall_capability: true` (a ferramenta de enrich exige essa checagem antes de revelar email). O motor não liga waterfall nem telefone sem pedido do operador; se ele pedir, o custo é variável por plano e não se promete número fixo.
3. Mostrar a estimativa no formato de `adapters/apollo/README.md`:

```
Lote 1 · 28 contas · 71 contatos escolhidos
Ferramenta: apollo_people_bulk_match (8 chamadas de até 10)
Custo máximo: 71 créditos (pessoa não encontrada não cobra)
Saldo agora: <saldo> créditos · renova em <AAAA-MM-DD>
Sem telefone, sem email pessoal, sem waterfall.
Aprova o lote?
```

4. Seguir só com "aprovado" escrito. Gravar a estimativa e a aprovação (quem, quando) em `rodadas/<rodada>/03-creditos.md`.

### 5. Enriquecer

`apollo_people_bulk_match` em chamadas de **até 10 pessoas** (limite do `details` no schema da ferramenta), passando o `id` de cada pessoa que veio da busca:

```json
{
  "details": [{"id": "<id da busca>"}, {"id": "<id da busca>"}],
  "reveal_personal_emails": false,
  "reveal_phone_number": false,
  "run_waterfall_email": false,
  "run_waterfall_phone": false
}
```

- Depois da primeira chamada, mostrar o `mcp_credits` (usados e saldo). Se o gasto real por pessoa passar 20% do estimado, parar e mostrar a estimativa corrigida.
- Se a resposta trouxer `apollo_plan_limit`, a resposta ao operador é o `message` do bloco, literal e inteiro, e a skill para.
- Gravar cada resposta em `rodadas/<rodada>/tmp/comite/match-<n>.json`.
- **Pessoa que mudou de empresa:** se o domínio da organização no match não é o domínio da conta, descartar e subir o próximo da reserva daquele papel. A reserva entra num lote novo, com estimativa própria.

### 6. Classificar email e canal

**`email_status`**, a partir do que o Apollo devolve:

| Apollo | `email_status` |
|---|---|
| `verified` | `verified` |
| `likely to engage`, `guessed`, `extrapolated` | `likely` |
| `unverified` | `unverified` |
| `bounced`, `invalid` | `invalid` |
| sem email, `unavailable`, nulo | `sem_email` (e `email` vazio) |

**`linkedin_url`**: normalizar pra `https://www.linkedin.com/in/<slug>` (https, sem parâmetros, sem barra final). URL que não é de perfil `/in/` fica vazia.

**`canal`**:

| Email `verified` | LinkedIn | `canal` |
|---|---|---|
| sim | sim | `ambos` |
| sim | não | `email` |
| não | sim | `linkedin` |
| não | não | contato sai; subir a reserva do papel |

Email que não é `verified` fica gravado em `email` pra referência, mas o contato não recebe email (canal `linkedin`).

**`cargo`**: o título que veio do match, conferido nesta data; `cargo_checado_em` = data de hoje. `primeiro_nome`: o primeiro nome, com acento, como a pessoa é chamada.

### 7. Campos da conta

Pra cada contato, copiar do veredito da conta no `02-validacao.json`, casando por `domain`:

- `company_name`, `trilha` e `primeira_frase` do veredito;
- `segmento` = o segmento da rodada (do nome da rodada e do `cliente.yaml`).

`primeira_frase` fica **vazia** se o veredito não tiver frase ou se o fato que a sustenta (`evidencias[primeira_frase_evidencia_idx].fato`) estiver em `adversarial.fatos_refutados`. O `render_email.py` e a `apollo-sequence-builder` leem só o `03-contatos.csv`; nada da conta que eles precisem pode ficar fora dele.

### 8. Supressão dos contatos

1. Exportar de novo o ledger (abas `supressao`, `contas`, `contatos`, `toques`, com `get_values` do conector do Google Sheets) pra `rodadas/<rodada>/_snapshot/<AAAA-MM-DD-HHMM>/<aba>.csv`, uma pasta nova por execução.
2. Rodar sobre o CSV de contatos (antes de gravar o final):

```bash
python scripts/suppress.py --lista rodadas/<rodada>/tmp/comite/contatos.csv \
  --ledger-dir rodadas/<rodada>/_snapshot/<AAAA-MM-DD-HHMM> \
  --saida rodadas/<rodada>/tmp/comite/contatos-filtrados.csv \
  --removidos rodadas/<rodada>/tmp/comite/contatos-removidos.csv \
  --col-dominio domain --col-email email --col-linkedin linkedin_url
```

3. Contato removido abre a vaga pra reserva do mesmo papel (novo lote, nova estimativa). Conta inteira suprimida (`supressao:<motivo>` por domínio ou `nao_abordar_conta`) sai da rodada e vai anotada no `03-sem-contato.csv` com o motivo.

### 9. Gravar e validar

**`rodadas/<rodada>/03-contatos.csv`**, UTF-8 com BOM, uma linha por contato no formato de `schemas/contato.schema.json`. Colunas nesta ordem: as obrigatórias (`domain`, `nome`, `cargo`, `papel`, `email`, `email_status`, `linkedin_url`, `canal`) e depois as opcionais na ordem do schema (`primeiro_nome`, `cargo_checado_em`, `ordem_na_conta`, `company_name`, `primeira_frase`, `segmento`, `trilha`, `apollo_person_id`, `fonte`). `ordem_na_conta` = 1 a 3 pela prioridade do passo 3. `fonte` = `apollo_search; apollo_match`.

Validar cada linha com Python antes de gravar (`ordem_na_conta` como inteiro; campo opcional vazio sai do objeto, exceto `email`, `linkedin_url` e `primeira_frase`, que o schema aceita vazios):

```python
import json
from jsonschema import Draft202012Validator
schema = json.load(open("<motor>/schemas/contato.schema.json", encoding="utf-8"))
v = Draft202012Validator(schema, format_checker=Draft202012Validator.FORMAT_CHECKER)
erros = {i: [e.message for e in v.iter_errors(linha)] for i, linha in enumerate(contatos)}
assert not any(erros.values()), erros
```

**`rodadas/<rodada>/03-sem-contato.csv`**: `domain`, `company_name`, `motivo` (`sem_resultado_na_busca`, `sem_canal`, `suprimida:<motivo>`, `mudou_de_empresa`), `cargos_buscados`.

**`rodadas/<rodada>/03-creditos.md`**: por lote, a estimativa mostrada, quem aprovou e quando, as chamadas feitas, os créditos usados de cada `mcp_credits`, o saldo antes e depois.

## Metas e checagens antes de entregar

- Toda conta P0 e lista tem pelo menos 1 contato no `03-contatos.csv` ou uma linha no `03-sem-contato.csv`.
- Nenhum contato de canal `linkedin` ou `ambos` sem `linkedin_url`; nenhum de canal `email` ou `ambos` sem email `verified` (o schema reprova).
- Nenhuma conta com mais de 3 contatos; nenhum contato repetido (mesmo email ou mesmo LinkedIn).
- Todo contato com `cargo_checado_em` de hoje.
- Nenhuma `primeira_frase` apoiada em fato refutado.
- Créditos gastos registrados.
- Resposta ao operador: contas com contato, contas sem contato por motivo, contatos por canal e por papel, créditos gastos e saldo.

## Armadilhas

- **Filtro de pessoas não é filtro de empresa.** `organization_locations` é a sede; quem mora fora do país passa. Se o canal exige o país, usar `person_locations`.
- **ID de conta × ID de organização.** O filtro de pessoas quer ID de organização; na busca de empresas, linha do grupo `accounts` tem o ID de organização em `organization_id`.
- **Cargo do Apollo envelhece.** A pessoa saiu e o perfil não mudou. O match mostra a empresa atual: domínio diferente, descarta.
- **Título parecido engana.** "Gerente de contas" casa com "gerente" e não é persona de ninguém. O casamento é pelo cargo inteiro da persona dentro do título.
- **Email `likely` não é `verified`.** Não entra em sequência de email; vai por LinkedIn.
- **Waterfall e telefone custam à parte** e são assíncronos. Fora do padrão do motor; só com pedido do operador e aviso de custo variável.
- **Conta com um fio só.** Conta com 1 contato fica marcada no resumo pro operador decidir se abre por LinkedIn ou espera a próxima rodada.
