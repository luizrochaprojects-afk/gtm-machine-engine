# Adaptador: Google Sheets (ledger)

Como a máquina lê e escreve o ledger. O ledger é uma planilha Google Sheets por cliente, com o ID em `ledger_id` no `cliente.yaml`. Abas, colunas, dono de cada coluna e fórmulas estão em `schemas/ledger.schema.md`. Este arquivo diz como usar o conector sem estragar o que o humano escreveu.

Toda skill que toca o ledger lê este arquivo antes.

Regras testadas no ledger do cliente zero:

- escrever só em colunas da máquina preserva as colunas humanas da mesma linha;
- valor com prefixo `'` mantém zero à esquerda e fica como texto;
- fórmula com `,` falha em planilha com localidade pt_BR; com `;` funciona;
- `append_values` cria linha nova no fim da tabela sem tocar nas outras.

## Ferramentas do conector

Nomes como aparecem na sessão. Os parâmetros são os do conector.

| Ferramenta | Pra quê | Parâmetros principais |
|---|---|---|
| `mcp__claude_ai_Google_Sheets__get_spreadsheet` | Abas, `sheetId`, localidade, número de linhas | `spreadsheetId`, `fields` (ex.: `["properties.locale", "sheets.properties.sheetId", "sheets.properties.title"]`) |
| `mcp__claude_ai_Google_Sheets__get_values` | Ler cabeçalho, coluna-chave, linha ou aba inteira | `spreadsheetId`, `range` (ex.: `contas!1:1`, `contas!A:A`, `contas!A12:P12`) |
| `mcp__claude_ai_Google_Sheets__update_values` | Escrever valores numa linha que já existe | `spreadsheetId`, `range`, `values` (matriz) |
| `mcp__claude_ai_Google_Sheets__append_values` | Linha nova no fim da tabela | `spreadsheetId`, `range` (sempre `<aba>!A1`), `values` |
| `mcp__claude_ai_Google_Sheets__update_formulas` | Escrever fórmulas | `spreadsheetId`, `range`, `formulas` (matriz de textos começando com `=`) |
| `mcp__claude_ai_Google_Sheets__update_spreadsheet` | Formatação e estrutura (batchUpdate): `addSheet`, `updateSheetProperties`, `repeatCell`, `updateSpreadsheetProperties` | `spreadsheetId`, `requests` |
| `mcp__claude_ai_Google_Sheets__insert_dimension` | Inserir coluna ou linha | `spreadsheetId`, `sheetId`, `dimension`, `startIndex`, `endIndex` |
| `mcp__claude_ai_Google_Sheets__batch_clear_values` | Limpar intervalos | `spreadsheetId`, `ranges` |
| `mcp__claude_ai_Google_Sheets__copy_sheet_to_another_spreadsheet` | Copiar uma aba pra outra planilha | ver o conector |
| `mcp__claude_ai_Google_Drive__create_file` | Criar a planilha do ledger | `title`, `contentMimeType`, `textContent` |
| `mcp__claude_ai_Google_Drive__copy_file` | Copiar um ledger-modelo vazio | ver o conector |
| `mcp__claude_ai_Google_Drive__share_file` | Dar acesso ao operador e ao aprovador | ver o conector |

O conector grava como se a pessoa tivesse digitado na célula. Por isso `'` vira texto e `=` vira fórmula. Consequências nas regras abaixo.

## Regras de leitura

1. **Achar a coluna pelo nome do cabeçalho, nunca pela letra.** Ler `<aba>!1:1`, montar o mapa nome → letra e usar o mapa. A única exceção são as fórmulas da aba `rodadas`, que citam letras fixas (ver schema).
2. **Conferir o cabeçalho contra o schema.** Se faltar coluna, sobrar coluna ou a ordem mudar numa coluna citada por fórmula (`contas!C`, `contatos!J`, `toques!G`, `toques!I`, `reunioes!E`), parar e avisar o operador. Não escrever nada até ele resolver.
3. **Achar a linha pela chave.** Ler só a coluna-chave (`contas!A:A` pra `dominio`, `contatos!A:A` pra `contato_id`, e assim por diante), achar o número da linha e só então ler a linha inteira. Chave normalizada antes de comparar: domínio por `scripts/normalize_domain.py`, email em caixa baixa.
4. **Chave repetida é erro.** Se a mesma chave aparece em duas linhas de `contas`, `contatos`, `supressao` ou `reunioes`, não escolher uma. Avisar o operador com os números das linhas.
5. **`get_values` devolve o valor exibido.** O `'` não aparece na leitura, e fórmula chega como resultado. Pra comparar, tirar o `'` do valor que se vai escrever.
6. **Ler as colunas humanas antes de agir.** `nao_abordar = sim` em `contas` ou `contatos` tira a conta ou o contato da rodada, sem exceção. A máquina não escreve rodada nova nessa linha; lista o caso no relatório da skill.

