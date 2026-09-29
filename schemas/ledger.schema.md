# Schema: ledger

O ledger é uma planilha Google Sheets por cliente. É a fonte da verdade da máquina: quem foi abordado, quando, por qual canal, o que respondeu e quem não pode ser abordado. Apollo e Syndie executam; o CRM do cliente recebe cópia pelo adaptador (`adapters/<crm>/`).

O ID da planilha fica em `ledger_id` no `cliente.yaml`. O ledger tem dado pessoal de contato: fica no Drive com acesso restrito, nunca no git.

Descrito a partir do ledger do cliente zero, criado e testado na construção da v0.1. Regras de leitura e escrita pela API em `adapters/google-sheets/README.md`.

## Convenções

- **Dono da coluna pela cor do cabeçalho.** Cinza (`#E5E5E5`, RGB 0.898) = máquina: as skills escrevem, ninguém edita à mão. Amarelo (`#FFF299`, RGB 1 / 0.949 / 0.6) = humano: operador e cliente editam, a máquina só lê.
- **A máquina lê a linha imediatamente antes de escrever** e escreve só nas colunas cinza da linha.
- **Texto com prefixo `'`:** domínio, IDs, telefone, data e qualquer valor com zero à esquerda ou que o Sheets poderia converter.
- **Datas como texto** no formato `AAAA-MM-DD` (ou `AAAA-MM-DD HH:MM` quando a hora importa).
- **Linha nova com `append_values`**, nunca escrevendo por cima de intervalo fixo.
- **Fórmulas em localidade pt_BR usam `;`** como separador de argumento.
- **Chaves:** `dominio` normalizado por `scripts/normalize_domain.py` (sem `http`, `www`, barra final; caixa baixa). `contato_id` = `<dominio>:<slug-do-nome>` (ex.: `acme.com.br:ana-souza`). `toque_id` = `<contato_id>:<rodada>:<passo>:<evento>`. `reuniao_id` = `<dominio>:<AAAA-MM-DD>`.
- **Valores fixos** (listas fechadas) estão marcados em cada coluna. Qualquer outro valor é erro da skill.
- **Snapshot:** no fim de cada rodada, cada aba é exportada em CSV pra `rodadas/<rodada>/ledger/<aba>.csv`, como foto pro loop de lições.

## Aba `leia-me`

Texto livre, sem colunas. Contém: título "Ledger da GTM Machine · <nome do cliente>", uma frase sobre o que o ledger é, a legenda das cores (célula de exemplo pintada de cinza e de amarelo com a explicação), a tabela "Aba × O que guarda" e a regra fixa: "Nenhuma automação reenvia mensagem a quem recebeu e não respondeu. "sim" em nao_abordar tira a conta ou o contato de qualquer rodada futura."

## Aba `contas`

Uma linha por empresa. Chave: `dominio`. Uma conta que volta em outra rodada tem a linha atualizada, não duplicada.

| Coluna | Dono | Formato | Valores | Quem escreve |
|---|---|---|---|---|
| `dominio` | máquina | texto `'` | domínio normalizado | `registrar-ledger` |
| `empresa` | máquina | texto | nome canônico | `registrar-ledger` |
| `rodada` | máquina | texto | nome da rodada mais recente | `registrar-ledger` |
| `segmento` | máquina | texto | slug do segmento | `registrar-ledger` |
| `trilha` | máquina | texto | id de oferta do `cliente.yaml`, `ambas` ou `incerta` | `registrar-ledger` |
| `veredito` | máquina | texto | `P0`, `lista`, `nutrir`, `fora` | `registrar-ledger` |
| `tier` | máquina | texto | `1`, `2`, `3` | `registrar-ledger` |
| `score` | máquina | número | 0 a 100 | `registrar-ledger` |
| `tecnografia` | máquina | texto | ferramentas separadas por `; ` | `registrar-ledger` |
| `fato_abordagem` | máquina | texto | fato que sustenta a primeira frase | `registrar-ledger` |
| `fonte_url` | máquina | texto | URL do fato | `registrar-ledger` |
| `estagio` | máquina | texto | `Working`, `Respondeu`, `Reuniao`, `Oportunidade`, `Cliente`, `Perdida`, `Nutrir` | `registrar-ledger` (Working); demais estágios pela triagem de respostas (S2) |
| `atualizado_em` | máquina | texto `'` | `AAAA-MM-DD` | toda skill que escreve na linha |
| `nao_abordar` | humano | texto | vazio ou `sim` | operador ou cliente |
| `dono` | humano | texto | quem cuida da conta | operador ou cliente |
| `nota` | humano | texto | livre | operador ou cliente |

