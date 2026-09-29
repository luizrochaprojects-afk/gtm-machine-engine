# Doutrina: outbound

Ofício de cold email, LinkedIn e a linha de abertura personalizada por conta. Pressupõe `doutrina/escrita.md` e `doutrina/ai-tells.md`. O que é de um cliente (números autorizados, âncoras, pricing, fórmulas de CTA do remetente, voz) está na `estrategia/doutrina-cliente.md` do workspace e tem precedência sobre este arquivo quando os dois falam do mesmo ponto.

Procedência: consolidada em 2026-10 a partir das rodadas de outbound do cliente zero. Exemplos reescritos com empresa fictícia.

## Cold email

- [regra] **Quatro tempos secos:** (1) abertura que prova relevância com um fato da conta, (2) hipótese de problema específica, (3) valor concreto já no toque 1, (4) pergunta de baixa fricção que se responde com um sim barato. Nunca pedir call de 30 minutos no toque 1.
- [regra] **CTA nunca promete asset que não existe.** "Te mando a conta pronta", "mando a planilha", "te passo o case" só entram se o asset existir antes do envio. Sem asset, o CTA é um sim ou não barato ("quer ver como isso rodaria na {{empresa}}?"). Procedência: CTA reprovado no gate de copy por prometer planilha que ninguém tinha feito.
- [regra] **Toque 1 em 70 a 80 palavras**, parágrafos de no máximo 2 frases curtas. Assunto curto, neutro ou ligado ao gatilho.
- [regra] **Ser curto em vez de anunciar que vai ser curto.** Comentário meta sobre o próprio email ("sei que você é ocupado, vou ser breve", "prometo 30 segundos", "desculpa o email do nada") gasta a linha mais cara do texto.
- [regra] **Uma pergunta só, e o email termina nela.** Sem CTA duplo, sem P.S. que se desculpa ou reabre ("mesmo que o timing não seja esse..."). O hedge no fim ensina que a resposta é opcional.
- [regra] **A ponte pra prova é uma ideia só, colada no problema do prospect.** Um cliente de referência (âncora) entra numa frase que fala da dor do prospect, não num parágrafo sobre o remetente. Reprovados: parágrafo sobre nós ("a gente opera o CRM de X, que vive de Y"); frase-salada com âncora + mecânica + benefício + preço num fôlego. Âncora, número e preço autorizados vêm da `doutrina-cliente.md`.
- [regra] **Preço não entra no toque 1**, salvo quando a `doutrina-cliente.md` autorizar uma frase específica (ex.: garantia). Mesmo autorizada, é uma frase, não um bloco.
- [regra] **Pedido de horário só nos toques finais.** Toques 1 a 3 mantêm o sim ou não barato. A embalagem de vendedor pro mesmo pedido ("vale uma call rápida de 15 minutos?", "faz sentido a gente conversar?") está banida em qualquer toque: é a frase que o prospect já leu 40 vezes na semana. A fórmula de pedido de horário do remetente fica na `doutrina-cliente.md`.
- [regra] **Encerramento (breakup) dá saída honesta** e termina a sequência de verdade. A formulação exata é voz do remetente e fica na `doutrina-cliente.md`.
- [regra] **Follow-up sempre adiciona substância nova:** prova, recurso ou ângulo. Nunca "bumping this", "voltando no meu último email", "só subindo esse email". Toque sem insight, prova ou recurso novo não sobe. 4 a 6 toques e para.
- [regra] **Prompt pra IA de ferramenta de outbound (Apollo AI, Syndie e afins) não referencia campo de CSV.** A ferramenta já injeta o contexto da conta e do contato; o prompt descreve o que a abertura precisa ser (fato específico da conta + tensão em dinheiro) e deixa a IA achar o fato. Sem `{{primeira_frase}}`, sem "se o campo estiver vazio". Só a merge tag do nome.

## Frases banidas e QA de envio

Vale pra email, DM e nota de convite.

- [regra] **Banidas na abertura** (tell de SDR automatizado): "Vi que", "Notei que", "Percebi que", "Reparei que", "<nome> aqui", "espero que esteja tudo bem", "passando pra", "vi seu perfil no LinkedIn", "dei uma olhada no site de vocês". A abertura é fato + tensão, não saudação nem declaração de que você olhou algo.
- [regra] **Banidas no corpo:** "a gente ajuda empresas como a sua a...", "somos uma startup que...", "queria trocar uma ideia / pegar sua opinião" quando é pitch, "sou um grande fã do trabalho de vocês". Todas passam no teste da intercambiabilidade com nota máxima, que é o problema.
- [regra] **Elogio não é personalização; mostrar o dever de casa é.** Trocar "admiro o que vocês construíram" pelo fato específico que só quem pesquisou aquela conta saberia.
- [regra] **Personalização fecha em dinheiro ou trabalho, não em biografia.** Faculdade, cidade, maratona, hobby, mesmo verdadeiros, provam que existe um enriquecedor de dados, não que se entendeu a operação. Se o fato pessoal não desemboca numa tensão comercial, não entra.
- [regra] **QA obrigatório com o email renderizado, não o template:** merge tag crua ou vazia ("Oi {{first_name}}", "na , vocês...") mata o toque e queima a sequência; acentuação completa (copy de agente sai em ASCII por padrão: "voces", "propria"); nome de empresa e cargo conferidos contra a lista. Linha a linha em pelo menos 3 contatos por segmento.
- [regra] **Passada final de tesoura:** reler o email inteiro e apagar toda frase que poderia ir, sem edição, pra qualquer outra conta da lista. O teste da intercambiabilidade vale do assunto ao CTA.
- [hipótese] **Teste do colega:** ler o toque em voz alta e perguntar se você mandaria aquilo, com aquelas palavras, pra um par que respeita. O que não sobrevive é linguagem de vendedor. Promover a regra se pegar o que os 5 testes da abertura deixam passar.