## Regras de escrita

1. **Ler a linha imediatamente antes de escrever.** Nada de reaproveitar uma leitura de minutos atrás: o humano pode ter mudado a linha no meio. Ler, comparar com o que se vai escrever, escrever.
2. **Só colunas de cabeçalho cinza.** Colunas amarelas são do humano: a máquina lê, nunca escreve, nem com valor vazio. Em todas as abas as colunas cinza vêm primeiro e as amarelas no fim; o intervalo de escrita termina na última coluna cinza (ex.: `contas!A12:M12`).
3. **Texto com prefixo `'`.** Domínio, `contato_id`, `toque_id`, `reuniao_id`, IDs de ferramenta, telefone e toda data (`'2026-10-02`, `'2026-10-02 09:30`). Também todo texto que comece com `=`, `+`, `-` ou `@` (ex.: uma primeira frase que começa com "+40%"), senão vira fórmula ou número.
4. **Número sem `'`.** Só `score` e `tier` são números.
5. **Linha nova com `append_values`,** com `range` = `<aba>!A1` e só as colunas cinza, na ordem do cabeçalho. Nunca escrever linha nova num intervalo fixo (ex.: `contas!A200`): se alguém inseriu linhas, sobrescreve dado. Não deixar linha vazia no meio da tabela: o `append_values` procura o fim da tabela a partir de A1 e uma linha vazia pode fazer a linha nova cair no lugar errado. Depois de anexar, ler a coluna-chave de novo e conferir que a chave aparece uma vez só.
6. **Atualizar linha existente com `update_values`** no intervalo exato da linha achada pela chave, só nas colunas cinza que mudam, mais `atualizado_em`. Conta que volta numa rodada nova tem a linha atualizada, não duplicada.
7. **Aba `toques` nunca se edita.** Evento novo é linha nova. Correção também é linha nova, com `nota` explicando (a nota é coluna humana: pedir ao operador).
8. **Fórmulas só com `update_formulas`,** com `;` como separador de argumento em localidade pt_BR. Antes da primeira fórmula da sessão, ler `properties.locale` com `get_spreadsheet`. Se não for `pt_BR`, parar e avisar: as fórmulas do schema estão escritas pra pt_BR.
9. **Lotes.** Até 500 linhas por chamada de `append_values`. Lista maior vai em várias chamadas, conferindo o total no fim.
10. **Não limpar dado.** `batch_clear_values` e `insert_dimension` não são usados em aba com dado, a não ser com pedido explícito do operador na conversa. Mudar coluna é mudança de schema: vai pro `CHANGELOG.md`.

### Linha nova na aba `rodadas`

1. `append_values` em `rodadas!A1` com as colunas A a E: `rodada_id`, `segmento`, `oferta`, `canais`, `'<inicio>`.
2. Ler `rodadas!A:A` e achar o número da linha (`N`) pela `rodada_id`.
3. `update_formulas` em `rodadas!FN:KN` com as fórmulas do schema, trocando `N`:

```
=COUNTIF(contas!C:C;AN)
=COUNTIF(contatos!J:J;AN)
=COUNTIFS(toques!G:G;AN;toques!I:I;"enviado")
=COUNTIFS(toques!G:G;AN;toques!I:I;"resposta")
=COUNTIF(reunioes!E:E;AN)
=IF(GN=0;0;JN/GN)
```

4. Ler `rodadas!AN:KN` e conferir que nenhuma célula voltou com erro (`#ERROR!`, `#NAME?`, `#REF!`).

L e M (`decisao_h3`, `nota`) são humanas. A `qa-lancamento` pede ao operador que escreva a decisão ali; a máquina não escreve.

## Snapshot no fim da rodada

