---
name: registrar-ledger
description: Grava uma rodada de outbound no ledger do cliente (Google Sheets) e copia pro CRM configurado. Escreve contas e contatos da rodada (estágio Working, rodada, trilha, veredito, tier, score, tecnografia, fato de abordagem, fonte), cria a linha da rodada com as fórmulas do funil, registra os toques enviados depois do lançamento, exporta o snapshot CSV de cada aba no fim da rodada e roda o adaptador do CRM do cliente.yaml (account-guardian, hubspot ou nenhum) sem bloquear o lançamento. Use na etapa E6 e no fim da rodada, quando o operador disser "registra no ledger", "sobe a rodada pro ledger", "grava os toques", "fecha a rodada", "snapshot do ledger", "manda pro CRM", "roda a registrar-ledger".
---

# registrar-ledger

O ledger é a memória da máquina: quem foi abordado, quando, por qual canal e com que resultado. Esta skill é quem escreve nele por uma rodada, em três momentos, e depois copia o que interessa pro CRM do cliente.

A skill não sabe quem é o cliente. O ID da planilha (`ledger_id`), o CRM (`crm`), as ofertas e os donos de gate vêm do `cliente.yaml`.

| Fase | Quando | O que escreve |
|---|---|---|
| 1. Rodada | Depois da montagem (Apollo e Syndie prontos), antes do QA | Contas, contatos, linha da rodada |
| 2. Toques | Depois do lançamento (H3 aprovado e envio acontecendo) | Toques `enviado` do primeiro passo de cada canal; adaptador do CRM |
| 3. Fechamento | Fim da rodada, quando o operador declarar | Snapshot CSV de cada aba |

## Antes de começar: o que ler

| # | Arquivo | O que tirar dele |
|---|---|---|
| 1 | `adapters/google-sheets/README.md` | Regras de leitura e escrita: ler antes de escrever, só colunas cinza, `'` pra texto, `;` nas fórmulas, `append_values` pra linha nova, o que fazer em erro. **Obrigatório.** |
| 2 | `schemas/ledger.schema.md` | Abas, colunas, dono, formato, valores fechados, chaves, fórmulas da aba `rodadas` |
| 3 | `cliente.yaml` | `ledger_id`, `crm`, `ofertas`, `stack` |
| 4 | Arquivos da rodada | Vereditos (`02-validacao.xlsx` ou JSON), `03-contatos.csv`, `04-apollo-import.csv`, `04-apollo-ids.json`, `04-syndie-upload*.csv`, `05-qa-lancamento.md` |
| 5 | `adapters/<crm>/README.md` | Quando `crm` não for `nenhum` |

## Fase 1: contas, contatos e linha da rodada

### Quem entra

- **Contas:** as que têm pelo menos um contato lançado na rodada (em `04-apollo-import.csv` ou em `04-syndie-upload*.csv`). Estágio `Working`. Contas com veredito `nutrir` podem entrar com estágio `Nutrir` se o operador pedir; `fora` não entra.
- **Contatos:** os que estão em `04-apollo-import.csv` ou em `04-syndie-upload*.csv`, com os dados de `03-contatos.csv`.

### Antes de escrever

1. Ler o cabeçalho de `contas`, `contatos` e `rodadas` (`<aba>!1:1`), montar o mapa nome → letra e conferir contra o schema. Diferença: parar.
2. Ler a coluna-chave de cada aba (`contas!A:A`, `contatos!A:A`, `rodadas!A:A`). Chave repetida: parar e avisar com os números das linhas.
3. Montar as linhas a escrever e mostrar o resumo ao operador: contas novas, contas que vão ser atualizadas, contatos novos, contatos atualizados.

### Campos da aba `contas`

| Coluna | Valor |
|---|---|
| `dominio` | `'` + domínio normalizado (`scripts/normalize_domain.py`) |
| `empresa` | `company_name` do veredito |
| `rodada` | nome da rodada |
| `segmento` | slug do segmento |
| `trilha` | `trilha` do veredito (id de oferta, `ambas` ou `incerta`) |
| `veredito` | `P0`, `lista`, `nutrir` ou `fora` |
| `tier` | número 1, 2 ou 3, sem `'` |
| `score` | número 0 a 100, sem `'` |
| `tecnografia` | `ferramenta` de cada item de `tecnografia[]`, separadas por `; ` |
| `fato_abordagem` | `fato` da evidência em `primeira_frase_evidencia_idx` (com `'` se começar com `=`, `+`, `-` ou `@`) |
| `fonte_url` | `url` da mesma evidência |
| `estagio` | `Working` |
| `atualizado_em` | `'AAAA-MM-DD` de hoje |

