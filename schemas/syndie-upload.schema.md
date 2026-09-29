# Schema: CSV de upload da Syndie

Arquivo `rodadas/<rodada>/04-syndie-upload.csv`, gerado pela `syndie-flow-builder` a partir de `03-contatos.csv`. Uma linha por contato com canal `linkedin` ou `ambos`.

Levantado a partir de dois CSVs de upload que já rodaram (só os nomes das colunas; nenhuma linha de dado entrou no motor).

## Formato do arquivo

- UTF-8 sem BOM (os uploads que rodaram não tinham BOM).
- Separador vírgula; campos com vírgula entre aspas duplas.
- Primeira linha é o cabeçalho, com os nomes exatamente como abaixo.
- Uma campanha da Syndie por arquivo: um arquivo por grupo de segmento e oferta (a Syndie não personaliza por variável custom, então segmentos diferentes precisam de campanhas diferentes).

## Colunas nativas (a Syndie lê e popula nas mensagens)

Obrigatórias, nesta ordem, no início do arquivo.

| Coluna | Variável no prompt | Conteúdo | De onde vem |
|---|---|---|---|
| `first_name` | `{{first_name}}` | Primeiro nome, com acento, sem sobrenome | `primeiro_nome` do contato |
| `last_name` | `{{last_name}}` | Sobrenome | `nome` do contato menos o primeiro nome |
| `linkedin_url` | não | URL do perfil `https://www.linkedin.com/in/<slug>` | `linkedin_url` do contato |
| `company` | `{{company}}` | Nome da empresa como a pessoa fala (sem "Ltda", "S.A.") | `company_name` do veredito |
| `title` | `{{title}}` | Cargo | `cargo` do contato |

Só estas quatro variáveis (`first_name`, `last_name`, `company`, `title`) podem aparecer em `message`, `customGuidelines` e `customComment` do fluxo. `scripts/validate_syndie_flow.py` reprova outras.

## Colunas de controle (a Syndie guarda, mas não popula nas mensagens)

Opcionais. Servem pra auditoria, pro filtro dentro da Syndie e pro retorno ao ledger. Nunca referenciar no prompt.

| Coluna | Conteúdo |
|---|---|
| `primeiro_nome` | Igual a `first_name` (legado; usado por fluxos antigos) |
| `empresa` | Igual a `company` (legado) |
| `dominio` | Domínio normalizado; chave de volta pro ledger |
| `papel` | `decisor`, `champion`, `influenciador` |
| `trilha` | id da oferta |
| `tier` | `1`, `2`, `3` |
| `veredito_conta` | `P0`, `lista` |
| `score_conta` | 0 a 100 |
| `email` | Email do contato, se houver |
| `email_status` | Status do enrich |
| `fonte` | De onde veio o contato |
| `ordem_na_conta` | 1 a 3 |
| `entra_na_cadencia` | `sim` ou `nao` |
| `headline` | Headline do LinkedIn |
| `cargo_checado_em` | `AAAA-MM-DD` |
| `sinal` | Sinal de prontidão da conta, se houver |
| `funcionarios`, `cidade`, `estado` | Firmografia |
| `modelo_atual`, `esp_atual`, `tamanho_base`, `time_crm` | Campos de pesquisa da conta (variam por cliente) |

## Regras

- Linha sem `linkedin_url` válida não entra.
- Linha cuja `linkedin_url` está na aba `supressao` do ledger (tipo `linkedin`) não entra; `scripts/suppress.py` roda antes.
- Linha com `entra_na_cadencia = nao` não entra.
- URLs normalizadas: `https://www.linkedin.com/in/<slug>`, sem barra final, sem parâmetros.
