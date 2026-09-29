# Adaptador: Syndie

Como a máquina usa a Syndie (automação de LinkedIn) numa rodada. A Syndie não tem API conhecida: a máquina gera os arquivos e o operador importa pela interface. Quem gera os arquivos é a skill `syndie-flow-builder`; quem confere a importação é a `qa-lancamento`.

Toda skill que prepara campanha de LinkedIn lê este arquivo antes.

## Limites da ferramenta

| Limite | Valor | Fonte e ressalva |
|---|---|---|
| Prompt da IA (`customGuidelines`) | até 1000 caracteres | Limite reportado pelo operador do cliente zero. **Ressalva:** fluxos exportados que já rodaram tinham prompts maiores que isso. Confirmar na interface na primeira importação (colar um prompt de 1001 caracteres e ver se a Syndie corta, recusa ou aceita) e registrar o resultado aqui e no `CHANGELOG.md`. Até lá, o motor trata 1000 como teto duro e `scripts/validate_syndie_flow.py` reprova acima disso. |
| Nota de convite | até 300 caracteres | Limite do próprio LinkedIn. Vale pra `message` do nó `send_invite` e pro que a IA gerar a partir do prompt. |
| Variáveis | só `{{first_name}}`, `{{last_name}}`, `{{company}}`, `{{title}}` | Coluna custom do CSV de upload não é populada nas mensagens. Qualquer outra variável sai crua ou vazia. O validador reprova. |
| Pesquisa da pessoa | não pesquisa | A IA da Syndie não busca nada sobre a pessoa nem sobre a empresa. O máximo que ela faz é referenciar **1 post recente** do perfil, quando existe (`mentionPost`). Prompt que manda "pesquisar a empresa" ou "citar a notícia recente" está morto na largada. |
| Personalização por segmento | uma campanha por grupo | Como a variável custom não chega na mensagem, segmento e oferta diferentes precisam de campanhas diferentes. Um grupo = um segmento × uma oferta = um fluxo JSON + um CSV de upload + uma campanha. |
| API | nenhuma conhecida | Importação de fluxo e de CSV só pela interface. Sem leitura de resultado por API: aceite, resposta e envio voltam por export manual ou pela triagem de respostas (S2). |
| Convites por semana | do `cliente.yaml` | `remetentes.perfil_linkedin.convites_por_semana`. O perfil é do cliente; o teto do plano de LinkedIn dele manda. |

Formato do fluxo: `schemas/syndie-flow.schema.json` (versão 3.0.0). Formato do CSV: `schemas/syndie-upload.schema.md`. Tipos de nó explicados em `skills/syndie-flow-builder/references/schema.md`; fluxos de referência anonimizados em `skills/syndie-flow-builder/references/fluxo-convite-dm.json` e `fluxo-lembrete.json`.

## Consequências pro texto

- O prompt descreve o que a mensagem precisa ser; não referencia campo de CSV (`doutrina/outbound.md`, seção de cold email, regra do prompt pra IA de ferramenta).
- Quanto menor o vão que a IA preenche, mais humano o texto (`doutrina/outbound.md`, seção LinkedIn). Preferir mensagem fixa escrita à mão com só a merge tag do nome, e deixar pra IA só o que ela consegue fazer: ler o post recente.
- Tom e tamanho: preferir o mais neutro e o mais curto que a interface oferecer.

## Arquivos que a máquina entrega por rodada

Em `clientes/<slug>/rodadas/<rodada>/`:

| Arquivo | O que é |
|---|---|
| `04-syndie-flow.json` | Fluxo no formato 3.0.0, validado. Com mais de um grupo na rodada: `04-syndie-flow-<grupo>.json`. |
| `04-syndie-upload.csv` | Leads do grupo, UTF-8 sem BOM. Com mais de um grupo: `04-syndie-upload-<grupo>.csv`. |
| `04-syndie-removidos.csv` | Quem saiu no anti-join e por quê. |
| `04-syndie-importacao.md` | Este passo a passo preenchido com os valores da rodada. |
| `04-syndie-flow-exportado.json` | O fluxo exportado da Syndie depois da importação (o operador salva). |
| `04-syndie-comparacao.md` | Comparação nó a nó entre o gerado e o exportado. |

## Antes de subir: anti-join de URLs

Ordem que já rodou em produção e vale pra toda rodada:

