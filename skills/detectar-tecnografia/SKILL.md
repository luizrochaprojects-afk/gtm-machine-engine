---
name: detectar-tecnografia
description: "Detecta, conta a conta, quais ferramentas da tecnografia alvo do cliente ativo cada empresa usa: scripts e SDKs no HTML do site, vagas que pedem a ferramenta e menções públicas, com URL da fonte, tipo de evidência, confiança e leitura (fit, troca, concorrente). Chamada pela validar-lista antes do veredito; também roda sozinha sobre um CSV de domínios. Use quando o operador pedir tecnografia, stack, 'que ferramenta essa empresa usa', 'quem usa X nessa lista', 'confere o CRM dessas contas', 'detecta os scripts do site' ou 'acha quem está trocando de ferramenta'."
---

# Detectar tecnografia

Etapa E2, antes do veredito. Pra cada domínio, responde quais ferramentas da `tecnografia_alvo` do cliente a conta usa, com prova. A saída confirma fit (a conta já gasta com a categoria), mostra sinal de troca e aponta quem já usa o equivalente ao que o cliente vende.

A skill não sabe quem é o cliente. As ferramentas procuradas, os sinais de HTML e a leitura de cada uma vêm do `cliente.yaml` do workspace ativo.

## Ler antes

1. `cliente.yaml` → `tecnografia_alvo`: `nome`, `categoria`, `sinais_html` e `leitura` de cada ferramenta.
2. `doutrina/producao-com-agentes.md` (orçamento de busca, WebFetch primeiro, lotes).
3. `adapters/apollo/README.md` (custo de `apollo_organizations_job_postings`).

## Entradas

- Chamada pela `validar-lista`: os domínios do lote.
- Sozinha: um CSV com coluna `domain` (ex.: `rodadas/<rodada>/01-lista-crua.csv`) e o nome da rodada. Se o CSV tiver `technologies` (vindo do Apollo), usar como pista.

Sem `tecnografia_alvo` no `cliente.yaml`, parar e pedir ao operador a lista de ferramentas (nome, categoria, leitura).

## Passos

### 1. Montar a tabela de sinais

Pra cada ferramenta da `tecnografia_alvo`, a lista de sinais que denunciam a ferramenta no HTML: os `sinais_html` do `cliente.yaml` mais os que a skill conhece (domínio do script, nome do arquivo JS, objeto global, cookie, atributo de formulário). Exemplo fictício de formato:

| ferramenta | categoria | leitura | sinais |
|---|---|---|---|
| FerramentaX | email-marketing | fit | `static.ferramentax.com`, `ferramentax.js`, `_fx_id` |

Sinal que a skill acrescentou por conta própria vai marcado como "sugerido" e entra na lista de sugestões do passo 6.

### 2. HTML do site (WebFetch primeiro, sem busca)

Por domínio, no máximo 3 páginas: a home e 1 ou 2 páginas onde a ferramenta costuma carregar (carrinho, checkout, login, página de assinatura, central de ajuda, rodapé com "tecnologia"). Ordem:

1. Baixar o HTML cru, que preserva as tags de script: `curl -sL --max-time 20 -A "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36" https://<domain>/ -o rodadas/<rodada>/tmp/tec/<domain>-home.html`. Procurar os sinais com `grep -i -o` e guardar o trecho casado.
2. Se o `curl` for bloqueado (403, desafio de bot, página vazia), usar WebFetch pedindo explicitamente "liste todas as URLs de `<script src>`, `<link>` e `<iframe>` e os objetos globais citados em scripts inline". WebFetch converte a página e pode descartar scripts: resultado vazio no WebFetch não prova ausência.
3. **Tag manager.** Se o HTML só tiver o contêiner de um tag manager (ex.: `googletagmanager.com/gtm.js?id=GTM-XXXX`), baixar o próprio contêiner (`https://www.googletagmanager.com/gtm.js?id=GTM-XXXX`, público) e procurar os sinais dentro dele. Ferramenta achada no contêiner é `script_html` com a URL do contêiner como fonte.
4. **Site renderizado por JavaScript** (HTML quase vazio, um `<div id="root">` e um bundle): procurar os sinais dentro do bundle principal (`<script src>` do próprio domínio). Se ainda assim não aparecer nada e o Chrome do operador estiver conectado, abrir a página e ler as requisições de rede (`read_network_requests`) procurando os domínios dos sinais. Sem Chrome, registrar `resultado = site_js_sem_leitura`.

Uma ferramenta achada no HTML vira uma linha com `tipo_evidencia = script_html` e `fonte` = URL da página (ou do contêiner, ou do bundle) onde o sinal apareceu.

### 3. Vagas

Vaga que pede experiência com a ferramenta mostra uso e, às vezes, troca ("migração de X pra Y").

- **Padrão, sem crédito:** até 1 WebSearch por conta, ex.: `"<nome da empresa>" vaga "<ferramenta>"`, e a página de vagas do próprio site ou da plataforma de recrutamento dela. Conta no orçamento de busca da sessão.
- **Pelo Apollo, com crédito:** `apollo_organizations_lookup` (gratuita) pra achar o ID e `apollo_organizations_job_postings` (1 crédito por conta). Só com a estimativa do lote mostrada ("N contas = N créditos", com o saldo de `apollo_usage_stats_credit_usage_stats`), a frase de confirmação que a ferramenta exige e o "aprovado" do operador.

