# Ciclos: quanto da máquina passa sem edição

Uma linha por skill, gate e rodada. Mostra se a máquina está aprendendo: o % mantido sem edição tem que subir de rodada para rodada. Quem escreve: o `loop-de-licoes`, a partir do bloco "Métrica" de cada diff em `aprendizado/diffs/`.

## Como calcular

- **Texto** (estratégia no H0, email e prompt da Syndie no H2): frases preservadas ÷ frases da máquina. Frase preservada é a que chega à versão aprovada igual, letra por letra, ignorando só espaço em branco. Frase cortada ou reescrita conta como editada. Frase que o humano acrescentou não entra na conta.
- **Lista** (H1): vereditos mantidos ÷ vereditos revisados. Só contam as contas que o humano revisou (incertas e P0). Veredito, trilha ou tier trocado conta como editado.
- **Silêncio = 100%.** Gate aprovado sem nenhuma mudança conta como 100% mantido. O diff registra "aprovado sem edição".
- **Reprovado = 0%.** Peça reprovada e refeita do zero conta 0% e a nova versão entra numa linha própria.
- Arredondar para número inteiro. Anotar o total entre parênteses (ex.: `78% (18/23)`).

## Tabela

| rodada | skill | gate | % mantido sem edição | data |
|---|---|---|---|---|
| | | | | |
