# Schema: sequência de email

Arquivo `rodadas/<rodada>/04-sequencia-email.md`, escrito pela `copy-email`, revisado pela `juiz-de-copy` e aprovado no gate H2. É lido por `scripts/render_email.py` (QA), pela `qa-lancamento` e pela `apollo-sequence-builder` (que cria os passos no Apollo). Por isso o formato é fixo.

## Estrutura

```markdown
# Sequência · <rodada> · <segmento> · <oferta>

Versão da máquina: <AAAA-MM-DD> · juiz: <nota média> · rodadas de revisão: <n>

## Variáveis

| variável | coluna | fallback |
|---|---|---|
| first_name | primeiro_nome | tudo bem |
| company | company_name | vocês |

## D1

Assunto: <assunto>

<corpo>

## D4

Assunto: (mesma thread)

<corpo>

## D8

Assunto: (mesma thread)

<corpo>

## D13

Assunto: <assunto novo ou (mesma thread)>

<corpo>
```

## Regras de formato

- **Quatro toques, nesta ordem:** `## D1`, `## D4`, `## D8`, `## D13`. O número é o dia da sequência; a `apollo-sequence-builder` calcula o intervalo entre passos a partir dele (3, 4 e 5 dias).
- **Variante por nível do contato (opcional):** um toque pode ser escrito duas vezes, `## D1 · decisor` e `## D1 · champion`, no lugar de `## D1`. Decisor recebe mensagem de dono (2 a 3 frases, receita, risco, posição); champion recebe mensagem de quem opera (3 a 4 frases, tempo, trabalho manual, dor do dia a dia). O contato com `papel = decisor` recebe a primeira; `champion` e `influenciador`, a segunda. Toque com variante tem as duas e nenhuma versão simples. Os demais toques ficam compartilhados. A `apollo-sequence-builder` cria uma sequência no Apollo por nível. [hipótese, 2026-09-29: testar na r1 se o decisor responde mais à versão de dono]
- **Primeira linha de cada toque:** `Assunto: <texto>`. `Assunto: (mesma thread)` responde na thread do toque anterior.
- **Corpo:** tudo depois da linha de assunto até o próximo `## `. Parágrafos separados por linha em branco. Sem Markdown dentro do corpo (sem negrito, lista ou link em sintaxe Markdown); URL, quando permitida, vai crua.
- **Variáveis:** `{{nome}}`, só as declaradas na tabela `## Variáveis`. `coluna` é a coluna de `03-contatos.csv` (ou do veredito da conta) que alimenta a variável. `fallback` é o texto que entra quando a coluna está vazia, e a frase precisa ler bem com ele.
- **Spintax:** `{opção a|opção b}`, só em saudação e transições. Nunca em frase com fato ou prova. O render usa a primeira opção por padrão.
- **Sem travessão (—).** Acentuação completa.
- **Seção opcional `## Notas do juiz`** no fim do arquivo: o que a `juiz-de-copy` não conseguiu consertar. O render ignora essa seção.

## Variáveis que o Apollo conhece

A `apollo-sequence-builder` traduz cada variável pra merge tag do Apollo. Variáveis padrão: `first_name`, `last_name`, `company` (`{{company}}` no Apollo), `title`. Qualquer outra variável (ex.: `primeira_frase`) vira campo custom de contato no Apollo, criado antes do import. Contato com a coluna vazia recebe o fallback no próprio campo antes de subir, pra que o Apollo nunca envie merge vazio.