## Aba `contatos`

Uma linha por pessoa. Chave: `contato_id`.

| Coluna | Dono | Formato | Valores | Quem escreve |
|---|---|---|---|---|
| `contato_id` | máquina | texto `'` | `<dominio>:<slug-do-nome>` | `registrar-ledger` |
| `dominio` | máquina | texto `'` | domínio normalizado | `registrar-ledger` |
| `nome` | máquina | texto | nome completo | `registrar-ledger` |
| `cargo` | máquina | texto | cargo conferido na data da rodada | `registrar-ledger` |
| `papel` | máquina | texto | `decisor`, `champion`, `influenciador` | `registrar-ledger` |
| `canal` | máquina | texto | `email`, `linkedin`, `ambos` | `registrar-ledger` |
| `email` | máquina | texto | email ou vazio | `registrar-ledger` |
| `email_status` | máquina | texto | `verified`, `likely`, `unverified`, `invalid`, `sem_email` | `registrar-ledger` |
| `linkedin_url` | máquina | texto | URL `https://www.linkedin.com/in/...` | `registrar-ledger` |
| `rodada` | máquina | texto | rodada em que entrou | `registrar-ledger` |
| `atualizado_em` | máquina | texto `'` | `AAAA-MM-DD` | toda skill que escreve na linha |
| `nao_abordar` | humano | texto | vazio ou `sim` | operador ou cliente |
| `nota` | humano | texto | livre | operador ou cliente |

## Aba `toques`

Uma linha por evento. Nunca se edita linha antiga; evento novo é linha nova. Chave: `toque_id`.

| Coluna | Dono | Formato | Valores | Quem escreve |
|---|---|---|---|---|
| `toque_id` | máquina | texto `'` | `<contato_id>:<rodada>:<passo>:<evento>` | skill que registra o evento |
| `data` | máquina | texto `'` | `AAAA-MM-DD HH:MM` | idem |
| `contato_id` | máquina | texto `'` | chave da aba `contatos` | idem |
| `dominio` | máquina | texto `'` | domínio normalizado | idem |
| `canal` | máquina | texto | `email`, `linkedin` | idem |
| `ferramenta` | máquina | texto | `apollo`, `syndie`, `gmail`, `manual` | idem |
| `rodada` | máquina | texto | nome da rodada | idem |
| `passo` | máquina | texto | `D1`, `D4`, `D8`, `D13`, `convite`, `dm1`, `dm2` | idem |
| `evento` | máquina | texto | `enviado`, `aceite`, `resposta`, `bounce`, `optout` | idem |
| `classificacao` | máquina | texto | vazio ou `positivo`, `objecao`, `agora_nao`, `pessoa_errada`, `ausente`, `bounce` | triagem de respostas (S2) |
| `respondido_por` | humano | texto | quem respondeu o prospect | operador |
| `nota` | humano | texto | livre | operador |

## Aba `supressao`

Domínios, emails e perfis que nunca entram numa rodada. Chave: `chave` + `tipo`.

| Coluna | Dono | Formato | Valores | Quem escreve |
|---|---|---|---|---|
| `chave` | máquina | texto `'` | domínio normalizado, email em caixa baixa ou URL de LinkedIn normalizada | `setup-workspace` (import inicial), `registrar-ledger` |
| `tipo` | máquina | texto | `dominio`, `email`, `linkedin` | idem |
| `motivo` | máquina | texto | `cliente`, `pipeline`, `abordado_sem_resposta`, `optout`, `negativacao`, `concorrente`, `parceiro` | idem |
| `origem` | máquina | texto | arquivo ou sistema de onde veio | idem |
| `data` | máquina | texto `'` | `AAAA-MM-DD` | idem |
| `adicionado_por` | humano | texto | quem pediu a supressão | operador ou cliente |
| `nota` | humano | texto | livre (ex.: data de liberação) | operador ou cliente |