## A linha de abertura personalizada (`primeira_frase`)

- [regra] **Dois tempos, não um:** frase 1 é o fato específico e verificável; frase 2 é a tensão que o fato revela. Fato sozinho é enunciado, não gancho. 2 frases, 120 a 230 caracteres. A tensão termina em dinheiro ou esforço real do prospect (venda que não sai, margem na mesa, custo de readquirir, trabalho manual).
- [regra] **Por que essa conta e por que agora.** O fato carrega recência ou movimento (lançamento, vaga, captação, loja nova, troca de plataforma, mudança de sortimento). Fato estático e verdadeiro há três anos não explica por que o email chegou hoje. Gatilho perecível leva a data da checagem.
- [regra] **Teste da intercambiabilidade**, o mais decisivo: trocar o nome da empresa por outra da mesma vertical. Se a frase continua fazendo sentido, é template com um dado enfiado. "Fórmula manipulada tem data pra acabar" reprova; o nome do clube de assinatura, o número de lojas, a data da vaga aprovam. Foi o teste que mais reprovou (94 de 274 linhas numa rodada).
- [regra] **Nunca atribuir motivação a uma decisão do prospect** ("a troca de plataforma foi atrás de analytics"). Cita-se o fato público da decisão, nunca o porquê.
- [regra] **Nunca tratar compra ou escolha recente do prospect como insuficiente** ("a ferramenta que vocês escolheram não resolve X"): a alfinetada volta pra quem escolheu. Nunca devolver o case do fornecedor dele ("vi no case do seu fornecedor que vocês...").
- [regra] **Sem pitch por negação:** se a ausência descrita é exatamente o que o remetente vende ("só não escolhe quem chamar"), a frase é anúncio disfarçado.
- [regra] **Sem máxima de palestra** na frase 2 ("analytics conta o que já aconteceu"). Observação sobre a conta, não sobre o mundo.
- [regra] **Nunca afirmar categoricamente o que a empresa não tem** ("nada dispara", "não existe régua") sem evidência de ausência. Com evidência fraca, um hedge honesto e só um: "pelo que dá pra ver de fora", "se eu li certo". Número que a verificação adversarial não confirmou não entra (caso real: dois números inflados de uma conta passaram duas revisões de copy antes de serem pegos).
- [regra] **A tensão nunca soa como auditoria ou puxão de orelha.** "Ninguém cuida de quem parou de voltar" reprova. "Isso só vira lista quando alguém senta pra cruzar na mão" aprova. O inimigo é a ferramenta, não o time (ver `escrita.md`).
- [regra] **Zero mecânica de produto na abertura.** Sem nome do remetente, case, número de resultado ou âncora; a prova já está no corpo da sequência.
- [regra] **Pipeline de geração em lote:** gerar por vertical (força diferenciação entre contas parecidas) → passada crítica com os 5 testes (intercambiabilidade, "e daí?", culpa, "como você sabe?", voz) → leitura fria por agentes novos que só veem a linha final e a evidência resumida (gramática, sentido na primeira leitura, fato não deturpado; pegou 23 de 174 numa rodada) → leitura humana final. Reescrita por variedade também passa pelos 5 testes.

## LinkedIn: primeiro toque (convite ou DM)

