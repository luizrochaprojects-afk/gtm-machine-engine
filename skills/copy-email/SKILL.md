---
name: copy-email
description: Escreve a sequência de cold email de 4 toques (D1 fato e dor, D4 prova, D8 recurso ou ângulo novo, D13 encerramento) de uma rodada de outbound, a partir da doutrina do motor, da doutrina-cliente, da oferta, do master copy e do segmento do workspace ativo; passa pela juiz-de-copy, renderiza 3 contatos com scripts/render_email.py e leva ao gate H2, salvando o diff. Use na etapa E5, quando o operador disser "escreve a sequência", "copy da rodada", "roda a copy-email", "email da r1", "sequência de email pro segmento X", "refaz o D4". Não escreve o prompt nem as mensagens da Syndie: isso é da syndie-flow-builder.
---

# copy-email

Escreve `rodadas/<rodada>/04-sequencia-email.md`: quatro toques de email pra um segmento e uma oferta, no formato de `schemas/sequencia-email.schema.md`. A skill não sabe quem é o cliente. Voz, saudação, fecho, números autorizados, âncoras, pricing, fórmula de pedido de horário e fórmula de encerramento vêm do workspace ativo. Se algo disso não estiver escrito lá, pergunte; nunca invente.

Nada sai daqui direto pro operador: a sequência passa pela `juiz-de-copy`, é renderizada em 3 contatos e só então chega ao gate H2.

## Antes de escrever: o que ler

Leia tudo, nesta ordem. Quando dois arquivos falam do mesmo ponto, vale o de cima.

| # | Arquivo | O que tirar dele |
|---|---|---|
| 1 | `estrategia/doutrina-cliente.md` | Saudação, fecho, assinatura e registro do remetente; números, claims e âncoras autorizados (e em qual toque cada um pode entrar); forma canônica de pricing; fórmula de pedido de horário e a partir de qual toque; fórmula de encerramento; mecânica por caso de uso; o que nunca dizer; assets que existem (com URL) |
| 2 | `estrategia/ofertas/<oferta>.md` | Porta de entrada (o primeiro compromisso que o prospect aceita), a dor que a oferta resolve, a mecânica concreta |
| 3 | `estrategia/master-copy/<oferta>.md` | Dor, prova e ângulos já aprovados no H0. Todo toque parte daqui |
| 4 | `segmentos/<segmento>/` | Tese do segmento, o que é particular da operação dessas contas, vocabulário do setor |
| 5 | `contexto/extracoes/voz-do-cliente-*.md`, se houver | A dor nas palavras do comprador: expressões literais, objeções, motivos de não decidir. Use a língua, nunca o nome de quem falou |
| 6 | `doutrina/outbound.md` | Seções "Cold email", "Frases banidas e QA de envio" e "A linha de abertura personalizada" |
| 7 | `doutrina/escrita.md` | Framing, verdade e forma |
| 8 | `doutrina/ai-tells.md` | Os quatro níveis. Escreva já pensando no Nível 4: pelo menos 1 particularidade por toque |
| 9 | `doutrina/producao-com-agentes.md` | Copy de agente sai em ASCII; reescrita re-passa todos os testes |

E também:

- `cliente.yaml`: a oferta (`ofertas[].id`, `segmento`, `arquivo`, `master_copy`), `remetentes.caixas_email[].assinatura`, `cadencia.email_passos` e o dono do gate H2 (`gates.H2`, mais `gates.C2` quando o aprovador do cliente ainda aprova a voz).
- `rodadas/<rodada>/03-contatos.csv`: as colunas disponíveis viram as variáveis possíveis.
- `rodadas/<rodada>/02-validacao.xlsx` (ou o JSON de vereditos): `primeira_frase` por conta e `adversarial.fatos_refutados`.
- Os diffs de H2 de rodadas anteriores (`aprendizado/diffs/*-H2-email.md`) e as `[hipótese]` da doutrina-cliente: o que o operador já cortou não volta.

## Pré-condições

Pare e diga ao operador o que falta se:

- não existe `aprendizado/diffs/<rodada>-H0-estrategia.md` com resultado aprovado (estratégia sem H0 não vira copy);
- falta a oferta, o master copy ou a doutrina-cliente;
- a doutrina-cliente não tem saudação, fecho ou fórmula de encerramento. Pergunte ao operador; com a resposta, proponha gravar como `[regra]` na doutrina-cliente com procedência (correção em conversa, ver `doutrina/_protocolo.md`).

