---
name: montar-tam
description: "Monta o TAM de um segmento e oferta do cliente ativo: traduz o gabarito de ICP em filtros do Apollo, roda a busca e o lookalike das contas âncora, junta listas de rodadas anteriores, normaliza domínio, deduplica, aplica a supressão do ledger e grava a lista crua da rodada com o tamanho por hipótese de ICP. Use quando o operador pedir pra montar TAM, montar ou puxar lista, buscar contas no Apollo, fazer lookalike, abrir rodada nova, 'quantas contas cabem nesse segmento', 'traz as empresas desse ICP', 'monta a lista da r2' ou 'reaproveita a lista antiga'."
---

# Montar TAM

Etapa E1. Sai daqui a lista crua de uma rodada: todas as contas do segmento que podem ser abordadas, uma vez cada, sem ninguém da supressão, com a fonte e a hipótese de ICP que trouxe cada uma. A skill não qualifica conta (isso é da `validar-lista`) e não gasta crédito de enrich sem aprovação.

A skill não sabe quem é o cliente. Tudo que muda por cliente vem do workspace ativo (`clientes/<slug>/`).

## Ler antes

1. `cliente.yaml`: `ofertas` (id e segmentos de cada oferta), `ledger_id`, `crm`, `supressao`, `tecnografia_alvo`, `personas`.
2. `estrategia/gabarito-icp.md` (formato em `schemas/gabarito.schema.md`). Sem as quatro seções obrigatórias, parar e avisar.
3. `estrategia/hipoteses-icp.md`, se existir: cada hipótese vira uma busca própria. Sem o arquivo, a rodada tem uma hipótese só, com o nome do segmento.
4. `segmentos/<segmento>/busca-apollo.md` da rodada anterior, se existir. Rodada nova parte dele e registra o que mudou.
5. `segmentos/<segmento>/ancoras.csv` (coluna `domain`, opcional `motivo`): contas que já compraram ou que o cliente aponta como modelo. Sem o arquivo, perguntar ao operador se há âncoras; se houver, gravar o arquivo antes de seguir.
6. `doutrina/outbound.md`, seção "Sinais e listas".
7. `adapters/apollo/README.md`: custo e limite de cada ferramenta.

Perguntar ao operador, se não estiver claro: segmento, oferta, número da rodada e se há listas anteriores pra reaproveitar.

## Nome da rodada

`AAAA-MM-DD-rN-<segmento>-<oferta>`, com a data de hoje, `N` sequencial por workspace (olhar `rodadas/`) e o id da oferta do `cliente.yaml`. Exemplo: `2026-10-05-r2-ecommerce-recompra-plataforma`. Criar `rodadas/<rodada>/`.

## Passos

### 1. Traduzir o gabarito em filtros

Ler cada critério do gabarito e decidir se ele vira filtro do Apollo, filtro local (depois da busca) ou fica pra `validar-lista`. Regra:

| Papel no gabarito | Vira | Como |
|---|---|---|
| `gate` que o Apollo mede bem (porte, sede, faixa de receita) | filtro positivo da busca | `organization_num_employees_ranges`, `organization_locations`, `revenue_range` |
| `gate` que só o site prova (recompra, checkout próprio, assinatura) | palavra-chave larga + checagem na `validar-lista` | `q_organization_keyword_tags` com os termos que costumam acompanhar o fato; nunca tratar a palavra-chave como prova |
| `qualifica` ligado a ferramenta | tecnologia | `currently_using_any_of_technology_uids` com os nomes da `tecnografia_alvo` de leitura `fit` ou `troca` (espaço e ponto viram `_`) |
| `qualifica` ou `dimensiona` descritivo | palavra-chave, segmento de mercado ou nada | `q_organization_keyword_tags`, `market_segments`; se não houver tradução honesta, fica pra `validar-lista` |
| `sinal` de vaga ou captação | hipótese separada "com sinal", nunca filtro da busca principal | `q_organization_job_titles` + `organization_job_posted_at_range`; `latest_funding_date_range` |
| desqualificador `duro` que tem código de setor | exclusão na busca | `not_organization_naics_codes`, `not_organization_sic_codes`, `organization_not_locations` |
| desqualificador `duro` descritivo (agência, consultoria, B2B puro) | negativo local | lista de termos procurados em `keywords`, `industry` e `short_description` depois da busca |
| desqualificador `validacao` | nada aqui | fica pra `validar-lista` |
| `pergunta` (discovery) | nada | não se vê de fora |

