# Protocolo de aprendizado

Como a GTM Machine aprende. Ler antes de gravar qualquer lição, no motor ou no workspace.

O aprendizado é estrutural e faz parte do trabalho: cada correção humana vira regra no lugar certo, e a rodada seguinte já sai com ela. Nunca se cria arquivo de "feedback" por episódio.

## Onde o conhecimento mora

| Arquivo | O que guarda | Onde |
|---|---|---|
| `_protocolo.md` (este) | O meta: como aprender | motor |
| `doutrina/<ofício>.md` | Como trabalhar, um arquivo por ofício (outbound, escrita, produção com agentes). Documento vivo, editado no lugar | motor |
| `estrategia/doutrina-cliente.md` | Números autorizados, âncoras, proibidos, voz da marca, preferências do aprovador | workspace |
| `aprendizado/diffs/` | Pares versão da máquina × versão aprovada, um por gate e peça | workspace |
| `aprendizado/ciclos.md` | % mantido sem edição por skill e rodada | workspace |
| `aprendizado/licoes-candidatas-motor.md` | Lições de ofício esperando promoção pro motor | workspace |

Feedback novo entra na doutrina do ofício correspondente. Se o ofício não tem doutrina, criar `doutrina/<ofício>.md`, nunca um arquivo de episódio.

## Dois canais de captura

1. **Correção em conversa.** O operador ou o aprovador corrige explicitamente → nasce `[regra]` direto, com procedência.
2. **Diff de gate.** O que o humano muda em silêncio antes de aprovar ou enviar. Todo gate (H0 a H3) salva a versão da máquina e a versão aprovada em `aprendizado/diffs/<rodada>-<gate>-<peça>.md`. É o canal que captura o que a conversa não captura.

## Loop de lições (diff pós-gate)

- **Gatilho:** fim de rodada, ou quando o operador pedir. Se a versão aprovada não estiver salva, pedir antes de fechar a tarefa: "me manda a versão que foi aprovada ou enviada".
- **Classificar cada mudança:** cosmética sem princípio (ignorar), erro da máquina (candidata), preferência nova (candidata, marcada como preferência).
- **Extrair o princípio, não a mudança.** "CTA pode declarar a intenção" e não "trocou a frase X pela Y". Lição boa evita uma classe de erro futura.
- **Marcar o endereço:** `cliente` (mercado, marca, número, voz do aprovador) ou `ofício` (como escrever, qualificar, operar). Na dúvida, `cliente`: é mais barato promover depois do que tirar do motor.
- **Portão de aprovação:** apresentar as lições e perguntar "gravo essas lições?". Aprovada → `[regra]`. Se o humano editar a formulação, gravar a versão dele. Sem resposta → `[hipótese]` marcada "diff não confirmado", reapresentada na próxima oportunidade.
- **Silêncio é sinal:** o que não foi mudado num texto que aplicava regras ou hipóteses recentes conta como confirmação delas.

## Ciclo de vida de uma regra

- **Entrada:** só o que muda comportamento futuro e não é derivável dos arquivos. Toda regra carrega procedência (data + o que aconteceu) em uma linha.
- **Força:** correção explícita ou lição aprovada nasce `[regra]`. Padrão visto uma vez sem confirmação nasce `[hipótese]`. Hipótese vira regra quando se repete, é confirmada ou sobrevive intacta a um diff; marcar a promoção com data.
- **Atualização:** contradição ou refinamento edita a regra existente no lugar (nova data, nota do que mudou). Proibido criar regra paralela sobre o mesmo ponto.
- **Esquecimento:** hipótese não confirmada em 3 rodadas sai na próxima consolidação. Regra revogada sai; deixar lápide de uma linha ("não fazer X; valeu até <data> porque Y") só se o erro for sedutor o bastante pra voltar.
- **Consolidação:** no fim da rodada, doutrina com 3+ hipóteses, contradição ou inchaço é reescrita inteira. Doutrina grande demais é dividida por canal (email, LinkedIn, listas).
- **Confirmação pelo mercado:** uma regra de copy também se confirma quando o ângulo tem reply positivo acima da média da rodada. Em outbound o prospect também é juiz.

## Loop de trabalho

1. **Antes** de uma tarefa de ofício: ler a doutrina dele e a `doutrina-cliente.md` do workspace. Nada de copy, lista ou peça sem isso.
2. **Durante:** cada correção é sinal. Anotar o princípio por trás, não o caso.
3. **Depois:** salvar o diff do gate; rodar o loop de lições no fim da rodada; atualizar `ciclos.md`.

## Promoção cliente → motor

A doutrina do motor só recebe ofício, e só anonimizado.

1. **Nasce no workspace.** Toda lição marcada `ofício` é gravada onde se aplica no cliente (`doutrina-cliente.md` ou a regra da rodada) e também copiada pra `aprendizado/licoes-candidatas-motor.md` do workspace, com data, rodada e diff de origem.
2. **Anonimizar.** Antes de subir: tirar nome de cliente, conta, pessoa, número, preço, vertical identificável. O exemplo vira empresa fictícia ou categoria ("um e-commerce de beleza"). Se o princípio não sobrevive sem o caso, ele é de cliente.
3. **Critério de subida:** a lição aparece em **2 clientes** diferentes, ou o **mantenedor do motor** decide promover antes (registrando o motivo).
4. **Gravar no motor:** a lição entra na `doutrina/<ofício>.md` com a força que tem (`[regra]` ou `[hipótese]`) e procedência anonimizada ("2 clientes, rodadas de 2026-10"), ou vira mudança numa `SKILL.md` ou na rubrica do juiz.
5. **CHANGELOG:** toda promoção gera entrada no `CHANGELOG.md` com versão, data, mudança e origem ("cliente zero + cliente 2", nunca o nome).
6. **Conferir:** `python scripts/check_sanitize.py` antes de fechar.

Lição de cliente nunca sobe. Número autorizado, âncora, pricing e voz do aprovador ficam no workspace para sempre.
