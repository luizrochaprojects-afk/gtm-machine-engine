# Doutrina: produção com agentes

Ofício de qualquer tarefa em que artefatos são gerados ou revisados em lote por agentes: validação de lista, copy por conta, pesquisa. Lida pela `validar-lista`, `detectar-tecnografia`, `copy-email` e `juiz-de-copy`.

Procedência: consolidada em 2026-10 a partir das rodadas de validação de lista do cliente zero. Exemplos sem nome de conta.

## Spec e calibração

- [regra] **Spec pela função, não pelos ingredientes.** Definir o artefato pelos componentes ("fato verificável, sem jargão, 2 frases") produz lixo que cumpre a lista: o agente entrega o que a spec mede. Definir pelo trabalho que o artefato faz ("fazer o dono sentir dinheiro parado"). Procedência: 274 linhas reprovadas em bloco por "cuspir fatos".
- [regra] **Um exemplo reprovado com erros nomeados calibra mais que dez regras abstratas.** Correção humana vira duas coisas: a regra abstrata na doutrina e o caso concreto embutido nos prompts seguintes (linha ruim + por quê + 1 a 2 reescritas boas).

## QA e revisão

- [regra] **Reescrita por qualquer gatilho (variedade, dedup, colisão de lote) re-passa por todos os testes.** Crítico otimizando uma dimensão sem piso nas outras piora o conjunto.
- [regra] **QA mecânico verde é pré-condição, nunca veredito.** Regex pega travessão, jargão, acento; não pega motivação atribuída, pitch por negação, máxima de palestra. Não reportar "QA passou limpo" sobre pergunta editorial. Procedência: 67% de um lote "limpo" caiu na leitura editorial.
- [regra] **Cada camada de revisão pega uma classe de erro, e olhos sem histórico são camada obrigatória:** gerador → crítico do ofício → leitura fria só com a linha final e a evidência → leitura humana. Quem carrega o contexto aprova o próprio contexto.
- [regra] **Reclamação de qualidade se responde lendo amostra, não contando padrão.** Regex de prevalência não refuta julgamento editorial.

## Dado e consolidação

- [regra] **Correção que não viaja com o dado ressuscita o erro.** Fato refutado pela verificação adversarial é bloqueio no registro que os agentes seguintes consomem, não observação numa coluna que ninguém lê.
- [regra] **Agente devolve nome de conta modificado** (corrige, abrevia, anexa a marca). Casar toda passada com a linha canônica pela chave `domain` normalizada; sem domínio, por nome exato → nome sem acento → prefixo com match único. Deduplicar no fim mantendo a linha que casou com a fonte.
- [regra] **Copy de agente sai em ASCII por padrão.** Exigir acentuação completa no prompt e checar por regex antes de entregar.

## Orçamento de busca e paralelismo

- [regra] **Teto de cerca de 200 WebSearch por sessão**, compartilhado entre todos os agentes; ele se recupera com o tempo (testar com uma busca antes de declarar a sessão morta).
- [regra] **WebFetch primeiro.** A prova de fit mora no site (checkout, login, página de assinatura ou clube, rodapé com a plataforma), não na busca. Busca só depois do fit resolvido, e só pra sinal de timing. Teto explícito no prompt: 2 WebSearch e 8 a 10 tool calls por empresa.
- [regra] **Lotes de até ~120 empresas por primeira passada**, como workflows pequenos em paralelo. Acima de ~16 agentes simultâneos o WebFetch devolve 429 e os agentes entram em backoff.
- [regra] **Verificação adversarial como workflow separado**, nunca segundo estágio do mesmo pipeline: no pipeline ela é a primeira coisa cortada quando o orçamento acaba.
- [regra] **Estouro no meio:** parar os workflows, consolidar pelo journal de cada run, marcar em `obs` o que ficou sem verificação. Nunca entregar linha degradada misturada com linha pesquisada.
- [regra] **Agrupar lotes de copy e revisão por vertical:** força o agente a diferenciar as contas mais propensas a colidir.