Porte: o `cliente.yaml` usa `51-200`; a API espera `"51,200"`. Tecnologia da `tecnografia_alvo` com leitura `concorrente` não entra como filtro positivo: a conta que já usa o equivalente ao que o cliente vende é caso da `validar-lista`.

Gravar a tradução em `segmentos/<segmento>/busca-apollo.md` no formato abaixo e mostrar ao operador. **Nenhuma busca roda antes do "aprovado" do operador na busca.** O bloco JSON de cada hipótese é o conjunto de filtros explícito que as ferramentas de busca exigem: a skill não inventa nem expande valor na hora da chamada.

~~~markdown
# Busca Apollo · <segmento> · <oferta>

Versão <n> · <AAAA-MM-DD> · gabarito versão <n> · aprovada por <papel> em <AAAA-MM-DD>
Mudou desde a versão anterior: <o quê e por quê, ou "primeira versão">

## Critério → filtro

| id | critério | papel | vira | parâmetro | valor |
|---|---|---|---|---|---|
| F1 | Recompra ou assinatura | gate | palavra-chave + validar-lista | q_organization_keyword_tags | assinatura, clube, recorrência |
| F2 | Já gasta com CRM ou mídia | qualifica | tecnologia | currently_using_any_of_technology_uids | klaviyo, rd_station |
| D1 | Agência | duro | negativo local | keywords, industry, short_description | agência, consultoria, white label |
| S1 | Vaga de CRM aberta | sinal | hipótese com sinal | q_organization_job_titles | analista de crm, lifecycle |

## Hipótese <id>: <nome>

Racional em uma linha (de `estrategia/hipoteses-icp.md`).

```json
{
  "organization_locations": ["Brazil"],
  "organization_num_employees_ranges": ["51,200", "201,500"],
  "q_organization_keyword_tags": ["assinatura", "clube de assinatura"],
  "currently_using_any_of_technology_uids": ["klaviyo"],
  "not_organization_naics_codes": ["5418"],
  "per_page": 100
}
```

Negativos locais: agência, consultoria, software house, atacado, distribuidora.

## Lookalike das âncoras

(passo 3)

## Ordem de seleção

Como a lista é ordenada pra formar os lotes (passo 7).
~~~

Uma hipótese por bloco. Filtro de tecnologia e de palavra-chave são "qualquer um de": uma hipótese com tecnologia E palavra-chave fica estreita demais; se a contagem do passo 2 vier abaixo de 50, separar em duas hipóteses.

### 2. Contar e buscar

1. Pra cada hipótese, contar com `apollo_organizations_lookup` usando os mesmos filtros (gratuita; devolve só id, nome e domínio). Mostrar a contagem por hipótese.
2. Chamar `apollo_usage_stats_credit_usage_stats` e rodar a primeira página de `apollo_mixed_companies_search` (`per_page: 100`, `page: 1`) da primeira hipótese. Ler o `mcp_credits` da resposta: se a busca cobrar, mostrar o custo por página × páginas previstas (`ceil(total ÷ 100)`) e pedir aprovação antes de paginar. Se a hipótese for grande demais pro orçamento, paginar só o necessário pros lotes das próximas rodadas e guardar a contagem total da etapa 1 como tamanho do TAM.
3. Paginar até acabar ou até o teto aprovado. De cada linha, guardar: domínio, nome, `estimated_num_employees`, `industry`, `keywords`, `technology_names` (ou equivalente), `linkedin_url`, ID de organização e descrição curta. Linha do grupo `accounts` usa `organization_id`, não `id`.
4. Gravar a resposta crua de cada página em `rodadas/<rodada>/tam/busca-<hipotese>-p<n>.json` e extrair as colunas com Python. Resposta grande não se relê inteira no contexto.
5. Marcar `fonte = apollo_busca` e `hipotese = <id da hipótese>`.

### 3. Lookalike das contas âncora

O MCP não tem busca de lookalike nativa. A skill monta uma busca parecida a partir do que as âncoras têm em comum:

1. Buscar as âncoras com `apollo_mixed_companies_search` e `q_organization_domains_list` (até 100 por chamada). Âncora que voltar sem palavras-chave ou tecnologias pode ser enriquecida com `apollo_organizations_enrich` (1 crédito cada), só com a frase de confirmação e o "aprovado" do operador.
2. Calcular o perfil comum, com Python sobre as respostas:
   - **Porte:** a faixa de cada âncora e a faixa vizinha de cada lado.
   - **Sede:** os países (ou estados) que aparecem em pelo menos metade das âncoras.
   - **Palavras-chave:** as que aparecem em pelo menos 2 âncoras (ou em pelo menos 40% delas, o que for maior), tirando termos genéricos (`e-commerce`, `internet`, `retail`, `b2c`) que trazem o mundo inteiro.
   - **Tecnologias:** as que aparecem em pelo menos metade das âncoras e estão na `tecnografia_alvo` ou são da mesma categoria.
   - **Setor:** o `industry` mais frequente, só como conferência (a busca não filtra setor por texto).
