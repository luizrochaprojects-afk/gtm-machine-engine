# Playbook: onboarding D0 a D15

Como um cliente novo sai do kickoff e chega à campanha no LinkedIn em 10 dias e ao email em 15. Vale pra qualquer cliente; o que é específico de cada um fica no workspace dele (`clientes/<slug>/`).

O caminho crítico é o email. Caixa nova precisa de 14 dias de aquecimento antes do primeiro envio, então domínio e caixas são comprados no D0. Cada dia de atraso na compra empurra o email um dia. O LinkedIn não depende disso e entra no ar antes.

## Legenda

- **Skill v0.1**: existe no motor e roda por comando.
- **Manual na v0.1**: a skill está prevista pro primeiro cliente externo (C1) e ainda não existe. O operador faz à mão, seguindo o que está descrito aqui, e o que ele fizer vira a base da skill.
- **Semana 2**: skill prevista pra depois do primeiro lote no ar. Até lá, também é manual.

Gates internos (H0 a H3) estão no `CLAUDE.md` do motor. Os gates do cliente (C1, C2, C3) estão na seção [Gates do cliente](#gates-do-cliente).

## Visão das fases

| Fase | Dias | O que acontece | Cliente recebe | Gate |
|---|---|---|---|---|
| Kickoff | D0 | Acessos, compra de domínio e caixas, início do aquecimento | Checklist de acesso com prazos | |
| Intake | D1 a D3 | Inventário das fontes e mapa de cobertura | Nada ainda | |
| Workshop | D4 | 2 a 3 horas com quem vende e quem decide | Pauta antes da reunião | |
| Estratégia | D5 a D7 | Hipóteses de ICP, TAM, oferta, master copy | Estratégia pra aprovar | C1 |
| Rodada 1 | D8 a D10 | Lista, comitê, copy, fluxo da Syndie, QA. LinkedIn no ar | Copy pra aprovar | C2 |
| Operação | D15 em diante | Email no ar, relatório semanal, revisão mensal | Relatório toda semana | C3 |

## D0 · Kickoff

**Objetivo.** Sair do dia com o workspace criado, o checklist enviado e o aquecimento das caixas começado.

**O que a gente faz.**

1. Roda a `setup-workspace` (skill v0.1) com o slug do cliente: cria `clientes/<slug>/` a partir do template, cria o ledger em Google Sheets, preenche o `cliente.yaml` com o que já se sabe e gera `entregas/checklist-acesso.md` a partir de `playbooks/checklist-acesso.md`.
2. Na reunião de kickoff, percorre o checklist item por item com o cliente e acerta quem providencia cada um e até quando.
3. Compra os domínios secundários e cria as caixas de email (ou recebe a autorização e a verba pra comprar), configura SPF, DKIM e DMARC e liga o aquecimento no mesmo dia. Registra `aquecimento_inicio` de cada caixa no `cliente.yaml`.
4. Agenda o workshop do D4 com quem vende e quem decide.
5. Acrescenta o nome do cliente, das pessoas e das contas dele em `scripts/termos-clientes.txt`.

**O que o cliente recebe.** O checklist de acesso com prazo e responsável por item, e o convite do workshop.

**O que o cliente precisa fazer.** Dar os acessos marcados D0 no checklist: perfil de LinkedIn do remetente e acesso à Syndie, autorização pra comprar domínio e caixas, contato de quem aprova.

**Critério de saída.** Caixas compradas e aquecendo, com a data registrada. Workspace e ledger criados. `setup.md` do workspace lista o que está conectado e o que falta. Workshop agendado.

## D1 a D3 · Intake e mapa de cobertura

**Objetivo.** Saber o que as fontes do cliente já respondem sobre o mercado dele antes de gastar hora de reunião.

**O que a gente faz.**

1. Inventaria as fontes que existirem. Varia por cliente: gravações de reunião, PDF de entrevista, export de CRM, deck, propostas, site, ou só o site.
2. Se o cliente usa Granola, roda a `voz-do-cliente` (skill v0.1): extrai dor, objeções e motivos de não-decisão com citação literal e origem, e grava em `contexto/extracoes/`.
3. Pras outras fontes, faz o intake à mão (a skill `intake-contexto` é C1, fora da v0.1): lê cada fonte e anota o que ela diz sobre cada campo que a estratégia precisa.
4. Se houver export de CRM, olha clientes ganhos, perdidos e oportunidades abertas à mão (a `analise-crm` é C1). Serve pra achar as contas âncora do lookalike e pra montar a supressão.
5. Monta o mapa de cobertura em `contexto/`: pra cada campo da estratégia (ICP, dor, prova, objeções, personas, concorrentes, o que não pode ser dito), o que se sabe, de que fonte, com que confiança e o que falta.

**O que o cliente recebe.** Nada ainda. O trabalho é interno.

**O que o cliente precisa fazer.** Entregar os itens do checklist com prazo D1 e D3: exports, materiais de vendas, gravações, lista de quem nunca abordar.

**Critério de saída.** Mapa de cobertura com cada campo marcado como coberto, parcial ou lacuna. As lacunas viram a pauta do workshop.

## D4 · Workshop

**Objetivo.** Fechar em 2 a 3 horas só o que as fontes não responderam.

**O que a gente faz.**

1. Escreve a pauta a partir das lacunas do mapa, na ordem do que mais trava a estratégia (a `roteiro-workshop` é C1; na v0.1 a pauta é feita à mão). Envia ao cliente pelo menos um dia antes.
2. Conduz o workshop com quem vende e quem decide. Grava, com autorização.
3. Converte a transcrição nos arquivos de estratégia do workspace, separando o que o cliente decidiu do que é inferência nossa (a `sintese-workshop` é C1; na v0.1 é manual). Inferência entra marcada como `[hipótese]`.

**O que o cliente recebe.** A pauta antes da reunião.

**O que o cliente precisa fazer.** Levar ao workshop quem vende e quem decide. Trazer por escrito os números e claims que podem ser usados na copy, ou marcar quando vão chegar.

**Critério de saída.** Nenhuma lacuna da pauta sem resposta ou sem dono. Decisões do cliente e hipóteses nossas separadas nos arquivos de estratégia.

## D5 a D7 · Estratégia

**Objetivo.** Ter a estratégia da primeira rodada aprovada pelo cliente no gate C1.

**O que a gente faz.**

1. Escreve de 2 a 5 hipóteses de ICP, priorizadas, cada uma com racional e critério de teste (a `hipoteses-icp` como skill é C1; na v0.1 é escrita à mão).
2. Escreve o gabarito de ICP da hipótese principal: critérios de fit, sinais de prontidão, critérios de discovery e desqualificadores.
3. Roda a `montar-tam` (skill v0.1) só pra medir o tamanho do TAM por hipótese, com a data do levantamento. Ainda não gasta crédito de enrich.
4. Escreve a oferta de entrada e o master copy por segmento, a partir das extrações e da doutrina. Registra na `doutrina-cliente.md` o que não pode ser dito e os números autorizados.
5. Passa pelo gate interno H0 e depois leva ao cliente pro C1.

**O que o cliente recebe.** Hipóteses de ICP com o tamanho de cada uma, o gabarito, a oferta, o master copy e a lista do que não será dito.

**O que o cliente precisa fazer.** Aprovar ou editar no C1. A edição do cliente é salva como diff.

**Critério de saída.** C1 aprovado por escrito, com data e nome de quem aprovou.

## D8 a D10 · Primeira rodada

**Objetivo.** Campanha de LinkedIn no ar no D10 e sequência de email montada, pausada, esperando o fim do aquecimento.

**O que a gente faz.** Tudo com skill v0.1, na ordem do fluxo da rodada (ver `README.md`):

1. `montar-tam`: lista crua da hipótese aprovada, com supressão aplicada.
2. `validar-lista` e `detectar-tecnografia`: veredito por conta com evidência, verificação adversarial e primeira frase. Gate H1.
3. `mapear-comite`: até 3 contatos por conta, com estimativa de crédito aprovada antes do enrich.
4. `copy-email` e `juiz-de-copy`: sequência de 4 toques e prompt da Syndie. Gate H2 interno e depois C2 com o cliente.
5. `syndie-flow-builder`: JSON do fluxo e CSV de upload; importação pela interface da Syndie.
6. `apollo-sequence-builder`: contas, contatos e sequência criados no Apollo, pausada.
7. `qa-lancamento`: emails renderizados, supressão e duplicata refeitas, caixas e limites conferidos. Gate H3.
8. `registrar-ledger`: lote no ledger com estágio Working e cópia pro CRM do cliente pelo adaptador, se houver.

Com H3 aprovado, a campanha do LinkedIn é ativada. O email fica pausado até as caixas fecharem 14 dias de aquecimento.

**O que o cliente recebe.** A copy da rodada pra aprovar (email, convite e mensagens do LinkedIn), e a confirmação do lançamento com o número de contas e contatos da rodada.

**O que o cliente precisa fazer.** Aprovar ou editar a copy no C2 até o D9, pra que o QA e o lançamento caibam no D10.

**Critério de saída.** C2 aprovado. H3 registrado no `05-qa-lancamento.md`. LinkedIn no ar. Sequência de email criada e pausada. Lote no ledger.

## D15 em diante · Operação

**Objetivo.** Email no ar e o loop rodando: cada semana mede, cada correção ensina, cada reunião volta com resultado.

**O que a gente faz.**

1. No D15, com as caixas aquecidas (`aquecida_em` preenchido no `cliente.yaml`), roda o QA de novo e inscreve os contatos na sequência. Respeita o teto de 20 a 30 envios por caixa por dia.
2. Trata as respostas: classifica e rascunha, e o operador envia (a `triagem-replies` é da semana 2; até lá, manual). Nenhuma automação reenvia mensagem a quem recebeu e não respondeu.
3. Pra cada reunião marcada, manda ao vendedor do cliente o brief e o pedido de resultado em 48 horas (a `handoff-reuniao` é C1; na v0.1 é manual). Ver C3.
4. Toda semana, relatório pro cliente: reuniões, funil da rodada contra o baseline, o que aprendemos e os próximos testes (a `relatorio-cliente` é C1 e a `review-semanal` é da semana 2; na v0.1 o relatório é montado à mão a partir da aba `rodadas` do ledger).
5. No fim de cada rodada, roda o `loop-de-licoes` (manual na v0.1): diffs viram lições marcadas cliente ou ofício, e `aprendizado/ciclos.md` registra o % mantido sem edição por skill.
6. Uma vez por mês, revisão de aprendizado com o cliente: quais hipóteses de ICP se confirmaram, quais saem, o que muda na oferta (a `aprendizado-mensal` é da semana 2). Mudança na estratégia volta pro C1.

**O que o cliente recebe.** Relatório semanal. Brief de cada reunião marcada. Revisão mensal.

**O que o cliente precisa fazer.** Devolver o resultado de cada reunião em 48 horas (C3). Ler o relatório semanal e responder quando houver decisão pedida.

**Critério de saída da fase de onboarding.** Email no ar, primeira semana de relatório entregue e pelo menos uma reunião com resultado devolvido pelo C3. A partir daí o cliente está em operação contínua.

## Gates do cliente

Os gates H0 a H3 continuam internos e seguem o `CLAUDE.md` do motor. O serviço acrescenta três gates que envolvem o cliente. Os donos de cada um ficam em `gates` no `cliente.yaml`, e toda decisão de gate é salva como diff em `aprendizado/diffs/` do workspace (modelo em `schemas/diff.template.md`).

| Gate | O que se aprova | Quem | Quando | Onde fica o registro |
|---|---|---|---|---|
| C1 · Estratégia | Hipóteses de ICP, gabarito, oferta, master copy, o que não pode ser dito, números e claims autorizados | Aprovador do cliente | D7, depois do H0. De novo quando a revisão mensal propõe mudança | Diff do C1 em `aprendizado/diffs/`; números e proibições na `doutrina-cliente.md` |
| C2 · Voz | Copy da rodada: sequência de email, convite e mensagens do LinkedIn, prompt da Syndie | Aprovador do cliente | Até o D9 na primeira rodada; antes do H3 em cada rodada seguinte | Diff do C2 em `aprendizado/diffs/`; preferências de voz na `doutrina-cliente.md` |
| C3 · Resultado | Resultado de cada reunião marcada | Vendedor do cliente que recebeu a reunião | Até 48 horas depois da reunião | Aba `reunioes` do ledger: `resultado`, `proximo_passo`, `data_resultado` |

### C1 · Estratégia

O cliente aprova antes de qualquer lista ser enriquecida ou mensagem escrita. Aprovação é por escrito, com data e nome. Edição do cliente vira diff e, quando é fato de mercado ou de marca, vai pra `doutrina-cliente.md`. Número que o cliente não autorizou por escrito não entra em copy.

### C2 · Voz

Nas primeiras rodadas o aprovador lê toda a copy. Depois de duas rodadas seguidas aprovadas sem edição dele, o C2 vira amostragem: o aprovador lê uma amostra da rodada (a copy de um segmento, por exemplo) em vez de tudo. Se ele editar algo na amostra, a rodada seguinte volta a ter leitura completa. O diff dele alimenta a `doutrina-cliente.md`, e é por isso que a amostragem chega.

### C3 · Resultado

A reunião marcada vai pro vendedor do cliente com o brief. Sem o resultado de volta, o loop não sabe se a lista e a copy trouxeram conta certa ou só reunião. O vendedor preenche em até 48 horas três campos fixos da aba `reunioes` do ledger:

- `resultado`: `qualificou`, `nao_qualificou`, `proposta`, `fechou` ou `nao_compareceu`;
- `proximo_passo`: texto livre;
- `data_resultado`: `AAAA-MM-DD`.

Passadas 48 horas sem preenchimento, o operador cobra uma vez e registra a cobrança em `nota`. Resultado em branco aparece no relatório semanal como reunião sem retorno.

## Em qual stack operar

Decisão aberta. Três hipóteses, em ordem de preferência pros primeiros clientes. Cada uma tem o teste que decide se fica.

| Hipótese | Como funciona | A favor | Contra | Teste |
|---|---|---|---|---|
| A · A stack é nossa | Apollo e Syndie operados por nós, ledger em Google Sheets compartilhado com o cliente, export pro CRM dele | Setup mais rápido, controle total do dado do loop | O cliente vê o dado no CRM dele só por cópia | Dias do kickoff à primeira campanha, e quanto o cliente pede do dado no CRM dele |
| B · A stack é dele | Adaptadores pro CRM e o sequenciador que ele já usa | Mais aderente ao que o time dele já opera | Cada cliente novo pode exigir um adaptador novo | Horas de setup por cliente; passou de 10, volta pra A |
| C · Híbrida | Execução nossa (Apollo, Syndie), estado no CRM dele via sincronização | Provável ponto de chegada | Exige o contrato de CRM do motor estável antes | Só depois de 2 clientes rodando em A |

Até a decisão, novos clientes entram em A. O campo `crm` do `cliente.yaml` diz pra onde a `registrar-ledger` copia contas e contatos (`account-guardian`, `hubspot` ou `nenhum`).
