# Verificar vaga no LinkedIn pelo Chrome do operador

Usada pela `validar-lista` quando o gatilho da rodada é vaga (um critério `sinal` do gabarito do tipo "vaga de <área> aberta"). A área e os títulos que contam vêm do gabarito do workspace (coluna `como verificar` do critério de vaga), nunca deste arquivo.

## Por que existe

WebFetch no LinkedIn é bloqueado por robots.txt, então a pesquisa web marca a vaga como "incerto" mesmo quando ela existe. Numa rodada real, 7 de 15 "incerto" viraram "sim" quando checados pelo navegador. "incerto" é limitação de ferramenta, não ausência de sinal.

## Pré-requisito

Chrome do operador conectado (ferramentas `mcp__claude-in-chrome__*`) e logado no LinkedIn. Se não estiver, não insistir: manter "incerto", avisar o operador e oferecer rodar depois.

## Receita

Usar `browser_batch` pra encadear navegação e leitura (bem mais rápido que uma chamada por vez).

**Passo 1. A empresa está contratando?**
Abrir `https://www.linkedin.com/company/<slug>/jobs/` e ler com `get_page_text`.
- "Não existem vagas no momento" (ou equivalente em inglês): não contrata agora. Resposta definitiva; registrar.
- "Vagas anunciadas recentemente": tem vagas, mas os títulos ficam num carrossel que não aparece no texto. Ir pro passo 2.

**Passo 2. Pegar o ID numérico da empresa.**
Na mesma página, `read_page` com filtro `interactive`: o link de "Pessoas" contém `currentCompany=%5B%22<ID>%22%5D`. Extrair o ID.

**Passo 3. Tem vaga da área? Ler os títulos reais.**
Abrir `https://www.linkedin.com/jobs/search/?keywords=<termo>&f_C=<ID>&geoId=<geoId do país>` e ler com `read_page` (filtro `interactive`). Os links são os títulos das vagas. O `<termo>` e os títulos que contam saem do critério de vaga do gabarito. `geoId` do Brasil: `106057199`; outro país, achar o `geoId` fazendo a busca uma vez pela interface.

- A busca é aproximada: casa o termo no corpo da vaga, não só no título. Ler os títulos e julgar pelo critério do gabarito. Vaga cujo título é da área conta; vaga de outra área que só cita o termo no texto (ex.: vendedor que "usa o sistema X") não conta.
- Vagas genéricas que aparecem igual em buscas de empresas diferentes são preenchimento do LinkedIn: zero vaga real daquela empresa.
- Confirmou: registrar título, URL da vaga (`https://www.linkedin.com/jobs/view/<id>/`) e a data da checagem.

**Atalho: URL de vaga já conhecida** (`linkedin.com/jobs/view/<id>/`): a página é pública e abre direto com `get_page_text`; empresa e cargo estão no `<title>` ("Cargo | Empresa | LinkedIn"). O sinal já vem confirmado de origem.

**Slug errado ou página indisponível:** buscar na web "<nome da empresa> linkedin company" pra achar o slug real. O slug nem sempre é o domínio sem ponto (ex.: `acme.com.br` pode ser `acme-commerce`).

## O que registrar no veredito

- No critério de vaga: `met` = `sim` ou `nao`, com a evidência apontada.
- Em `evidencias`: `fato` = "vaga de <título> aberta", `url` = link da vaga (ou da página de vagas da empresa, no caso "não"), `confianca` = `alta` quando o título foi lido, `data` = data da checagem.
- Em `obs`, no caso "não", o motivo: "sem nenhuma vaga aberta" ou "tem vagas, nenhuma da área". As duas leituras servem pro roteamento.

Vaga é sinal perecível: a checagem é uma foto do dia, e o critério tem `validade` no gabarito. Recomendar ao operador manter um alerta de vagas contínuo (no Apollo ou no LinkedIn) pras contas da rodada.