## Passo 1: briefing da rodada

Antes de qualquer frase, monte e mostre ao operador em até 12 linhas:

- segmento, oferta e porta de entrada;
- a dor, numa frase, com as palavras do comprador;
- a prova autorizada, copiada literalmente da doutrina-cliente (frase, número ou âncora, e em que toque pode entrar). Se não houver nenhuma, escreva "sem prova autorizada: D4 usa mecanismo e porta de entrada";
- a forma da âncora: nomeada (só quando a lista reconhece o nome) ou por categoria;
- o recurso do D8: asset que existe hoje, com URL, ou "sem asset: D8 vai de ângulo novo";
- a fórmula de pedido de horário e o toque mínimo em que ela pode aparecer;
- a fórmula de encerramento;
- o que nunca dizer nesta rodada.

Esse briefing é a lista fechada do que pode ser afirmado. Frase que não se apoia nele, na `primeira_frase` da conta ou nas extrações não entra.

## Passo 2: variáveis e fallbacks

1. Liste as variáveis que a sequência vai usar. Prefira as que o Apollo já conhece (`first_name`, `last_name`, `company`, `title`). Qualquer outra (ex.: `primeira_frase`) vira campo custom no Apollo e precisa existir como coluna em `03-contatos.csv`.
2. **`primeira_frase`:** use só quando a rodada tiver primeira frase por conta. Ela mora no veredito; se não estiver em `03-contatos.csv`, proponha ao operador levar a coluna pra lá casando por `domain` (nunca por nome de empresa). Se a primeira frase de uma conta cita um fato que está em `fatos_refutados`, esvazie a célula dela (entra o fallback) e avise.
3. **Todo fallback é texto escrito, e a frase lê bem com ele.** Teste escrevendo a linha inteira com o fallback no lugar:
   - `Oi, {{first_name}}.` com fallback `tudo bem` vira "Oi, tudo bem." e lê bem.
   - `na {{company}}` com fallback `vocês` vira "na vocês" e reprova. Reescreva a frase ou troque o fallback ("na sua rede", "aí").
   - O fallback de `primeira_frase` é uma abertura de segmento em dois tempos: um fato verificável do segmento + a tensão que ele revela, 120 a 230 caracteres. Ele não passa no teste da intercambiabilidade por conta, e está tudo bem: o juiz o avalia como abertura de segmento.
4. Conte quantos contatos vão cair no fallback de cada variável. Acima de 20% em `primeira_frase` ou `first_name`, avise o operador antes de seguir: a rodada vai sair genérica pra esses contatos.
5. Preencha a tabela `## Variáveis` (variável, coluna, fallback). Variável que não está na tabela não pode aparecer no corpo.

## Passo 3: escrever os quatro toques

Regras que valem nos quatro:

- **Uma pergunta por email, e o email termina nela.** Nada depois da pergunta além do fecho e da assinatura da doutrina-cliente. Sem P.S.
- **Registro de email:** "para", "está", "você". Sem "pra" e "tá", salvo se a doutrina-cliente disser outra coisa. Coloquial, nunca corporativo.
- **Sem travessão (U+2014).** Ponto, vírgula ou dois-pontos.
- **Acentuação completa** desde o rascunho.
- **Spintax** (`{a|b}`) só em saudação e transições, nunca em frase com fato ou prova. Cada opção precisa passar em todos os testes sozinha; o render usa a primeira.
- **Você > nós:** mais frases sobre a operação do prospect do que sobre o remetente.
- **Pelo menos 1 particularidade por toque** (`ai-tells.md`, Nível 4). No D1 ela vem da `primeira_frase`; nos outros, do segmento ou da prova: número não redondo autorizado, nome verificável da âncora, detalhe específico da operação do segmento, expressão literal do comprador.
- **Valor no próprio toque:** cada email vale alguma coisa mesmo que não seja respondido. Follow-up que só "sobe" o anterior não existe.
- **Pedido de horário** só nos toques finais e só na fórmula da doutrina-cliente. Os toques D1 a D8 pedem um sim ou não barato. Se a doutrina-cliente só libera o pedido a partir de um toque que esta sequência não tem, nenhum toque pede horário. "Vale uma call rápida de 15 minutos?" e "faz sentido a gente conversar?" estão banidas em qualquer toque.
- **Número, âncora, preço ou asset** só como estão no briefing do passo 1.