3. Gravar o perfil na seção "Lookalike das âncoras" do `busca-apollo.md`: a tabela âncora × porte × palavras-chave × tecnologias, os valores escolhidos e o JSON da busca. Mostrar ao operador e rodar só depois do "aprovado", como no passo 2.
4. Tirar as próprias âncoras do resultado. Marcar `fonte = lookalike` e `hipotese = lookalike` (ou o id da hipótese que a âncora representa, se `hipoteses-icp.md` ligar âncoras a hipóteses).

Menos de 3 âncoras não fazem perfil: avisar e pular o lookalike.

### 4. Listas anteriores como fonte extra

Aceitar qualquer CSV com coluna de domínio (`domain`, `dominio`, `website`): `rodadas/<rodada-antiga>/01-lista-crua.csv`, `02-validacao.json` antigo, lista enviada pelo cliente, export de outra ferramenta.

- Marcar `fonte = lista:<nome do arquivo>` e `hipotese` da lista, se ela tiver; senão `hipotese = lista-anterior`.
- Conta que já tem veredito em `02-validacao.json` de rodada anterior com menos de 90 dias leva o veredito junto em `short_description` (`veredito anterior: lista em 2026-09-10`), pra `validar-lista` não pesquisar de novo sem motivo.
- Colunas que a lista não tiver ficam vazias. Não preencher por inferência.

### 5. Normalizar e deduplicar

1. Juntar todas as fontes num CSV só, `rodadas/<rodada>/tam/juntas.csv`, com as colunas da lista crua.
2. Normalizar: `python scripts/normalize_domain.py --csv rodadas/<rodada>/tam/juntas.csv --coluna domain --saida rodadas/<rodada>/tam/normalizadas.csv`. Linha sem domínio não entra; anotar quantas.
3. Deduplicar por `domain` com Python: uma linha por domínio. A linha que fica é a da fonte com mais colunas preenchidas; `fonte` e `hipotese` guardam todas as fontes e hipóteses que trouxeram o domínio, separadas por `; ` (ex.: `apollo_busca; lookalike`). Contar quantas duplicatas saíram.
4. Aplicar os negativos locais do `busca-apollo.md`: termo achado em `keywords`, `industry` ou `short_description` tira a linha e grava o motivo `negativo:<termo>`.

### 6. Aplicar a supressão

1. Exportar o ledger: com o conector do Google Sheets (`get_values`), ler as abas `supressao`, `contas`, `contatos` e `toques` da planilha `ledger_id` e gravar cada uma como CSV com cabeçalho em `rodadas/<rodada>/_snapshot/<AAAA-MM-DD-HHMM>/<aba>.csv` (UTF-8; uma pasta por execução, com a hora da exportação). Localizar colunas pelo nome do cabeçalho. Aba vazia vira CSV só com cabeçalho. Nos passos seguintes, `<snapshot>` é essa pasta.
2. Se o `crm` do `cliente.yaml` não for `nenhum` e o operador tiver um export do CRM mais novo que a última importação pra aba `supressao`, acrescentar os domínios dele ao `<snapshot>/supressao.csv` com `motivo` `cliente` ou `pipeline` e `origem = export-crm-<AAAA-MM-DD>`. Isso muda só a cópia local; subir as linhas pro ledger é da `registrar-ledger` ou do operador.
3. Rodar:

```bash
python scripts/suppress.py --lista rodadas/<rodada>/tam/dedup.csv \
  --ledger-dir rodadas/<rodada>/_snapshot/<AAAA-MM-DD-HHMM> \
  --saida rodadas/<rodada>/tam/filtrado.csv \
  --removidos rodadas/<rodada>/tam/removidos.csv \
  --col-dominio domain --nivel contas
```

`--nivel contas` é obrigatório aqui: sem ele, o script trata como lista de contatos qualquer lista que tenha coluna `email` ou `linkedin_url`, e a lista crua tem `linkedin_url` da página da empresa. Em modo contatos, o "abordado sem resposta" seria procurado por pessoa, não por domínio, e conta já tocada passaria.

4. Somar os removidos pela coluna `motivo_supressao` do `removidos.csv` (`supressao:<motivo da aba>`, `nao_abordar_conta`, `toque_sem_resposta`), mais os negativos locais do passo 5.

### 7. Ordenar e cortar lotes

