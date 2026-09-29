# GTM Machine

[English](README.md) · Português

Sistema de outbound operado com Claude Code, do ICP à reunião marcada. Montado uma vez (o **motor**) e aplicado a cada cliente por um **workspace** próprio.

Versão atual: ver `CHANGELOG.md`.

## Motor × workspace

O repositório tem duas coisas que nunca se misturam.

| | Motor (este repositório) | Workspace (`clientes/<slug>/`) |
|---|---|---|
| O que é | O que vale pra qualquer empresa | O que só vale pra um cliente |
| Contém | `doutrina/` de ofício, `skills/`, `schemas/`, `templates/`, `adapters/`, `playbooks/`, `scripts/` | `cliente.yaml`, contexto, estratégia, `doutrina-cliente.md`, segmentos, rodadas, aprendizado |
| Git | Este repositório | Um repositório privado por cliente, ignorado pelo git do motor |
| Quem muda | O mantenedor do motor, com entrada no `CHANGELOG.md` | O operador, nas rodadas e nos gates |

Duas regras seguram a fronteira:

1. **O motor nunca guarda fato de cliente.** Nome de conta, pessoa, número autorizado, preço ou ID não entram em nenhum arquivo do motor. `python scripts/check_sanitize.py` falha se aparecer.
2. **O workspace nunca reescreve uma skill.** Toda skill lê cliente, ofertas, ICP, voz, stack e supressão do workspace ativo. O que muda por cliente mora no workspace.

## Criar o workspace de um cliente

1. Abrir o Claude Code na raiz deste repositório.
2. Rodar a skill `setup-workspace` com o slug do cliente (ex.: `acme`). Ela:
   - copia `templates/workspace/` pra `clientes/<slug>/`;
   - cria o ledger em Google Sheets a partir de `schemas/ledger.schema.md`;
   - pergunta os campos do `cliente.yaml` (formato em `schemas/cliente.schema.yaml`), um bloco por vez;
   - gera o checklist de acesso do cliente a partir de `playbooks/checklist-acesso.md`;
   - testa Apollo, Google Sheets, Syndie, Gmail e CRM, e grava `setup.md` com o que está ok e o que falta.
3. Rodar `git init` em `clientes/<slug>/` (repositório privado do cliente).
4. Acrescentar os nomes do cliente, das pessoas e das contas dele em `scripts/termos-clientes.txt`.

## O loop: etapas E0 a E9

| Etapa | O que faz | Skill na v0.1 | Gate humano |
|---|---|---|---|
| E0 Estratégia e ICP | Gabarito, oferta, master copy | `voz-do-cliente` + escrita manual | H0 |
| E1 TAM | Busca, lookalike, normaliza, deduplica, suprime | `montar-tam` | |
| E2 Qualificação | Veredito por conta com evidência, adversarial, trilha | `validar-lista`, `detectar-tecnografia` | H1 |
| E3 Comitê e contatos | Até 3 contatos por conta, crédito aprovado antes | `mapear-comite` | |
| E4 Sinais e timing | Sinais datados viram evento | (semana 2) | |
| E5 Mensagem | Email de 4 toques e prompt da Syndie, com juiz | `copy-email`, `juiz-de-copy` | H2 |
| E6 Montagem e lançamento | Apollo, Syndie, QA, registro no ledger | `apollo-sequence-builder`, `syndie-flow-builder`, `qa-lancamento`, `registrar-ledger` | H3 |
| E7 Respostas | Triagem de reply e rascunho | (semana 2) | H4 |
| E8 Reunião e venda | Brief, ficha de qualificação | (semana 2) | H5 |
| E9 Medição e aprendizado | Diffs viram lições; funil por rodada | `loop-de-licoes` (manual) | |

`setup-workspace` roda antes de tudo, uma vez por cliente.

## Rodar uma rodada

Nome da rodada: `AAAA-MM-DD-rN-<segmento>-<oferta>`. Arquivos numerados na ordem do fluxo, em `clientes/<slug>/rodadas/<rodada>/`:

```
_snapshot/<data-hora>/          foto do ledger usada pela supressão (uma por execução)
01-lista-crua.csv               montar-tam
02-tecnografia.csv              detectar-tecnografia (quando roda sozinha)
02-validacao.json               validar-lista: um veredito por conta
02-validacao.xlsx               validar-lista: auditoria + resumo   → gate H1
03-contatos.csv                 mapear-comite
03-sem-contato.csv              mapear-comite: contas sem contato achado
03-creditos.md                  mapear-comite: créditos estimados e gastos
04-sequencia-email.md           copy-email + juiz                   → gate H2
04-juiz-email.md                juiz-de-copy: relatório da sequência
04-juiz-syndie.md               juiz-de-copy: relatório do prompt da Syndie
04-render-amostra.md            render de 3 contatos antes do H2
04-apollo-import-contas.csv     apollo-sequence-builder
04-apollo-import.csv            apollo-sequence-builder (contatos)
04-apollo-ids.json              apollo-sequence-builder: IDs criados no Apollo
04-syndie-flow.json             syndie-flow-builder
04-syndie-upload.csv            syndie-flow-builder
05-qa-lancamento.md             qa-lancamento                       → gate H3
06-registro-ledger.md           registrar-ledger
ledger/                         snapshot CSV das abas no fim da rodada
```

Todo gate salva o par versão da máquina × versão aprovada em `aprendizado/diffs/<rodada>-<gate>-<peça>.md` (modelo em `schemas/diff.template.md`). O `loop-de-licoes` lê esses diffs no fim da rodada.

## Regras fixas

- Nada é enviado sem o gate H3 aprovado por escrito no `05-qa-lancamento.md`.
- Nenhuma automação reenvia mensagem a quem recebeu e não respondeu.
- Nenhum crédito de enrich é gasto antes da aprovação do lote.
- O ledger em Google Sheets é a memória da máquina. Apollo e Syndie executam; o CRM do cliente recebe cópia pelo adaptador.

## Verificações

```bash
python -m pytest scripts/          # testes dos scripts
python scripts/check_sanitize.py   # nenhum termo de cliente no repositório
```

`scripts/termos-clientes.txt` é dado de cliente e fica fora do git: não vem com o repositório, cada operador cria o seu, um termo por linha. Sem ele, o check sai com código 2. O check varre todo arquivo que o git versionaria e mostra o número do termo, nunca o termo.