### Campos da aba `contatos`

| Coluna | Valor |
|---|---|
| `contato_id` | `'<dominio>:<slug-do-nome>`; slug = nome completo em caixa baixa, sem acento, espaços viram hífen (`acme.com.br:ana-souza`) |
| `dominio` | `'` + domínio normalizado |
| `nome`, `cargo`, `papel`, `canal`, `email`, `email_status`, `linkedin_url` | de `03-contatos.csv` (email em caixa baixa; URL normalizada `https://www.linkedin.com/in/<slug>`) |
| `rodada` | nome da rodada |
| `atualizado_em` | `'AAAA-MM-DD` de hoje |

### Escrever

1. **Linha que já existe** (achada pela chave):
   1. Ler a linha inteira imediatamente antes de escrever.
   2. `nao_abordar = sim`: não escrever; listar no relatório (e a conta ou o contato não devia estar na rodada: avisar).
   3. Conta com `estagio` `Respondeu`, `Reuniao`, `Oportunidade` ou `Cliente`: não escrever; avisar. Não se rebaixa estágio.
   4. `update_values` no intervalo exato da linha, só nas colunas cinza (em `contas`, até a coluna M; em `contatos`, até a K), com os valores novos. Coluna cinza que não muda vai com o valor que está lá (lido no passo 1). Colunas amarelas ficam fora do intervalo.
2. **Linha nova:** `append_values` em `<aba>!A1`, só as colunas cinza, na ordem do cabeçalho. Até 500 linhas por chamada. Depois, ler a coluna-chave e conferir que cada chave aparece uma vez só.
3. Não deixar linha vazia no meio da aba.

### Linha da rodada

1. Se `rodada_id` já existe em `rodadas!A:A`: não criar outra. Conferir que as fórmulas de F a K estão lá; se faltarem, escrever só as que faltam.
2. Senão, seguir "Linha nova na aba `rodadas`" do `adapters/google-sheets/README.md`: `append_values` com A a E (`rodada_id`, `segmento`, `oferta` = `<id> · <nome>`, `canais` = `LinkedIn + email`, `LinkedIn` ou `email` conforme a rodada, `inicio` = `'AAAA-MM-DD`), achar a linha `N`, `update_formulas` em `F<N>:K<N>` com as fórmulas do schema com `;`, e ler de volta conferindo que nenhuma célula voltou com erro.
3. Conferir `properties.locale = pt_BR` antes da primeira fórmula. Se não for, parar.
4. As colunas L (`decisao_h3`) e M (`nota`) são humanas. Não escrever.

## Fase 2: toques e CRM

### Toques

O schema não tem evento "agendado": toque só entra quando o envio aconteceu. A skill registra o **primeiro passo de cada canal** (`D1` do email e `convite` do LinkedIn) no dia em que ele sai. Os passos seguintes, aceites, respostas, bounces e optouts são da triagem de respostas (S2); até ela existir, o operador pede esta fase de novo pra registrar `enviado` dos passos seguintes.

1. Só com "H3 aprovado" no `05-qa-lancamento.md` e data e hora preenchidas no bloco "Lançamento".
2. **Email (Apollo):** pra cada contato inscrito (`inscricoes` do `04-apollo-ids.json`), confirmar o envio com `apollo_emailer_messages_search` (mensagens da sequência) ou `apollo_emailer_campaigns_activity_feed`. Só o que o Apollo mostra como enviado vira toque; o resto espera a próxima execução.
3. **LinkedIn (Syndie):** sem API. Pedir ao operador o export de leads da campanha com o status (ou a confirmação de que os convites saíram em tal data). Sem fonte, não registrar: anotar "toques de LinkedIn pendentes" no relatório.
4. Pra cada envio confirmado, montar a linha: `toque_id` = `'<contato_id>:<rodada>:<passo>:enviado`, `data` = `'AAAA-MM-DD HH:MM` do envio, `contato_id`, `dominio`, `canal` (`email` ou `linkedin`), `ferramenta` (`apollo` ou `syndie`), `rodada`, `passo` (`D1` ou `convite`), `evento` = `enviado`, `classificacao` vazia.
5. Ler `toques!A:A` e tirar do lote todo `toque_id` que já existe (a fase pode rodar mais de uma vez). `append_values` em `toques!A1` só com as colunas cinza (A a J). Aba `toques` nunca é editada.
6. Registrar o mesmo dia do envio. Toque que demora a entrar no ledger deixa a pessoa fora da supressão de "abordado sem resposta" de outra rodada.

