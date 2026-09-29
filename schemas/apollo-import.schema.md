# Schema: CSV de import do Apollo

Dois arquivos, gerados pela `apollo-sequence-builder`: `rodadas/<rodada>/04-apollo-import-contas.csv` (contas) e `rodadas/<rodada>/04-apollo-import.csv` (contatos). Serve de registro do que foi criado no Apollo pelo MCP e de caminho alternativo de import pela interface (Lists → Import) quando o MCP falhar.

Levantado a partir de um CSV de import de Account List que já rodou (só nomes de colunas; nenhuma linha de dado entrou no motor). O arquivo de origem tinha só `dominio` e `empresa`, sem BOM; o motor padroniza os nomes de coluna em inglês (que o Apollo casa sozinho no import) e acrescenta os campos da rodada.

## Formato do arquivo

- **UTF-8 com BOM** (sem BOM, o import do Apollo pela interface quebra acentos).
- Separador vírgula; campos com vírgula entre aspas duplas.
- **`domain` sem `http`, sem `www`, sem barra final, em caixa baixa.** É a chave de match do Apollo. Normalizar com `scripts/normalize_domain.py`.

## Import de contas (Account List) · `04-apollo-import-contas.csv`

Mínimo aceito pelo Apollo: `domain` e `company_name`.

| Coluna | Obrigatória | Conteúdo |
|---|---|---|
| `domain` | sim | Domínio normalizado |
| `company_name` | sim | Nome canônico da conta |
| `segmento` | não | Slug do segmento (campo custom de conta) |
| `trilha` | não | id da oferta (campo custom de conta) |
| `veredito` | não | `P0` ou `lista` |
| `tier` | não | `1`, `2`, `3` |
| `rodada` | não | Nome da rodada; também vira o rótulo (label) |

## Import de contatos · `04-apollo-import.csv`

Uma linha por contato com canal `email` ou `ambos`.

| Coluna | Obrigatória | Conteúdo |
|---|---|---|
| `first_name` | sim | Primeiro nome, com acento |
| `last_name` | sim | Sobrenome |
| `email` | sim | Email com `email_status = verified` |
| `title` | sim | Cargo |
| `company_name` | sim | Nome da conta |
| `domain` | sim | Domínio normalizado |
| `linkedin_url` | não | URL do perfil |
| `primeira_frase` | não | Abertura personalizada da conta (campo custom de contato) |
| `segmento` | não | Campo custom |
| `trilha` | não | Campo custom |
| `rodada` | não | Nome da rodada |

Os campos custom (`primeira_frase`, `segmento`, `trilha`) precisam existir no Apollo antes do import (Settings → Fields, ou `apollo_fields_create`). A `apollo-sequence-builder` confere com `apollo_fields_index` antes de subir.