Vaga vira linha com `tipo_evidencia = vaga`, `fonte` = URL da vaga. Só conta vaga **da própria conta**: vaga publicada por agência, consultoria ou recrutadora em nome de um cliente não identificado não prova nada sobre a conta.

### 4. Menções públicas

Só se a ferramenta não apareceu no HTML nem em vaga, e dentro do teto de 2 WebSearch por conta (somando o passo 3): case publicado pelo fornecedor da ferramenta, página de integração do site da conta, notícia, perfil de funcionário que cita a ferramenta no cargo atual. Vira `tipo_evidencia = mencao_publica`.

### 5. Confiança e leitura

| Evidência | Confiança |
|---|---|
| Script ou SDK da ferramenta no HTML, no contêiner do tag manager ou no bundle | `alta` |
| Vaga da própria conta, aberta ou fechada há menos de 6 meses, pedindo a ferramenta | `media` |
| Case do fornecedor ou página de integração da própria conta, com data de menos de 1 ano | `media` |
| Só menção (notícia antiga, perfil de pessoa, post de terceiro, lista de "empresas que usam") | `baixa` |
| Só o campo `technologies` do Apollo | `baixa`, `tipo_evidencia = apollo`, `fonte` = URL da página da conta no Apollo ou do site |

`leitura` vem da `tecnografia_alvo` (`fit`, `troca`, `concorrente`). Duas ferramentas da mesma categoria na mesma conta, ou vaga que fala em migração, é sinal de troca: registrar as duas e anotar em `nota`.

Ferramenta não achada não vira linha no campo `tecnografia` do veredito: ausência de sinal não prova que a conta não usa. Ela aparece só no CSV (passo 6), com `resultado = nao_detectada`.

### 6. Gravar

**Formato devolvido à `validar-lista`**, por domínio, uma lista no formato do campo `tecnografia` de `schemas/veredito.schema.json`:

```json
[
  {"ferramenta": "FerramentaX", "fonte": "https://www.acme.com.br/", "tipo_evidencia": "script_html", "confianca": "alta", "leitura": "fit"}
]
```

**`rodadas/<rodada>/02-tecnografia.csv`**, UTF-8 com BOM, uma linha por domínio × ferramenta procurada:

| Coluna | Conteúdo |
|---|---|
| `domain` | domínio normalizado |
| `ferramenta` | nome da `tecnografia_alvo` |
| `categoria` | da `tecnografia_alvo` |
| `resultado` | `detectada`, `nao_detectada`, `site_inacessivel`, `site_js_sem_leitura` |
| `tipo_evidencia` | `script_html`, `vaga`, `mencao_publica`, `apollo` ou vazio |
| `fonte` | URL da evidência ou vazio |
| `sinal_encontrado` | trecho casado (ex.: `static.ferramentax.com/onsite.js`) |
| `confianca` | `alta`, `media`, `baixa` ou vazio |
| `leitura` | `fit`, `troca`, `concorrente` |
| `checado_em` | `AAAA-MM-DD` |
| `nota` | agência na vaga, contêiner de tag manager, possível troca |

**`rodadas/<rodada>/02-tecnografia-sinais-sugeridos.md`**, se a skill achou sinal novo: ferramenta, sinal, domínio e URL onde apareceu. Serve pro operador acrescentar em `sinais_html` do `cliente.yaml`. A skill não edita o `cliente.yaml`.

Antes de devolver, validar cada lista contra o item de `tecnografia` do schema com Python (`jsonschema`, subschema `properties.tecnografia`).

## Lote e orçamento

- Até 10 domínios: rodar direto na sessão.
- Mais de 10: um subagente por domínio (ou um workflow simples com um agente por domínio), com a tabela de sinais do passo 1 no prompt, teto de 2 WebSearch e 8 tool calls por domínio, e saída no formato do CSV. No máximo ~16 em paralelo (acima disso o fetch devolve 429).
- Resposta grande (HTML, bundle, contêiner) fica em arquivo em `rodadas/<rodada>/tmp/tec/` e é lida com `grep`, nunca inteira no contexto.

## Armadilhas

- **HTML renderizado por JavaScript esconde as tags.** Página que monta tudo no navegador mostra um HTML vazio. Procurar no bundle e, se possível, nas requisições de rede; sem isso, `site_js_sem_leitura`, nunca `nao_detectada`.
- **Tag manager esconde a ferramenta.** O HTML só mostra o contêiner; a ferramenta está dentro dele. Ler o contêiner.
- **Vaga de agência.** Agência anuncia vaga pedindo a ferramenta pra atender um cliente dela. Não é evidência da conta; e se a própria conta é agência, isso é assunto do desqualificador da `validar-lista`.
- **Só menção é confiança baixa.** Lista de "empresas que usam X", perfil de ex-funcionário e post antigo mostram no máximo que a conta já usou.
- **O `technologies` do Apollo erra e envelhece.** Serve de pista pra procurar no HTML, não de prova.
- **Script de ferramenta parecida.** Duas ferramentas podem usar domínios parecidos ou a mesma CDN. O sinal precisa ser específico da ferramenta; na dúvida, confiança `media` e nota.
- **Bloqueio por bot.** 403 ou desafio não é ausência: `site_inacessivel`.