### Adaptador do CRM

Depois dos toques do primeiro dia, rodar o adaptador do `crm` do `cliente.yaml`. **Nunca bloqueia o lançamento:** falha vira pendência no relatório.

| `crm` | O que fazer |
|---|---|
| `account-guardian` | Seguir `adapters/account-guardian/README.md`. Gerar sempre `rodadas/<rodada>/crm/account-guardian-contas.csv` e `account-guardian-contatos.csv` (caminho A, com o passo a passo pro operador). Oferecer o caminho B (MCP, uma a uma) e só seguir com o sim do operador, mostrando o lote antes. |
| `hubspot` | Adaptador fora do escopo da v0.1. Gerar `rodadas/<rodada>/crm/hubspot-contas.csv` (`domain`, `name`, `segmento`, `trilha`, `rodada`) e `hubspot-contatos.csv` (`email`, `firstname`, `lastname`, `jobtitle`, `company`, `domain`, `linkedin_url`, `rodada`) em UTF-8 com BOM, e escrever no relatório: importar pela interface do HubSpot (Contatos → Importar → arquivo, associando contatos a empresas pelo domínio); passo a passo não testado. |
| `nenhum` | Pular. Anotar "cliente sem CRM" no relatório. |

Direção só ledger → CRM. Nada do CRM volta pro ledger nesta skill.

## Fase 3: fechamento da rodada

Quando o operador declarar a rodada encerrada (em geral, sete dias depois do último D13 e da última DM):

1. Seguir "Snapshot no fim da rodada" do `adapters/google-sheets/README.md`: `contas`, `contatos`, `toques`, `supressao`, `reunioes` e `rodadas`, cada uma em `rodadas/<rodada>/ledger/<aba>.csv`, UTF-8, cabeçalho incluído, colunas cinza e amarelas.
2. Conferir que o número de linhas de cada CSV bate com o da aba.
3. Avisar o operador que o `loop-de-licoes` já pode rodar sobre a rodada.

## O que gravar e onde

| Arquivo | Fase |
|---|---|
| Ledger (Google Sheets): abas `contas`, `contatos`, `rodadas` | 1 |
| Ledger: aba `toques` | 2 |
| `rodadas/<rodada>/crm/*` | 2 |
| `rodadas/<rodada>/ledger/<aba>.csv` | 3 |
| `rodadas/<rodada>/06-registro-ledger.md` | todas: uma seção por execução, com data, fase, linhas anexadas e atualizadas por aba, linhas não escritas e por quê, toques pendentes, resultado do CRM |

Fim de cada execução: resumo curto ao operador com as mesmas informações e o que está pendente.

## Gates

- Fase 1 roda antes do QA; a `qa-lancamento` confere que ela foi feita.
- Fase 2 só depois de "H3 aprovado" no `05-qa-lancamento.md`.
- A skill não escreve em coluna humana, incluindo `decisao_h3`.

## Armadilhas

- **Escrever sem ler a linha.** O operador pode ter marcado `nao_abordar` um minuto antes.
- **Intervalo que pega coluna amarela.** O intervalo de escrita termina na última coluna cinza.
- **Data sem `'`** vira data do Sheets e volta diferente na leitura.
- **Fórmula com vírgula** falha em pt_BR.
- **Toque "agendado".** Não existe no schema. Só `enviado`, confirmado na ferramenta.
- **Toque duplicado** ao rodar a fase 2 duas vezes. Conferir `toque_id` antes de anexar.
- **Conta que volta** numa rodada nova tem a linha atualizada, não duplicada.
- **CRM travando a rodada.** Erro no CRM é pendência, não bloqueio. E erro de qualificação do Account Guardian é o processo funcionando: não contornar.