No fim de cada rodada, cada aba vira um CSV em `rodadas/<rodada>/ledger/<aba>.csv` no workspace (`contas.csv`, `contatos.csv`, `toques.csv`, `supressao.csv`, `reunioes.csv`, `rodadas.csv`; a `leia-me` não entra).

1. `get_values` com `<aba>!A:Z`, cabeçalho incluído, colunas cinza e amarelas (o snapshot guarda também o que o humano escreveu).
2. Gravar em UTF-8, separador vírgula, aspas onde precisar. Valores como a planilha exibe (sem `'`; fórmula como resultado).
3. Conferir que o número de linhas do CSV bate com o da aba.

A pasta `rodadas/*/ledger/` está no `.gitignore` do workspace: tem dado pessoal de contato. O snapshot é a foto que o `loop-de-licoes` e o `suppress.py` leem.

## Criar a planilha do zero

Quem faz: a `setup-workspace`. Resultado: planilha "GTM Machine · Ledger · <nome do cliente>" com 7 abas na ordem `leia-me`, `contas`, `contatos`, `toques`, `supressao`, `reunioes`, `rodadas`.

1. **Criar.** `create_file` com `title` = `GTM Machine · Ledger · <nome>` e `contentMimeType` = `application/vnd.google-apps.spreadsheet`, sem conteúdo (funciona: testado em 2026-09-29). Se o conector recusar sem conteúdo, mandar `textContent` com uma linha qualquer e `contentMimeType` = `text/csv` (o Drive converte pra planilha). Guardar o ID devolvido: vai pro `ledger_id`.
   - Alternativa: se o operador tiver um ledger-modelo vazio no Drive, `copy_file` dele e pular pro passo 6 pra conferir.
2. **Localidade e fuso.** `update_spreadsheet` com `updateSpreadsheetProperties`: `properties` = `{"locale": "pt_BR", "timeZone": "<fuso da janela_envio ou America/Sao_Paulo>"}`, `fields` = `"locale,timeZone"`.
3. **Abas.** `get_spreadsheet` pra pegar o `sheetId` da primeira aba. Numa chamada de `update_spreadsheet`: `updateSheetProperties` renomeando a primeira aba pra `leia-me` (`fields: "title"`) e seis `addSheet` com `properties.title` = `contas`, `contatos`, `toques`, `supressao`, `reunioes`, `rodadas` e `index` 1 a 6. Ler de novo os `sheetId` gerados.
4. **Cabeçalhos.** `update_values` na linha 1 de cada aba com os nomes das colunas do schema, na ordem do schema.
5. **Cores, negrito e primeira linha congelada.** Uma chamada de `update_spreadsheet` com, por aba:
   - `repeatCell` nas colunas cinza da linha 1: `range` = `{"sheetId": <id>, "startRowIndex": 0, "endRowIndex": 1, "startColumnIndex": 0, "endColumnIndex": <última cinza + 1>}`, `cell.userEnteredFormat` = `{"backgroundColor": {"red": 0.898, "green": 0.898, "blue": 0.898}, "textFormat": {"bold": true}}`, `fields` = `"userEnteredFormat.backgroundColor,userEnteredFormat.textFormat.bold"`.
   - `repeatCell` nas colunas amarelas da linha 1 com `backgroundColor` = `{"red": 1, "green": 0.949, "blue": 0.6}`, mesmo `textFormat` e `fields`.
   - `updateSheetProperties` com `gridProperties.frozenRowCount` = 1 e `fields` = `"gridProperties.frozenRowCount"`.
   - **Máscara de campos:** sempre caminhos completos separados por vírgula. A forma com parênteses (`userEnteredFormat(backgroundColor,textFormat.bold)`) é recusada pelo conector com `Invalid field` (testado em 2026-09-29).
   - Na aba `rodadas`, `repeatCell` em K2:K1000 com `numberFormat` `{"type": "PERCENT", "pattern": "0%"}` e `fields` = `"userEnteredFormat.numberFormat"`.

   Colunas por aba (índice começa em 0; o fim é exclusivo):

   | Aba | Cinza (máquina) | Amarelo (humano) |
   |---|---|---|
   | `contas` | A a M (0 a 13) | N a P (13 a 16) |
   | `contatos` | A a K (0 a 11) | L a M (11 a 13) |
   | `toques` | A a J (0 a 10) | K a L (10 a 12) |
   | `supressao` | A a E (0 a 5) | F a G (5 a 7) |
   | `reunioes` | A a F (0 a 6) | G a K (6 a 11) |
   | `rodadas` | A a K (0 a 11) | L a M (11 a 13) |

   Cores exatas: cinza `#E5E5E5` (RGB 0.898 / 0.898 / 0.898); amarelo `#FFF299` (RGB 1 / 0.949 / 0.6).