- [regra] **O gancho é o problema que a pessoa vive, nunca o produto.** Abrir explicando o que o remetente faz é pitch.
- [regra] **A primeira mensagem existe pra abrir conversa**, não pra explicar a solução. Mesmo uma frase de produto já pesa. O "como funciona" é a recompensa da resposta.
- [regra] **DM pós-conexão pede um primeiro sim barato:** pergunta que se responde com sim ou não ("hoje alguém aí acompanha quanto da receita vem da base? Um sim ou não já me ajuda"), nunca pergunta-ensaio ("como você olha isso?") nem frase professoral.
- [regra] **"Queria pegar sua opinião / trocar uma ideia sobre X" quando o objetivo é vender está banido.** É pedido de tempo disfarçado de curiosidade. Se o convite é comercial, diz isso com leveza.
- [regra] **História do remetente como empatia, não como flex:** "vivi esse problema, por isso construí isto". Inverte o eixo de "você tem um problema, eu resolvo" pra "eu vivi isso". A empresa entra como desfecho da história, sem explicação. A história real de cada remetente fica na `doutrina-cliente.md`; nunca inventar biografia.
- [regra] **CTA aponta pra pessoa e pro tema, com saída fácil.** Nunca demo ou call no primeiro contato.
- [hipótese] Declarar a intenção com leveza no CTA ("...e mostrar um pouco do que estou construindo") é transparência, não pitch; o proibido segue sendo explicar a mecânica. Aprovado uma vez num diff.
- [regra] **Ancorar em fato real e específico** (vaga com cargo, captação com data). Nunca "vi seu post sobre X" se o post não existe.
- [regra] **Fundir toques é destilar**, não empilhar: a melhor ideia de cada um num fôlego curto, em blocos de 1 a 2 frases.
- [regra] **Follow-up sem resposta:** uma faceta nova do mesmo problema + saída fácil ("se não for o momento, sem problema"). 4 a 6 dias depois; no máximo 2 DMs, depois nutrir pelo feed (curtir, comentar), sem insistir.
- [hipótese] Cadência warm: conectar → curtir ou comentar posts → DM 1 (problema + sondagem de momento) → DM 2 (faceta nova).
- [hipótese] **Reagir ao detalhe concreto do post, nunca à tese.** A tese é a parte mais intercambiável de qualquer texto e a primeira que o modelo pega.
- [hipótese] **Quanto menor o vão que a IA preenche, mais humano o texto.** Em ferramenta com placeholder, escrever a mensagem fixa à mão e deixar pra IA só o slot curto.
- [hipótese] **Sem detalhe concreto, mandar convite sem nota.** Nota genérica gasta a única impressão e marca o perfil como automatizado.

## Sinais e listas

- [regra] **O sinal "contratando CRM" do Apollo tem muito ruído.** Numa rodada, só 9 de 29 contas com "vaga de CRM" tinham vaga real de CRM ou lifecycle; o resto era vaga de vendas ou marketing citando CRM no texto. Gatilho de vaga só entra em sequência de vaga depois de checado (título + link + data); senão a conta vai pra sequência de fit. Vaga é sinal perecível.
- [regra] **Em lookalike de marca de consumo, o falso positivo nº 1 é a indústria com marca forte que só vende pra distribuidor ou varejo.** Sem checkout próprio não há base própria a operar.
- [regra] **Agência é o falso positivo nº 1 em listas com sinal de CRM:** abre vaga de CRM pra entregar ao cliente, não pra operar base própria. É parceiro, não comprador.
- [regra] **O Apollo erra com frequência:** descrição colada na empresa errada, setor errado, homônimo. Resolver o negócio real com evidência antes de confiar no seed.
- [regra] **Ordem de importância:** lista certa (40%), oferta específica (40%), copy (20%). Um sinal escolhe o momento, não as palavras: email genérico bem cronometrado continua genérico.
- [regra] **Fato, hipótese, desconhecido.** "Abriu vaga de CRM" é fato. "Está pronto pra comprar" é hipótese. O que falta pra confirmar vira pergunta de discovery, não veredito.
- [regra] **Uma vertical por vez.** Primeiro lote no segmento que as contas da casa já provam; segundo segmento só com o primeiro medido.
- [regra] **Nunca reabordar em silêncio.** Quem recebeu e não respondeu sai da automação. Retoque só manual, com outro ângulo e sinal novo.

## Entregabilidade

- [regra] **Teto de bounce de 2% por rodada.** Passou disso, a sequência pausa até a lista ser revista. Antes do envio: só email `verified`, nenhuma caixa genérica (`contato@`, `vendas@`), SPF, DKIM e DMARC válidos no domínio remetente. Procedência: decisão do mantenedor em 2026-09-29, alinhada ao padrão de mercado (2%), mais rígido que os 3% usados antes.
- [regra] **No máximo 30 envios por caixa por dia.** O limite de cada caixa fica no `cliente.yaml`.
- [regra] **Domínio secundário é o padrão.** Enviar pelo domínio principal do cliente só por decisão explícita dele, registrada no `cliente.yaml`, porque é a reputação do domínio que ele usa com os próprios clientes que fica em jogo.

## Mensagem por nível do contato

- [hipótese] **O decisor e quem opera leem emails diferentes.** Decisor (dono, C-level): 2 a 3 frases, dor em receita, risco ou posição; problema operacional faz ele delegar o email. Quem opera (CRM, lifecycle, e-commerce): 3 a 4 frases, dor em tempo e trabalho manual; ROI abstrato não ressoa em quem não assina o orçamento. Aplicada no D1 como variante por nível (`schemas/sequencia-email.schema.md`). Procedência: adaptada de um playbook público de mensagem ATL/BTL, 2026-09-29; testar comparando reply por nível.