### D1: fato + dor + valor + pergunta

- **Assunto:** até 5 palavras, neutro ou ligado ao gatilho. Sem nome do remetente, sem ponto de exclamação, sem isca.
- **Corpo:** 70 a 80 palavras, contando da primeira frase depois da saudação até a pergunta, com uma `primeira_frase` real de tamanho mediano no lugar da variável. Com o fallback, não pode passar de 80. Parágrafos de no máximo 2 frases.
- **Estrutura:**
  1. saudação da doutrina-cliente;
  2. `{{primeira_frase}}` sozinha no primeiro parágrafo (ou a abertura de segmento, se a rodada não tiver primeira frase por conta);
  3. a dor como hipótese específica, numa frase que funcione depois da primeira frase real e depois do fallback;
  4. o valor concreto: o que muda na operação dele, com a mecânica por caso de uso da doutrina-cliente. Nada de benefício genérico;
  5. a pergunta de sim barato, terminando o email;
  6. fecho e assinatura da doutrina-cliente.
- **Proibido no D1:** link, anexo, preço (salvo frase autorizada pra D1), pedido de reunião, comentário sobre o próprio email ("vou ser breve"), abertura banida ("Vi que", "Notei que", "<nome> aqui", "espero que esteja tudo bem").

### D1 por nível: decisor e champion

[hipótese, 2026-09-29] O D1 sai em duas variantes quando `03-contatos.csv` tem os dois níveis (algum contato com `papel = decisor` e algum com `champion` ou `influenciador`). Com um nível só, escreva um D1 só.

- **`## D1 · decisor`** (dono, C-level, head que responde pela receita): 2 a 3 frases depois da saudação, até 60 palavras. A dor em receita, risco ou posição competitiva. Nada de problema operacional: o decisor que lê trabalho manual delega o email pra quem faz o trabalho.
- **`## D1 · champion`** (quem opera CRM, lifecycle, retenção, e-commerce; o influenciador usa esta): 3 a 4 frases, 70 a 80 palavras. A dor em tempo, trabalho manual, régua que alguém monta na mão. Nada de ROI abstrato: quem opera não assina o orçamento e não sente o número.
- As duas variantes seguem todas as regras do D1 acima (primeira frase, uma pergunta, sem link, sem preço) e usam o mesmo assunto ou assuntos diferentes, à escolha. A `primeira_frase` da conta é a mesma nas duas; o que muda é a dor, o valor e a pergunta.
- D4, D8 e D13 continuam compartilhados. Escreva-os de forma que sigam bem depois de qualquer uma das duas variantes.

### D4: prova

- **Assunto:** `(mesma thread)`.
- **Corpo:** 50 a 80 palavras.
- Uma prova só, colada na dor do prospect numa frase (a ponte de `outbound.md`). Nada de parágrafo sobre o remetente.
- Sem prova autorizada, a prova é o mecanismo e a forma de medir (a porta de entrada da oferta). Nunca case, número ou cliente que a doutrina-cliente não autoriza.
- Termina numa pergunta de sim barato diferente da do D1.

### D8: recurso ou ângulo novo

- **Assunto:** `(mesma thread)`.
- **Corpo:** 40 a 80 palavras.
- **Recurso:** só se o asset existir hoje e estiver registrado na doutrina-cliente ou na oferta, com URL. A URL vai crua, sem Markdown.
- **Sem recurso, ângulo novo:** outra faceta da mesma dor, tirada dos ângulos do master copy ou das extrações de voz do cliente. Não repete a dor nem a prova dos toques anteriores.
- Termina numa pergunta de sim barato.

### D13: encerramento

- **Assunto:** `(mesma thread)` ou um assunto novo curto.
- **Corpo:** 30 a 60 palavras.
- Saída honesta que encerra a sequência de verdade, com a fórmula da doutrina-cliente. Não culpa o prospect pelo silêncio, não faz chantagem ("vou entender que não é prioridade"), não abre a porta pra mais um toque.
- Se a doutrina-cliente liberar pedido de horário neste toque, a pergunta é a fórmula dela. Senão, uma pergunta de sim barato que dá a saída.

