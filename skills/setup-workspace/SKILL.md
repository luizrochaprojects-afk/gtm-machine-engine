---
name: setup-workspace
description: "Cria o workspace de um cliente novo da GTM Machine: copia o template para clientes/<slug>/, cria o ledger em Google Sheets, preenche o cliente.yaml perguntando um bloco por vez, importa a supressão, gera o checklist de acesso do cliente e testa Apollo, Google Sheets, Syndie, Gmail e CRM, gravando setup.md com o que está ok e o que falta. Use sempre que o operador disser que vai começar um cliente novo, pedir para montar, criar ou configurar o workspace, o ledger ou o cliente.yaml, ou quiser conferir se as conexões de um cliente estão prontas antes de uma rodada (ex.: 'começa o cliente acme', 'monta o workspace', 'cria o ledger', 'testa as conexões do cliente')."
---

# Setup do workspace

Monta, uma vez por cliente, tudo que as outras skills leem: a pasta `clientes/<slug>/`, o `cliente.yaml`, o ledger e o relatório de conexões. Roda antes de qualquer rodada. Também serve para retomar um setup que parou no meio ou para testar as conexões de novo.

Esta skill não sabe nada do cliente. Tudo vem das respostas do operador.

## Entradas

- **slug** do cliente: minúsculas, sem acento, hífen no lugar de espaço (ex.: `acme`). Se o operador não deu, perguntar.
- **nome** do cliente como aparece nos documentos (ex.: `Acme Commerce`).
- Respostas do operador para cada bloco do `cliente.yaml`.
- Arquivos de supressão que o operador tiver (CSV), copiados para `clientes/<slug>/supressao/`.

## Ler antes

1. `CLAUDE.md` do motor.
2. `schemas/cliente.schema.yaml`: campos, obrigatórios e valores aceitos.
3. `schemas/ledger.schema.md`: abas, colunas, cores e fórmulas.
4. `adapters/google-sheets/README.md`: como criar a planilha e como escrever nela.
5. `CHANGELOG.md`: a versão do motor é o título da entrada mais recente (`## v<x.y.z> · ...`).
6. `playbooks/checklist-acesso.md`, só no passo 7.

## Workflow

### 1. Conferir o destino

1. Validar o slug. Se tiver maiúscula, acento ou espaço, propor a versão corrigida e confirmar.
2. Se `clientes/<slug>/` não existe, seguir.
3. Se existe, listar o que já está lá (`cliente.yaml` preenchido? `ledger_id`? `setup.md`?) e perguntar ao operador:
   - **completar:** copiar só o que falta do template e retomar do primeiro passo pendente;
   - **testar conexões:** pular para o passo 8;
   - **parar.**

   Nunca sobrescrever arquivo existente, nem com a versão do template.

### 2. Copiar o template

1. Copiar `templates/workspace/` para `clientes/<slug>/` sem sobrescrever (`cp -rn templates/workspace/. clientes/<slug>/`). Conferir que `.gitignore` e os `.gitkeep` vieram.
2. Ler a versão do motor no `CHANGELOG.md`.
3. No `clientes/<slug>/CLAUDE.md`, trocar `<nome do cliente>`, `<x.y.z>` e `<AAAA-MM-DD>` (data de hoje). Não mexer no resto.

### 3. Bloco identidade

Perguntar `nome` (se ainda não veio) e `crm` (`account-guardian`, `hubspot` ou `nenhum`). `slug` e `versao_motor` a skill já tem. Gravar esses campos no `cliente.yaml` antes de seguir.

Se o operador disser `hubspot`, avisar: o adaptador do HubSpot está fora da v0.1. O campo fica gravado, mas a `registrar-ledger` só vai gerar CSV e o teste do passo 8 marca "falta". Perguntar se prefere `nenhum` por enquanto.

### 4. Criar o ledger

Seguir a seção "Criar a planilha do zero" de `adapters/google-sheets/README.md`, na ordem:

1. `mcp__claude_ai_Google_Drive__create_file` com título `GTM Machine · Ledger · <nome>`.
2. Localidade `pt_BR` e fuso (`America/Sao_Paulo` se ainda não houver `janela_envio.fuso`).
3. As 7 abas na ordem `leia-me`, `contas`, `contatos`, `toques`, `supressao`, `reunioes`, `rodadas`.
4. Cabeçalhos do schema, cinza nas colunas da máquina e amarelo nas humanas, negrito, primeira linha congelada, K da aba `rodadas` em %.
5. Texto da `leia-me`.
6. Conferir abas, ordem, cabeçalhos e localidade.
7. Perguntar ao operador com quem compartilhar (operador e aprovador) e usar `mcp__claude_ai_Google_Drive__share_file` só com esses emails.

Gravar o ID em `ledger_id` no `cliente.yaml` assim que a planilha existir, antes de formatar: se algo falhar no meio, o setup retoma pela planilha certa.

A aba `rodadas` nasce só com o cabeçalho. A linha de cada rodada, com as fórmulas, é criada pela `registrar-ledger` ou pelo operador ao abrir a rodada.

Se o operador já tiver um ledger criado para esse cliente, pedir o link, ler as abas e os cabeçalhos, comparar com o schema e só completar o que falta. Não recriar.

### 5. Preencher o cliente.yaml, um bloco por vez

Um bloco por mensagem. Em cada bloco: dizer o que o bloco é em uma frase, mostrar o exemplo fictício do schema, fazer as perguntas, validar as respostas contra o schema, mostrar o trecho de YAML que vai ser gravado e gravar. Gravar bloco a bloco, não no fim: se a conversa cair, o que foi respondido está salvo.

1. **Ofertas.** Para cada oferta: `id`, `nome`, `porta_de_entrada`, `segmento[]`. `arquivo` e `master_copy` ficam com o caminho padrão (`estrategia/ofertas/<id>.md`, `estrategia/master-copy/<id>.md`) mesmo que o arquivo ainda não exista. Recusar `id` de H0 a H5 e de C1 a C3 (colidem com os gates) e propor outro. Criar `segmentos/<slug-do-segmento>/` para cada segmento citado.
2. **Stack.** `sequenciador_email` (`apollo` ou `nenhum`), `linkedin` (`syndie`, `manual` ou `nenhum`), `fonte_contexto[]`. `stack.crm` recebe o mesmo valor do `crm` da raiz, sem perguntar de novo.
3. **Remetentes.** Perfil de LinkedIn (nome, URL, ferramenta, convites por semana), caixas de email (email, limite diário, início do aquecimento, data em que ficou aquecida, assinatura), janela de envio (dias, início, fim, fuso). Limite diário acima de 30 é recusado: o teto do motor é 30. Caixa sem `aquecida_em` fica registrada, mas avisar que ela não entra em rodada. Perguntar também a cadência; se o operador não tiver preferência, gravar o padrão `[D1, D4, D8, D13]`.
4. **Gates.** Primeiro as pessoas (`gates.pessoas`: papel → nome e email), depois o dono de cada gate H0 a H3 e C1 a C3 por papel. Todo papel citado num gate tem que existir em `pessoas`.
5. **Supressão.** Perguntar quais arquivos o cliente mandou (clientes ativos, pipeline, optout, negativação, concorrentes, parceiros). Pedir que o operador copie os arquivos para `supressao/` e gravar os caminhos relativos. Lista vazia é aceita, mas avisar que a primeira rodada vai suprimir só pelo histórico do ledger.
6. **Tecnografia alvo.** Ferramentas que a `detectar-tecnografia` vai procurar: nome, categoria, sinais no HTML (se o operador souber) e leitura (`fit`, `troca` ou `concorrente`). Campo opcional: aceitar lista vazia.
7. **Personas.** Por faixa de porte (formato do Apollo, ex.: `51-200`): cargos, papel (`decisor`, `champion` ou `influenciador`), máximo por conta.

No fim, ler o `cliente.yaml` inteiro, conferir que todo campo obrigatório do schema está preenchido e que o YAML abre sem erro (`python -c "import yaml; yaml.safe_load(open('clientes/<slug>/cliente.yaml', encoding='utf-8'))"`). Campo obrigatório vazio vai para a lista de pendências do `setup.md`.

### 6. Importar a supressão para o ledger

Roda uma vez por arquivo. Depois do import, a supressão lê só o ledger.