6. **Aba `leia-me`.** `update_values` em `leia-me!A1` com:

   | Linha | A | B |
   |---|---|---|
   | 1 | `Ledger da GTM Machine · <nome do cliente>` | |
   | 2 | `Memória da máquina: quem foi abordado, quando, por qual canal, o que respondeu e quem não pode ser abordado.` | |
   | 4 | `Legenda` | |
   | 5 | `máquina` | `Cabeçalho cinza: a máquina escreve. Não editar à mão.` |
   | 6 | `humano` | `Cabeçalho amarelo: operador e cliente editam. A máquina só lê.` |
   | 8 | `Aba` | `O que guarda` |
   | 9 | `contas` | `Uma linha por empresa abordada ou avaliada.` |
   | 10 | `contatos` | `Uma linha por pessoa.` |
   | 11 | `toques` | `Uma linha por evento: envio, aceite, resposta, bounce, optout.` |
   | 12 | `supressao` | `Domínios, emails e perfis que nunca entram numa rodada.` |
   | 13 | `reunioes` | `Reuniões marcadas e o resultado devolvido pelo vendedor.` |
   | 14 | `rodadas` | `Uma linha por rodada, com o funil em fórmulas.` |
   | 16 | `Regra fixa` | `Nenhuma automação reenvia mensagem a quem recebeu e não respondeu. "sim" em nao_abordar tira a conta ou o contato de qualquer rodada futura.` |

   Pintar A5 de cinza e A6 de amarelo com `repeatCell` (mesmas cores). Negrito em A1, A4, A8:B8 e A16.
7. **Conferir.** `get_spreadsheet` com `fields` = `["properties.title", "properties.locale", "sheets.properties.title", "sheets.properties.index", "sheets.properties.gridProperties.frozenRowCount"]` e `get_values` da linha 1 de cada aba. Tudo tem que bater com o schema.
8. **Acesso.** `share_file` só pro operador e pro aprovador, como editores. Nunca "qualquer pessoa com o link": o ledger tem dado pessoal de contato.

## Em caso de erro

1. **Não sobrescrever e não tentar de novo às cegas.** Uma escrita que deu erro pode ter sido aplicada em parte.
2. **Reler** o intervalo que ia ser escrito e a coluna-chave. Descobrir o que entrou e o que não entrou.
3. **Completar só o que falta,** seguindo as regras de escrita. Se a leitura mostrar linha duplicada ou valor inesperado numa coluna cinza, não corrigir sozinho: parar.
4. **Avisar o operador** com a aba, as linhas, o que se ia escrever e o que está lá agora. Registrar o caso no relatório da skill.
5. **Conector fora do ar ou sem permissão:** parar a etapa que escreve no ledger. A skill pode seguir gerando os arquivos da rodada, mas marca "ledger pendente" no relatório e o `qa-lancamento` não aprova H3 com ledger pendente.

## Armadilhas

- **Planilha em inglês.** Ledger criado fora da `setup-workspace` pode vir com localidade `en_US`, e aí as fórmulas com `;` quebram. Conferir `properties.locale` antes de escrever fórmula.
- **Data vira número.** `2026-10-02` sem `'` vira data do Sheets e volta formatada diferente na leitura. Sempre `'`.
- **Domínio com zero ou hífen no começo** e telefone perdem formato sem `'`.
- **Texto que começa com `+` ou `=`** vira fórmula. Primeira frase, fato e nota passam pela regra do `'`.
- **Linha vazia no meio** faz o `append_values` escrever no lugar errado. Se o operador apagou linhas, pedir que remova a linha inteira, não só o conteúdo.
- **Filtro ativo na planilha** não muda o que a API lê, mas confunde o operador ao conferir. Avisar se ele disser que "a linha sumiu".
- **Coluna humana vazia não é convite.** Mesmo em branco, a máquina não escreve nela.
