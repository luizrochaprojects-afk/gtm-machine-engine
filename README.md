# GTM Machine

English · [Português](README.pt-BR.md)

GTM Machine is an outbound system operated with Claude Code. It takes a company from its ideal customer profile (ICP) to a booked meeting: it builds the account list, qualifies each account, finds contacts, writes the email and LinkedIn copy, and launches the sequences. People approve the work at four gates, H0 to H3. Nothing is sent until the H3 launch gate is approved in writing.

<!-- TODO: screenshot -->
![GTM Machine round, stage by stage](docs/round.png)

## How it works

- This repository is the **engine**: doctrine, skills, schemas, templates, adapters and scripts that apply to any company. Each client gets a **workspace** in `clientes/<slug>/`, a separate private repository that the engine's git ignores.
- Skills never know who the client is. They read the ICP, offers, voice, stack and suppression list from the active workspace.
- Work runs in rounds. Each skill writes numbered files to `clientes/<slug>/rodadas/<round>/`. A Google Sheets ledger is the machine's memory; Apollo and Syndie do the sending.
- A copy judge checks every sequence against the doctrine and can veto it. A pre-send QA renders the emails, reruns suppression and duplicate checks, and checks the sending domains and limits.
- Every gate saves the machine's version and the approved version as a diff. The lessons loop turns those diffs into rules, in the client workspace or in the engine doctrine.

## Stages and skills

| Stage | Skills in v0.1 | Gate |
|---|---|---|
| Setup, once per client | `setup-workspace` | |
| E0 Strategy and ICP | `voz-do-cliente`, plus manual writing | H0 |
| E1 Total addressable market | `montar-tam` | |
| E2 Qualification | `validar-lista`, `detectar-tecnografia` | H1 |
| E3 Buying committee | `mapear-comite` | |
| E5 Messaging | `copy-email`, `juiz-de-copy` | H2 |
| E6 Build and launch | `apollo-sequence-builder`, `syndie-flow-builder`, `qa-lancamento`, `registrar-ledger` | H3 |
| E9 Learning | `loop-de-licoes` (run by hand) | |

E4 (signals and timing), E7 (replies) and E8 (meeting and sale) have no skill in v0.1 and are done by hand.

## Status

Version 0.1. No skill has run in a live round yet. The first live round is the validation, and the `CHANGELOG.md` will record what it changes.

## Running it

1. Open Claude Code at the repository root.
2. Run the `setup-workspace` skill with a client slug, for example `acme`. It copies `templates/workspace/` to `clientes/<slug>/`, creates the ledger in Google Sheets, asks for the `cliente.yaml` fields and tests the connections to Apollo, Google Sheets, Syndie, Gmail and the CRM.
3. Run `git init` inside `clientes/<slug>/`. Add the client's company, people and account names to `scripts/termos-clientes.txt`.
4. Run the stages in the order of the table, approving each gate. Close the round with `loop-de-licoes`.

Checks:

```bash
python -m pytest scripts/          # script tests
python scripts/check_sanitize.py   # no client term anywhere in the repository
```

`scripts/termos-clientes.txt` is the list of client names that must never appear in the engine. It is git-ignored and not included here. Create it locally with one term per line. Without it, the check exits with code 2.

## Language

The skills, doctrine, schemas and templates are written in Brazilian Portuguese. File and folder names are in Portuguese too: `clientes` is clients, `rodadas` is rounds, `doutrina` is doctrine.