O operador também pode acrescentar linhas à mão; a máquina trata a linha inteira como válida desde que `chave` e `tipo` estejam preenchidos.

## Aba `reunioes`

Reuniões marcadas e o resultado devolvido pelo vendedor (gate C3). Chave: `reuniao_id`.

| Coluna | Dono | Formato | Valores | Quem escreve |
|---|---|---|---|---|
| `reuniao_id` | máquina | texto `'` | `<dominio>:<AAAA-MM-DD>` | triagem de respostas (S2) ou operador |
| `dominio` | máquina | texto `'` | domínio normalizado | idem |
| `contato_id` | máquina | texto `'` | chave da aba `contatos` | idem |
| `data` | máquina | texto `'` | `AAAA-MM-DD HH:MM` | idem |
| `rodada` | máquina | texto | nome da rodada | idem |
| `trilha` | máquina | texto | id de oferta | idem |
| `conduzida_por` | humano | texto | vendedor | vendedor ou operador |
| `resultado` | humano | texto | `qualificou`, `nao_qualificou`, `proposta`, `fechou`, `nao_compareceu` | vendedor |
| `proximo_passo` | humano | texto | livre | vendedor |
| `data_resultado` | humano | texto `'` | `AAAA-MM-DD` | vendedor |
| `nota` | humano | texto | livre | vendedor ou operador |

## Aba `rodadas`

Uma linha por rodada. Os números do funil são fórmulas sobre as outras abas, nunca valores digitados. Linha nova é criada pela `registrar-ledger` (ou pelo operador ao abrir a rodada) com as colunas A a E como texto e as fórmulas abaixo, trocando `N` pelo número da linha.

| Coluna | Letra | Dono | Formato | Conteúdo |
|---|---|---|---|---|
| `rodada_id` | A | máquina | texto | nome da rodada |
| `segmento` | B | máquina | texto | slug do segmento |
| `oferta` | C | máquina | texto | id e nome da oferta |
| `canais` | D | máquina | texto | ex.: `LinkedIn + email` |
| `inicio` | E | máquina | texto `'` | `AAAA-MM-DD` |
| `contas` | F | máquina | fórmula | `=COUNTIF(contas!C:C;AN)` |
| `contatos` | G | máquina | fórmula | `=COUNTIF(contatos!J:J;AN)` |
| `toques_enviados` | H | máquina | fórmula | `=COUNTIFS(toques!G:G;AN;toques!I:I;"enviado")` |
| `respostas` | I | máquina | fórmula | `=COUNTIFS(toques!G:G;AN;toques!I:I;"resposta")` |
| `reunioes` | J | máquina | fórmula | `=COUNTIF(reunioes!E:E;AN)` |
| `reunioes_por_contato` | K | máquina | fórmula, formato % | `=IF(GN=0;0;JN/GN)` |
| `decisao_h3` | L | humano | texto | `aprovado AAAA-MM-DD HH:MM por <nome>` ou `bloqueado` |
| `nota` | M | humano | texto | livre |

A coluna `contas` conta pela rodada mais recente da conta (aba `contas`, coluna C). Conta que volta numa rodada nova passa a contar na nova.

## Ordem das colunas

A ordem acima é a ordem na planilha. Skill que lê o ledger localiza a coluna pelo nome do cabeçalho, não pela letra, exceto nas fórmulas de `rodadas`, que dependem das letras das outras abas (`contas!C`, `contatos!J`, `toques!G`, `toques!I`, `reunioes!E`). Mudar a ordem de uma coluna citada numa fórmula exige atualizar o schema, as fórmulas e o `CHANGELOG.md`.