1. Ler a aba `supressao` do ledger (`get_values` em `supressao!A:E`). Se já existem linhas com `origem` igual ao nome do arquivo, esse arquivo já foi importado: pular e dizer.
2. Para cada arquivo em `supressao`: ler só o cabeçalho e as 3 primeiras linhas, mostrar ao operador e perguntar:
   - qual coluna é a chave e de que tipo (`dominio`, `email` ou `linkedin`);
   - qual o motivo, da lista fechada do schema (`cliente`, `pipeline`, `abordado_sem_resposta`, `optout`, `negativacao`, `concorrente`, `parceiro`).
3. Normalizar cada chave:
   - domínio com `scripts/normalize_domain.py` (sem `http`, `www`, caminho e barra final; caixa baixa). Se a coluna tem email em vez de domínio e o tipo é `dominio`, usar a parte depois do `@`;
   - email em caixa baixa, sem espaço;
   - LinkedIn como `https://www.linkedin.com/in/<perfil>`, sem parâmetros e sem barra final.
4. Descartar linha sem chave e chave repetida (dentro do arquivo e contra o que já está na aba).
5. Montar as linhas com as colunas cinza: `'<chave>`, `tipo`, `motivo`, `origem` (nome do arquivo), `'<data de hoje>`. Colunas `adicionado_por` e `nota` ficam em branco: são humanas.
6. `append_values` em `supressao!A1`, até 500 linhas por chamada.
7. Reler a aba e conferir o total. Anotar por arquivo: linhas lidas, importadas, descartadas sem chave, descartadas repetidas.

### 7. Checklist de acesso do cliente

1. Ler `playbooks/checklist-acesso.md`. Se não existir, pular este passo e marcar no `setup.md` como pendência do motor.
2. Perguntar a data do D0 (kickoff). Sem resposta, usar hoje.
3. Preencher para este cliente: nome, prazo de cada item em data (D0 + dias do playbook), responsável do lado do cliente (de `gates.pessoas`).
4. Tirar o que não se aplica pela stack: sem LinkedIn, sai o acesso à Syndie e ao perfil; `crm: nenhum`, sai o acesso ao CRM; `sequenciador_email: nenhum`, saem domínios e caixas.
5. Marcar como já feito o que o setup confirmou (ex.: arquivos de supressão recebidos).
6. Gravar em `entregas/checklist-acesso.md`. Essa pasta sai para o cliente: nada de ID do ledger, nota interna ou dado de outro cliente.

### 8. Testar as conexões

Cada teste é uma chamada leve que não gasta crédito nem escreve nada. Status possíveis: `ok`, `falta` (conexão não configurada ou dado que o cliente ainda não mandou) e `erro` (configurada, mas falhou).

| Conexão | Quando testar | Como testar | ok quando |
|---|---|---|---|
| Apollo | `sequenciador_email: apollo` ou sempre que a rodada for usar busca | `mcp__claude_ai_Apollo_io__apollo_users_api_profile` com `include_credit_usage: true` | devolve nome e email do usuário; anotar o saldo de crédito |
| Google Sheets | sempre | `mcp__claude_ai_Google_Sheets__get_values` em `leia-me!A1:B2` do `ledger_id` | devolve o título do ledger |
| Syndie | `linkedin: syndie` | não há API. Perguntar ao operador se entra na Syndie com o perfil do `remetentes.perfil_linkedin` e procurar um export de fluxo (`.json`) em `contexto/fontes/` | operador confirma o acesso; o export é bônus, não condição |
| Gmail | sempre | `mcp__claude_ai_Gmail__search_threads` com `query: "newer_than:1d"` e `pageSize: 1` | responde (lista vazia também é ok); anotar de qual conta é |
| CRM | conforme `crm` | `account-guardian`: `mcp__guardian__guardian_whoami`. `hubspot`: não testar. `nenhum`: não testar | `account-guardian`: devolve usuário e organização. `hubspot`: `falta` (adaptador fora da v0.1). `nenhum`: `ok` (o ledger é o único registro) |
| Granola | `fonte_contexto` inclui `granola` | `mcp__claude_ai_Granola__get_account_info` | devolve o email da conta; anotar se é de uma das pessoas do `cliente.yaml` |

Não usar `apollo_mixed_companies_search` nem nenhuma ferramenta de enrich no teste: o perfil basta para saber se a conexão está de pé.

Se uma ferramenta não aparece na sessão, o status é `falta` e o que fazer é "conectar o conector <nome> no Claude e abrir sessão nova". Se aparece e dá erro de autenticação, o status é `erro` e o que fazer é reconectar. No Account Guardian, sessão expirada se resolve com `mcp__guardian__guardian_login`.

