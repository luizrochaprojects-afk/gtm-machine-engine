# Diff · <rodada> · <gate> · <peça>

Arquivo: `aprendizado/diffs/<rodada>-<gate>-<peça>.md`. Um arquivo por gate e por peça. Escrito pela skill que gerou a peça (bloco da máquina) e completado no gate (bloco aprovado e notas). Depois de fechado, não se edita: correção posterior vira diff novo.

## Cabeçalho

| Campo | Valor |
|---|---|
| Rodada | `<AAAA-MM-DD-rN-segmento-oferta>` |
| Gate | `H0`, `H1`, `H2` ou `H3` |
| Peça | `estrategia`, `lista`, `email`, `syndie`, `qa` ou outra |
| Data | `<AAAA-MM-DD>` |
| Skill de origem | `<nome da skill>` |
| Versão do motor | `<x.y.z>` |
| Aprovado por | `<papel e nome, do cliente.yaml>` |
| Resultado | `aprovado sem edição`, `aprovado com edição` ou `reprovado` |

## Versão da máquina

A saída exata da skill, como chegou ao gate. Texto colado inteiro ou, pra listas e planilhas, a tabela das linhas revisadas (ex.: domínio, veredito da máquina, score).

```
<conteúdo>
```

## Versão aprovada

O que foi efetivamente aprovado ou enviado. Mesmo formato do bloco anterior, pra permitir comparação linha a linha. Se aprovado sem edição, escrever "igual à versão da máquina".

```
<conteúdo>
```

## Notas do operador

Por que mudou. Uma linha por mudança relevante, no formato:

- `<o que mudou>` · `<por quê, nas palavras de quem aprovou>`

Em lista (H1): uma linha por veredito alterado, com domínio, veredito da máquina → veredito aprovado e motivo.

## Métrica

| Campo | Valor |
|---|---|
| Unidades da máquina | `<frases ou linhas>` |
| Unidades preservadas sem edição | `<n>` |
| % mantido | `<preservadas ÷ máquina>` |

Preenchido pela `loop-de-licoes`; alimenta `aprendizado/ciclos.md`.