## Passo 4: autochecagem mecânica

Antes de chamar o juiz, confira e corrija:

- nenhum travessão (U+2014) no arquivo;
- toda `{{variável}}` está na tabela, e toda linha da tabela tem fallback;
- cada toque tem exatamente um `?`, e ele está na última frase antes do fecho;
- D1 dentro de 70 a 80 palavras (variante de decisor: até 60); nenhuma URL no D1;
- com variantes: `## D1 · decisor` e `## D1 · champion` presentes, sem `## D1` simples;
- nenhuma palavra em ASCII onde falta acento (voce, nao, esta, sao, tambem, ja, ate, entao, operacao, reposicao, voces);
- nenhum "pra" ou "tá" no corpo, salvo se a doutrina-cliente permitir.

QA mecânico verde é pré-condição, não veredito (`producao-com-agentes.md`).

## Passo 5: gravar o arquivo

Grave `rodadas/<rodada>/04-sequencia-email.md` exatamente no formato de `schemas/sequencia-email.schema.md`: título, linha de versão, `## Variáveis`, `## D1` (ou `## D1 · decisor` e `## D1 · champion`), `## D4`, `## D8`, `## D13`, cada toque começando por `Assunto:`. Corpo sem Markdown. A linha de versão fica provisória (`juiz: pendente · rodadas de revisão: 0`) até o juiz voltar.

## Passo 6: juiz

Rode a `juiz-de-copy` sobre o arquivo. Ela avalia cada toque, revisa até 3 rodadas, roda a leitura fria, atualiza a linha de versão, escreve `## Notas do juiz` no fim do arquivo e grava o relatório em `rodadas/<rodada>/04-juiz-email.md`. Não mostre nada ao operador antes disso.

## Passo 7: render em 3 contatos

```bash
python scripts/render_email.py --sequencia rodadas/<rodada>/04-sequencia-email.md --contatos rodadas/<rodada>/03-contatos.csv --amostra 3 --saida rodadas/<rodada>/04-render-amostra.md
```

- Se a rodada tiver mais de um segmento no CSV, use `--amostra 3 --por segmento`.
- Garanta que a amostra tenha pelo menos um contato com `primeira_frase` vazia, pra ver o fallback renderizado. Se a amostra não pegar, rode de novo com `--linha N` apontando um contato com a coluna vazia. Se nenhum contato tiver, leia à mão cada frase com o fallback da tabela e registre que leu.
- **Saída 1** (sobrou `{{`, variável não declarada ou travessão): corrija o texto e rode de novo.
- **Aviso de palavra sem acento:** corrija se for erro; se for nome próprio, deixe e anote.
- Qualquer correção de texto depois do juiz volta ao juiz só no toque alterado (reescrita re-passa os testes). Correção de acento ou de merge não abre rodada nova de revisão.

## Passo 8: gate H2

1. **Abra o diff antes de mostrar.** Crie `aprendizado/diffs/<rodada>-H2-email.md` a partir de `schemas/diff.template.md`: cabeçalho (rodada, gate `H2`, peça `email`, data, skill `copy-email`, versão do motor do `cliente.yaml`, aprovador de `gates.H2`) e o bloco `## Versão da máquina` com o `04-sequencia-email.md` inteiro, do jeito que vai ser mostrado. Deixe `Resultado`, `## Versão aprovada`, `## Notas do operador` e `## Métrica` em aberto.
2. **Mostre ao operador, nesta ordem:** os 4 toques renderizados pra um contato real; a tabela de variáveis com a contagem de quem cai em fallback; o placar do juiz por toque; o conteúdo de `## Notas do juiz`; o resultado do render.
3. **O operador edita** no próprio arquivo ou no chat. Aplique a edição no `04-sequencia-email.md`. Se a edição cair num veto do juiz (travessão, segunda pergunta, merge sem fallback, número não autorizado), avise uma vez, com o motivo. A decisão é dele.
4. Depois de qualquer edição, rode o render de novo. Edição aprovada também não pode sair com `{{` sobrando.
5. **Feche o diff** quando o operador aprovar:
   - `Resultado`: `aprovado sem edição`, `aprovado com edição` ou `reprovado`;
   - `## Versão aprovada`: o arquivo aprovado inteiro, ou "igual à versão da máquina";
   - `## Notas do operador`: uma linha por mudança relevante, `<o que mudou> · <por quê, nas palavras de quem aprovou>`. Pergunte o porquê de cada mudança que não for óbvia; se ele não quiser dizer, escreva "sem motivo declarado".
   - Não preencha `## Métrica`: é da `loop-de-licoes`.