1. Exclusões primeiro: supressão, clientes, pipeline e quem já foi tocado estão na aba `supressao` e na aba `toques` do ledger.
2. Contatos da rodada saem da `mapear-comite` (`03-contatos.csv`).
3. **Anti-join por URL de LinkedIn** contra o snapshot fresco do ledger: `python scripts/suppress.py --lista <upload>.csv --ledger-dir <snapshot> --saida <upload>.csv --removidos 04-syndie-removidos.csv --col-dominio dominio --col-linkedin linkedin_url`. A URL precisa estar normalizada (`https://www.linkedin.com/in/<slug>`, sem barra final, sem parâmetros) dos dois lados, senão o anti-join não casa.
4. Conferir o cargo no dia e preencher `cargo_checado_em`.
5. Só então subir na Syndie.

Na Syndie, se ela avisar que um lead já está em outra campanha, tirar o lead desta campanha e anotar no `04-syndie-importacao.md`. Pessoa em duas campanhas recebe dois convites.

## Passo a passo de importação pela interface

Quem faz: o operador, logado no perfil de remetente do `cliente.yaml`. Os nomes exatos de botão mudam com versões da Syndie; quando não baterem, procurar a função equivalente e anotar o nome novo aqui.

1. **Criar a campanha.** Nome = nome da rodada (com `-<grupo>` se houver mais de um grupo). Perfil de envio = `remetentes.perfil_linkedin` do `cliente.yaml`. Não iniciar.
2. **Importar o fluxo.** No editor de fluxo da campanha, usar a opção de importar JSON e escolher `04-syndie-flow.json`. Se o fluxo usar nó `add_update_tag` com `tagId` vazio, criar a tag com o `tagName` do JSON antes e associar no nó.
3. **Conferir o fluxo na tela.** Número de nós e de arestas igual ao `metadata` do JSON; delays de cada nó; os dois ramos (sim e não) de cada condição; o texto de cada prompt e mensagem colado inteiro, sem corte no fim.
4. **Subir o CSV.** Importar `04-syndie-upload.csv` como lista de leads da campanha. Mapear `first_name`, `last_name`, `linkedin_url`, `company`, `title` pros campos nativos. As colunas de controle podem ficar como campos extras ou ser ignoradas; nunca mapear uma delas pra um campo nativo.
5. **Conferir os leads.** Total de leads na campanha = linhas do CSV (sem o cabeçalho). Abrir 3 leads e conferir nome com acento, empresa e cargo.
6. **Deixar pausada.** A campanha fica criada, com fluxo e leads, e **não é iniciada**. Iniciar só depois de "H3 aprovado" no `05-qa-lancamento.md`.
7. **Exportar o fluxo importado.** Usar a opção de exportar o fluxo da campanha e salvar como `rodadas/<rodada>/04-syndie-flow-exportado.json`. Avisar a máquina: a `syndie-flow-builder` compara nó a nó com o gerado e a `qa-lancamento` usa o resultado.
8. **Iniciar depois do H3.** Com o H3 aprovado, iniciar a campanha e anotar data e hora no `05-qa-lancamento.md` (bloco "Lançamento"). A `registrar-ledger` usa essa data pros toques.

Se a importação de JSON falhar (arquivo recusado, nó faltando), não montar o fluxo à mão por cima: mandar o erro pra `syndie-flow-builder`, corrigir o JSON, apagar o fluxo parcial e importar de novo.

## Opção: importação pelo navegador com Claude in Chrome

**Não testado.** Registrar aqui o resultado da primeira tentativa.

A mesma sequência acima pode ser feita pelo Claude in Chrome, com o operador logado na Syndie no próprio navegador:

1. O operador abre a Syndie, faz login e resolve 2FA ou captcha. A máquina não digita senha.
2. A máquina carrega as ferramentas do Chrome, lê a página, cria a campanha, importa o JSON e o CSV com a ferramenta de upload de arquivo e confere a contagem na tela.
3. A máquina exporta o fluxo e salva o arquivo na rodada.
4. **A máquina nunca clica em iniciar, ativar ou retomar campanha.** O passo 8 é sempre do operador, depois do H3.
5. Se a tela não bater com o passo a passo (botão diferente, modal inesperado), parar e devolver pro operador em vez de improvisar.

## Pendências a confirmar

- Limite real do `customGuidelines` (ver ressalva na tabela de limites).
- O que exatamente vai no contexto da IA quando `mentionPost` está ligado: o corpo do post ou só o tema. Se for só o tema, prompt que pede "o detalhe concreto do post" não tem como ser cumprido.
- Se a Syndie preserva os `id` dos nós na importação ou gera novos. A comparação da `syndie-flow-builder` não depende de id, mas o relatório fica mais simples se preservar.
- Se existe export de leads com status (convite enviado, aceito, respondeu) que sirva de fonte pros toques no ledger.