### 9. Gravar setup.md

Gravar `clientes/<slug>/setup.md` com:

```markdown
# Setup: <nome do cliente>

Data: <AAAA-MM-DD> · motor <x.y.z> · operador: <nome>
Ledger: <URL da planilha>

## Conexões

| Conexão | Status | Detalhe | O que fazer |
|---|---|---|---|
| Apollo | ok | <usuário>, <saldo de crédito> | nada |
| Google Sheets | ok | ledger lido | nada |
| Syndie | falta | operador ainda sem acesso ao perfil | cliente libera acesso (item do checklist) |
| Gmail | ok | conta <email> | nada |
| CRM | ok | crm: nenhum | nada |

## Supressão importada

| Arquivo | Motivo | Lidas | Importadas | Sem chave | Repetidas |
|---|---|---|---|---|---|

## Pendências do cliente.yaml

- <campo obrigatório vazio e quem responde>

## Pendências do cliente

- <item do checklist de acesso ainda aberto, com prazo>

## Próximos passos

- [ ] `git init` em `clientes/<slug>/` (operador)
- [ ] Acrescentar os termos do cliente em `scripts/termos-clientes.txt`
- [ ] <primeira tarefa da estratégia>
```

Rodar o passo 8 de novo só atualiza a tabela de conexões e a data; o resto do arquivo fica.

### 10. Fechar com o operador

1. **Git.** Não rodar git. Lembrar o operador de rodar `git init` dentro de `clientes/<slug>/`: o workspace é um repositório privado próprio, fora do git do motor.
2. **Termos proibidos no motor.** Montar a lista sugerida para `scripts/termos-clientes.txt`: nome do cliente e variações, nomes das pessoas de `gates.pessoas`, domínios do cliente e dos remetentes, `ledger_id`. Mostrar e perguntar "acrescento esses termos?". Só escrever com sim. Avisar quando um termo é palavra comum (ex.: um slug que é palavra do dicionário), porque vai gerar falso alarme.
3. Rodar `python scripts/check_sanitize.py` na raiz do motor e confirmar que nada do cliente vazou para fora de `clientes/`.
4. Resumir em poucas linhas: o que ficou pronto, o que está `falta` ou `erro` e o que o operador precisa fazer.

## Entregar

- `clientes/<slug>/` com a estrutura do template.
- `clientes/<slug>/CLAUDE.md` com nome, data e versão do motor.
- `clientes/<slug>/cliente.yaml` preenchido e válido contra o schema.
- Ledger em Google Sheets com as 7 abas, cabeçalhos, cores e `leia-me`; ID no `cliente.yaml`.
- Aba `supressao` com o import inicial.
- `clientes/<slug>/entregas/checklist-acesso.md`.
- `clientes/<slug>/setup.md` com a tabela de conexões.

## Armadilhas

- **Sobrescrever um workspace existente.** `cp` sem `-n` apaga o trabalho do operador. Sempre copiar sem sobrescrever e perguntar antes.
- **Fato de cliente no motor.** Tudo que o operador responde vai para `clientes/<slug>/`. Nada volta para `skills/`, `schemas/`, `templates/` ou `doutrina/`, nem como exemplo.
- **Perguntar tudo de uma vez.** Um bloco por mensagem. Formulário gigante vira resposta pela metade.
- **Ledger em inglês.** Planilha criada sem ajustar a localidade fica `en_US` e as fórmulas com `;` quebram. Ajustar para `pt_BR` no passo 4.
- **Compartilhar o ledger por link aberto.** Tem dado pessoal de contato. Só emails nomeados.
- **Gastar crédito no teste.** O teste do Apollo é o perfil do usuário, não uma busca nem um enrich.
- **Import de supressão repetido.** Conferir a coluna `origem` antes; o mesmo arquivo importado duas vezes duplica a aba.
- **CRM `nenhum` não é erro.** O setup e as rodadas funcionam só com o ledger. Não travar nem insistir.
- **Id de oferta com nome de gate** (`H1`, `C2`) confunde diffs e relatórios. Recusar no bloco de ofertas.
- **Checklist com dado interno.** `entregas/` vai para o cliente. ID do ledger, saldo de crédito e notas do operador ficam no `setup.md`, não no checklist.
