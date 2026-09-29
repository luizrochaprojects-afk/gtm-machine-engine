# CLAUDE.md · workspace de <nome do cliente>

versao_motor: <x.y.z>

Workspace da GTM Machine para <nome do cliente>. Criado em <AAAA-MM-DD> pela `setup-workspace`. O motor fica dois níveis acima (`../../`); este workspace só guarda o que vale para este cliente.

## Antes de trabalhar

1. Ler o `CLAUDE.md` do motor (`../../CLAUDE.md`). As regras de lá valem aqui.
2. Ler a doutrina do motor que a tarefa pede (`../../doutrina/`): copy lê `outbound.md`, `escrita.md` e `ai-tells.md`; lista lê `outbound.md` e `producao-com-agentes.md`.
3. Ler `estrategia/doutrina-cliente.md`. Quando ela e a doutrina do motor falam do mesmo ponto, a do cliente ganha.
4. Configuração do cliente (ofertas, stack, remetentes, donos dos gates, ID do ledger, CRM): `cliente.yaml`. Nunca copiar esses valores para dentro do motor.

## Versão do motor

Este workspace foi montado com a versão acima. Ao atualizar o motor, conferir o `CHANGELOG.md` do motor, trocar a versão aqui e no `cliente.yaml` e anotar a data.

## Regras só deste cliente

Regras de operação que valem só aqui (ex.: dia da semana sem envio, quem precisa ser copiado numa aprovação). Uma linha por regra, com procedência (data e o que aconteceu). Regra de copy, voz ou número autorizado vai para `estrategia/doutrina-cliente.md`, não aqui.

-

## Onde fica cada coisa

| Pasta | O que guarda | Quem escreve |
|---|---|---|
| `contexto/fontes/` | O que o cliente mandou, como veio | operador (fora do git) |
| `contexto/extracoes/` | Uma nota por fonte, com trecho e origem | skills de contexto |
| `estrategia/` | Hipóteses, gabarito, ofertas, master copy, roteamento, doutrina do cliente | gates H0 e C1 |
| `supressao/` | Arquivos de supressão importados uma vez para o ledger | operador |
| `segmentos/` | Busca, sequência e fluxo por segmento | skills |
| `rodadas/` | Uma pasta por rodada, arquivos numerados na ordem do fluxo | skills (não se editam) |
| `aprendizado/` | Diffs de gate, ciclos, lições candidatas ao motor | skills e loop de lições |
| `relatorios/` | Relatórios internos | skills |
| `entregas/` | Única pasta que sai para o cliente | operador |
