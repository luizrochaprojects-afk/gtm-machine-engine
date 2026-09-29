# Gabarito de ICP: <nome do cliente>

Versão <n> · <AAAA-MM-DD> · aprovado no H0 em <AAAA-MM-DD> por <papel>
Ofertas cobertas: <id da oferta>, <id da oferta>

Formato em `../../schemas/gabarito.schema.md`. As quatro seções são obrigatórias: sem elas a `montar-tam` e a `validar-lista` não aceitam o gabarito.

## Definição em uma frase

<O padrão por trás do ICP, não a lista de verticais.>

## 1. Fit

### Audiência comum

| id | nome | papel | como verificar | fonte aceita | peso | validade |
|---|---|---|---|---|---|---|
| | | | | | | |

### Oferta <id>

| id | nome | papel | como verificar | fonte aceita | peso | validade |
|---|---|---|---|---|---|---|
| | | | | | | |

## 2. Sinais de prontidão

Teto de bônus dos sinais: <padrão +20>

| id | nome | papel | como verificar | fonte aceita | peso | validade |
|---|---|---|---|---|---|---|
| | | sinal | | | | |

## 3. Critérios de discovery

| id | nome | papel | como verificar | fonte aceita | peso | validade |
|---|---|---|---|---|---|---|
| | | pergunta | | | | |

## 4. Desqualificadores

### Duros

| id | nome | papel | como verificar | fonte aceita | peso | validade |
|---|---|---|---|---|---|---|
| | | duro | | | | |

### De validação

| id | nome | papel | como verificar | fonte aceita | peso | validade |
|---|---|---|---|---|---|---|
| | | validacao | | | | |

## Score e vereditos

| Score | Veredito | O que acontece |
|---|---|---|
| ≥ 80 | `P0` | entra na rodada já; revisão humana no H1 |
| 60 a 79 | `lista` | entra na rodada |
| 40 a 59 | `nutrir` | sem outbound |
| < 40 | `fora` | não entra |

## Tier e trilha

- **Tier:** <como sai do score e do critério `dimensiona`>
- **Trilha:** <como se decide a oferta de cada conta; `incerta` quando só a reunião decide>

## Persona por porte

Personas no `cliente.yaml`. Exceções:

-