Ordem de seleção, gravada no `busca-apollo.md`:

1. Hipótese na ordem de prioridade de `hipoteses-icp.md`.
2. Dentro da hipótese: conta trazida por mais de uma fonte primeiro; depois a que tem tecnologia da `tecnografia_alvo` de leitura `fit`; depois o porte do meio da faixa do gabarito.
3. Desempate por domínio, em ordem alfabética (a ordem precisa ser reproduzível).

Lotes de 20 a 40 contas na ordem acima. O primeiro lote de um segmento ou de um gabarito novo é o piloto de 10 contas da `validar-lista`.

### 8. Gravar

**`rodadas/<rodada>/01-lista-crua.csv`**, UTF-8 com BOM, na ordem de seleção, com estas colunas e nesta ordem:

| Coluna | Conteúdo |
|---|---|
| `domain` | domínio normalizado |
| `company_name` | nome da conta como o Apollo ou a lista trouxe |
| `fonte` | `apollo_busca`, `lookalike`, `lista:<arquivo>`; várias separadas por `; ` |
| `hipotese` | id da hipótese; várias separadas por `; ` |
| `employees` | número de funcionários (inteiro) ou vazio |
| `industry` | setor do Apollo |
| `keywords` | palavras-chave separadas por `; ` |
| `technologies` | tecnologias separadas por `; ` |
| `linkedin_url` | página da empresa no LinkedIn |
| `apollo_org_id` | ID de organização do Apollo (pista, não chave) |
| `short_description` | descrição curta do Apollo ou nota da lista anterior |

**`segmentos/<segmento>/tam-AAAA-MM-DD.md`**:

```markdown
# TAM · <segmento> · <oferta> · <AAAA-MM-DD>

Rodada: <rodada> · busca: busca-apollo.md versão <n> · gabarito versão <n>

## Total por hipótese

| hipótese | contagem no Apollo (lookup) | trazidas | depois de dedup | depois de supressão | lotes de 30 |
|---|---|---|---|---|---|

## Total por fonte

| fonte | linhas | únicas (só essa fonte) |
|---|---|---|

## Removidos por motivo

| motivo | contas |
|---|---|
| sem domínio | |
| duplicata | |
| negativo:<termo> | |
| <motivo_supressao do suppress.py> | |

## Lotes

Lote piloto: linhas 1 a 10. Lote 1: linhas 11 a 40. ...

## Créditos

Estimativa mostrada, aprovação (quem, quando), gasto real e saldo, do `mcp_credits`.

## Leitura

Quantas rodadas cada hipótese aguenta no ritmo do `cliente.yaml`; hipótese que veio pequena demais ou larga demais e o ajuste proposto na busca.
```

Os arquivos intermediários ficam em `rodadas/<rodada>/tam/`.

## Gate e conferência antes de entregar

- Busca aprovada pelo operador antes da primeira chamada. Nenhum crédito de enrich sem estimativa e "aprovado".
- Nenhum domínio repetido em `01-lista-crua.csv` (conferir com Python).
- Nenhum domínio do `<snapshot>/supressao.csv` e nenhum com `nao_abordar = sim` na lista (rodar a checagem de novo sobre o arquivo final).
- Total por hipótese registrado com a data.
- Resposta ao operador: total por hipótese, removidos por motivo, número de lotes, créditos gastos e o que a skill recomenda mudar na busca.

## Armadilhas

- **Palavra-chave não é prova.** "assinatura" no Apollo aparece em quem vende software de assinatura. O gate é provado no site, pela `validar-lista`.
- **O Apollo erra.** Descrição colada na empresa errada, setor errado, homônimo. Não corrigir aqui; a `validar-lista` resolve o negócio real.
- **Sinal de vaga do Apollo é ruidoso.** Vaga "de CRM" costuma ser vaga de vendas que cita CRM no texto. Hipótese "com sinal" só vira sequência de vaga depois de checada.
- **Agência entra por tecnologia.** Quem implanta a ferramenta pra terceiros também "usa" a ferramenta. Negativar agência na origem.
- **Âncora grande distorce o lookalike.** Uma âncora enterprise puxa o porte pra cima. Porte do lookalike respeita o gate de porte do gabarito.
- **Grupo `accounts` da busca.** O `id` ali é de conta salva no time; o ID de organização está em `organization_id`.
- **Exclusão por lista não existe na API.** A supressão é sempre local, pelo `suppress.py`, com o snapshot do ledger da própria rodada.
- **`apollo_plan_limit`.** Se aparecer, a resposta ao operador é o `message` do bloco, literal, e a skill para.