6. Se o `cliente.yaml` põe o aprovador do cliente no gate (H2 ou C2), a versão aprovada pelo operador vai pra ele, e a edição dele entra no mesmo diff como mais uma linha de notas, com o papel de quem mudou.

Diff fechado não se edita. Mudança depois do fechamento vira diff novo.

## O que grava e onde

| Arquivo | Quando |
|---|---|
| `rodadas/<rodada>/04-sequencia-email.md` | Passo 5, atualizado pelo juiz e pelo operador |
| `rodadas/<rodada>/04-juiz-email.md` | Gravado pela `juiz-de-copy` |
| `rodadas/<rodada>/04-render-amostra.md` | Passo 7 |
| `aprendizado/diffs/<rodada>-H2-email.md` | Aberto no passo 8.1, fechado no 8.5 |
| `estrategia/doutrina-cliente.md` | Só com aprovação, quando o operador responder uma lacuna (saudação, fecho, encerramento) |

## Armadilhas

- **Escrever antes do briefing.** Sem a lista fechada do que pode ser afirmado, o texto enche de claim que ninguém autorizou.
- **Fallback que quebra a gramática.** Variável depois de "na", "da", "pela" é o erro mais comum. Leia a frase com o fallback, sempre.
- **Primeira frase que não encaixa.** A frase seguinte precisa funcionar depois da primeira frase real e depois do fallback. Teste com as duas.
- **Prometer o que não existe.** "Te mando a planilha", "segue o case": só se o asset existir antes do envio.
- **D8 que repete o D1 com outras palavras.** Ângulo novo é faceta nova da dor, não sinônimo.
- **Encerramento que não encerra.** "Se mudar de ideia, estou por aqui" seguido de mais um toque é mentira.
- **Ajustar a fórmula do remetente.** Saudação, fecho, pedido de horário e encerramento da doutrina-cliente entram literais. Se parecerem ruins, diga ao operador; não reescreva.
- **Uma sequência pra dois segmentos.** Segmento diferente tem dor diferente: uma sequência por segmento e oferta.

## Exemplo (empresa fictícia)

A Acme vende software que sugere o pedido de reposição de cada loja de uma rede de material de construção. A doutrina-cliente fictícia define "Oi, {{first_name}}." e "Abs, Ana." e não autoriza nenhum número no D1.

**D1 reprovado** e por quê: "Oi, {{first_name}}! Vi que a {{company}} está crescendo muito. A gente ajuda empresas como a sua a otimizar a reposição de estoque com IA. Faz sentido uma call rápida de 15 minutos? Ou prefere que eu mande um material?"

- "Vi que" é abertura banida; "crescendo muito" passa no teste da intercambiabilidade com nota máxima.
- "A gente ajuda empresas como a sua" é frase banida; "otimizar" é jargão.
- Duas perguntas; pedido de call no D1; promete material que não existe.
- Zero particularidade; todas as frases falam do remetente.

**D1 aprovado:**

> Oi, {{first_name}}.
>
> {{primeira_frase}}
>
> Quando a reposição de sábado depende de planilha, o cliente da obra não espera: leva o cimento no concorrente da esquina.
>
> A Acme lê a venda de cada loja por hora e sugere o pedido antes da ruptura, dentro do estoque mínimo que o comprador define.
>
> Hoje a reposição de sábado na {{company}} ainda sai de planilha?
>
> Abs, Ana.

Com `primeira_frase` = "A Casa Exemplo abriu a 14ª loja em agosto, em Sorocaba. Cada loja nova é mais uma planilha de reposição para o fim de semana." (o corpo renderizado fica com 79 palavras) e fallback de `company` = "sua rede" ("na sua rede" lê bem).
