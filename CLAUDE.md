# CLAUDE.md · motor da GTM Machine

Regras que valem em toda sessão neste repositório. O `CLAUDE.md` de cada workspace (`clientes/<slug>/CLAUDE.md`) acrescenta as regras daquele cliente e declara a versão do motor que usa.

## Três regras

1. **Skill não sabe quem é o cliente.** Toda skill lê ICP, oferta, voz, stack, personas, tecnografia alvo e supressão do workspace ativo (`cliente.yaml`, `estrategia/`, `doutrina-cliente.md`, ledger). Nome de cliente, conta, pessoa, perfil de remetente, número autorizado ou preço nunca entram numa `SKILL.md`, num schema, num template ou na doutrina do motor. Exemplo em arquivo do motor usa empresa fictícia.
2. **Toda lição nasce marcada cliente ou ofício.** Cliente = mercado, marca, número autorizado, preferência do aprovador → vai pra `doutrina-cliente.md` do workspace. Ofício = como escrever, qualificar, operar → vai pra `doutrina/` do motor só depois de anonimizada, e só quando aparecer em 2 clientes ou por decisão do mantenedor (ver `doutrina/_protocolo.md`).
3. **Nada é enviado sem gate H3.** Nenhuma mensagem sai, nenhum contato é inscrito em sequência e nenhuma campanha é ativada sem "H3 aprovado" escrito no `05-qa-lancamento.md` da rodada, com data e responsável.

## Antes de trabalhar

- **Ler `doutrina/` antes de qualquer copy ou lista.** Copy: `doutrina/outbound.md`, `doutrina/escrita.md`, `doutrina/ai-tells.md` e a `doutrina-cliente.md` do workspace. Lista: `doutrina/outbound.md` (seção de sinais e listas) e `doutrina/producao-com-agentes.md`.
- Descobrir o workspace ativo: a pasta `clientes/<slug>/` em que se está trabalhando. Se não estiver claro, perguntar.
- Ler `doutrina/_protocolo.md` antes de gravar qualquer lição.

## Regras duras de operação

- Nenhuma automação reenvia mensagem a quem recebeu e não respondeu.
- Nenhum crédito de enrich (Apollo) é gasto antes de mostrar a estimativa e ter o lote aprovado.
- No ledger, a máquina lê a linha antes de escrever e só escreve nas colunas de cabeçalho cinza. Regras em `adapters/google-sheets/README.md`.
- Todo gate (H0 a H3) salva o diff em `aprendizado/diffs/` do workspace.

## Gates

| Gate | O que se aprova | Onde fica o registro |
|---|---|---|
| H0 | Estratégia: gabarito, oferta, master copy, o que não pode ser dito | `aprendizado/diffs/<rodada>-H0-estrategia.md` |
| H1 | Lista: vereditos das contas incertas e P0 | `aprendizado/diffs/<rodada>-H1-lista.md` |
| H2 | Copy: email e prompt da Syndie | `aprendizado/diffs/<rodada>-H2-<peça>.md` |
| H3 | Lançamento: go/no-go | `rodadas/<rodada>/05-qa-lancamento.md` + diff |

C1, C2 e C3 são os gates do cliente no serviço (ver `playbooks/onboarding.md`).

## Manutenção do motor

- Mudança no motor entra no `CHANGELOG.md` com versão, data, mudança e origem.
- No fim de cada bloco de trabalho: `python -m pytest scripts/` e `python scripts/check_sanitize.py`. Os dois precisam passar.
- Material de origem de clientes (workspaces antigos, planilhas, doutrina própria deles) é matéria-prima: ler e reescrever, nunca copiar arquivo inteiro. De CSV, só nome de coluna.
- Sessão na nuvem não roda git na pasta do computador. Commits são feitos pelo operador.
