# Schema: gabarito de ICP

O gabarito é o arquivo `estrategia/gabarito-icp.md` do workspace. Diz, de forma verificável, quem é conta boa pra cada oferta do cliente. É lido pela `montar-tam` (vira filtro de busca) e pela `validar-lista` (vira critério de veredito). É aprovado no gate H0 (e C1 no serviço).

Um gabarito sem as quatro seções abaixo não é aceito pelas skills.

## Cabeçalho

```markdown
# Gabarito de ICP: <nome do cliente>

Versão <n> · <AAAA-MM-DD> · aprovado no H0 em <AAAA-MM-DD> por <papel>
Ofertas cobertas: <id da oferta>, <id da oferta>
```

## Definição em uma frase

Um parágrafo que diz o padrão por trás do ICP, não a lista de verticais. Exemplo fictício: "Negócio B2C em que a segunda compra define a economia, com base própria grande pro porte, que já gasta com CRM ou mídia e decide sem comitê."

## As quatro seções obrigatórias

### 1. Fit

Critérios que dizem se a conta pode comprar. Divididos em:

- **Audiência comum:** vale pra todas as ofertas.
- **Subcritério por oferta:** uma subseção `#### Oferta <id>` pra cada oferta, com o que muda (ex.: porte, operação própria, tipo de dor visível de fora).

Cada critério de fit tem um **papel**:

| Papel | Significado | Efeito no veredito |
|---|---|---|
| `gate` | Sem ele a conta está fora | ausente ⇒ `fora`, sem exceção |
| `qualifica` | Soma pontos de fit | entra no score |
| `dimensiona` | Diz o tamanho da oportunidade | entra no score e no tier |

### 2. Sinais de prontidão

Fatos datados que dizem que a conta está pronta agora (vaga, troca de plataforma, captação, data forte da vertical). Aceleram, nunca qualificam: conta sem sinal e com fit continua conta. Cada sinal tem **validade** (quantos dias o fato vale) e **bônus** no score.

### 3. Critérios de discovery

O que não dá pra saber de fora e vira pergunta na primeira reunião. Cada item diz a pergunta e o que a resposta muda (troca de trilha, desqualificação, tier).

### 4. Desqualificadores

- **Duros:** tiram a conta da lista na hora (ex.: agência, compra única, enterprise com comitê). Marcam `is_anti_icp`.
- **De validação:** só aparecem na pesquisa e rebaixam o veredito (ex.: marca que só vende pra distribuidor, domínio do Apollo que é de outra empresa).

## Formato de cada critério

Todo critério, em qualquer seção, é uma linha de tabela com estas colunas:

| Coluna | O que vai | Exemplo fictício |
|---|---|---|
| `id` | Código curto, único no gabarito | `F1` |
| `nome` | O critério em poucas palavras | Recompra ou assinatura |
| `papel` | `gate`, `qualifica`, `dimensiona` (fit); `sinal` (prontidão); `pergunta` (discovery); `duro` ou `validacao` (desqualificador) | `gate` |
| `como verificar` | O passo concreto que o agente faz | Achar no site página de assinatura, clube, "compre de novo" ou plano mensal |
| `fonte aceita` | De onde a evidência pode vir | site da conta (checkout, página de assinatura); review público; notícia datada |
| `peso` | Pontos no score (fit e sinal); vazio nos outros | 30 |
| `validade` | Só pra sinal: dias que o fato vale | 90 |

Exemplo de tabela:

```markdown
| id | nome | papel | como verificar | fonte aceita | peso | validade |
|---|---|---|---|---|---|---|
| F1 | Recompra ou assinatura | gate | Página de assinatura, clube ou plano mensal no site | site da conta | 30 | |
| F2 | Já gasta com CRM ou mídia | qualifica | Ferramenta de CRM no HTML ou pixel de mídia | HTML do site; vaga pública | 25 | |
| S1 | Vaga de CRM aberta | sinal | Vaga com título de CRM ou lifecycle, link e data | página de vaga | 10 | 45 |
```

## Score e vereditos

O gabarito declara as faixas. Padrão do motor, que o gabarito pode mudar:

| Score | Veredito | O que acontece |
|---|---|---|
| ≥ 80 | `P0` | entra na rodada já; revisão humana no H1 |
| 60 a 79 | `lista` | entra na rodada |
| 40 a 59 | `nutrir` | sem outbound |
| < 40 | `fora` | não entra |

Regras fixas: desqualificador duro ou `gate` ausente ⇒ `fora` e score abaixo de 40. Bônus de sinais tem teto declarado no gabarito (padrão: +20).

## Tier e trilha

- **Tier** (`1`, `2`, `3`): o gabarito diz como sai do score e do critério `dimensiona` (ex.: tier 1 = P0 com base grande).
- **Trilha:** o gabarito diz como se decide a oferta de cada conta (pela operação da conta, pelo tipo de dor visível de fora, ou `incerta` quando só a reunião decide). Valores: id de oferta do `cliente.yaml`, `ambas` ou `incerta`.

## Persona por porte

Referência ao campo `personas` do `cliente.yaml`. O gabarito só registra exceções (ex.: conta sem título de CRM detectável não é desqualificada; o alvo vira o decisor).
