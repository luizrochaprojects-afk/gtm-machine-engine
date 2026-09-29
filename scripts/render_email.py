"""Renderiza a sequência de email por contato, como o prospect vai ler.

Uso:
    python scripts/render_email.py --sequencia 04-sequencia-email.md --contatos 03-contatos.csv
        [--linha N | --dominio x.com.br | --amostra 3 [--por segmento]]
        [--variante N] [--saida out.md]

Lê a sequência no formato de schemas/sequencia-email.schema.md e os contatos de
03-contatos.csv (UTF-8, com ou sem BOM). Sem seleção, renderiza todos os contatos.
--linha N pega a N-ésima linha de dados (1 = primeira depois do cabeçalho).
--amostra K pega as K primeiras linhas; com --por <coluna>, as K primeiras de cada valor.
Spintax {a|b} usa a primeira opção; --variante N usa a N-ésima (volta ao início se faltar).
Variável com a coluna vazia recebe o fallback da tabela.

Um toque pode ter duas variantes por nível do contato: `## D1 · decisor` e
`## D1 · champion`. O contato com papel decisor recebe a primeira; champion e
influenciador recebem a segunda; papel vazio recebe a de champion, com aviso.

Erros (saem com código 1): variável usada e não declarada na tabela; {{ ou }} sobrando
depois do render; travessão; sequência sem os toques D1, D4, D8 e D13; toque com só
uma das variantes, ou com variante e versão simples ao mesmo tempo.
Avisos (não falham): palavra comum sem acento que denuncia texto em ASCII.
A seção `## Notas do juiz` é ignorada. Erros e avisos vão pra stderr.
"""
from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

from normalize_domain import ler_csv, normalize_domain

TOQUES_OBRIGATORIOS = ("D1", "D4", "D8", "D13")
NIVEIS = ("decisor", "champion")
NIVEL_POR_PAPEL = {"decisor": "decisor", "champion": "champion", "influenciador": "champion"}
TITULO_TOQUE = re.compile(r"(D\d+)(?:\s*·\s*(decisor|champion))?")
TRAVESSAO = "\u2014"
VARIAVEL = re.compile(r"\{\{\s*([^{}]*?)\s*\}\}")
_OPCAO = r"(?:[^{}]|\{\{[^{}]*\}\})*"
SPINTAX = re.compile(r"(?<!\{)\{(" + _OPCAO + r"\|" + _OPCAO + r")\}(?!\})")
PALAVRAS_ASCII = re.compile(
    r"\b(voces|voce|nao|tambem|proprias?|proprios?|reguas?|ja|entao)\b", re.IGNORECASE
)
COLUNAS_DOMINIO = ("domain", "dominio")


@dataclass
class Variavel:
    nome: str
    coluna: str
    fallback: str


@dataclass
class Toque:
    nome: str
    assunto: str
    corpo: str
    nivel: str | None = None

    @property
    def rotulo(self) -> str:
        return f"{self.nome} · {self.nivel}" if self.nivel else self.nome


@dataclass
class Sequencia:
    variaveis: dict[str, Variavel] = field(default_factory=dict)
    toques: list[Toque] = field(default_factory=list)


def _celulas(linha: str) -> list[str]:
    return [c.strip() for c in linha.strip().strip("|").split("|")]


def ler_sequencia(texto: str) -> Sequencia:
    """Separa a tabela de variáveis e os toques `## D<n>`; ignora as outras seções."""
    sequencia = Sequencia()
    secoes: list[tuple[str, list[str]]] = []
    for linha in texto.splitlines():
        if linha.startswith("## "):
            secoes.append((linha[3:].strip(), []))
        elif secoes:
            secoes[-1][1].append(linha)

    for titulo, linhas in secoes:
        chave = titulo.lower()
        if chave in ("variáveis", "variaveis"):
            for linha in linhas:
                if not linha.strip().startswith("|"):
                    continue
                celulas = _celulas(linha)
                if len(celulas) < 3 or set(celulas[0]) <= set("-: "):
                    continue
                if celulas[0].lower() in ("variável", "variavel"):
                    continue
                nome = celulas[0].strip("`{} ")
                sequencia.variaveis[nome] = Variavel(nome, celulas[1].strip("` "), celulas[2])
        elif TITULO_TOQUE.fullmatch(titulo):
            conteudo = list(linhas)
            while conteudo and not conteudo[0].strip():
                conteudo.pop(0)
            assunto = ""
            if conteudo and conteudo[0].lower().startswith("assunto:"):
                assunto = conteudo.pop(0).split(":", 1)[1].strip()
            corpo = "\n".join(conteudo).strip("\n")
            nome, nivel = TITULO_TOQUE.fullmatch(titulo).groups()
            sequencia.toques.append(Toque(nome, assunto, corpo, nivel))
    return sequencia


def resolver_spintax(texto: str, variante: int = 1) -> str:
    def escolher(achado: re.Match) -> str:
        opcoes = achado.group(1).split("|")
        return opcoes[(max(variante, 1) - 1) % len(opcoes)]

    anterior = None
    while anterior != texto:
        anterior, texto = texto, SPINTAX.sub(escolher, texto)
    return texto


def valor_da_variavel(variavel: Variavel, contato: dict[str, str]) -> str:
    valor = (contato.get(variavel.coluna) or "").strip()
    return valor or variavel.fallback


def renderizar(texto: str, sequencia: Sequencia, contato: dict[str, str], variante: int) -> str:
    texto = resolver_spintax(texto, variante)

    def trocar(achado: re.Match) -> str:
        variavel = sequencia.variaveis.get(achado.group(1))
        return valor_da_variavel(variavel, contato) if variavel else achado.group(0)

    return VARIAVEL.sub(trocar, texto)


def conferir_sequencia(sequencia: Sequencia) -> list[str]:
    erros = []
    nomes = [t.nome for t in sequencia.toques]
    faltando = [t for t in TOQUES_OBRIGATORIOS if t not in nomes]
    if faltando:
        erros.append(f"sequência sem o(s) toque(s) {', '.join(faltando)} (precisa de D1, D4, D8 e D13)")
    for nome in dict.fromkeys(nomes):
        niveis = [t.nivel for t in sequencia.toques if t.nome == nome]
        if niveis != [None] and (None in niveis or sorted(niveis) != sorted(NIVEIS)):
            erros.append(f"{nome}: com variante por nível, precisa de exatamente '## {nome} · decisor' e "
                         f"'## {nome} · champion', sem versão simples")
    for toque in sequencia.toques:
        for parte, texto in (("assunto", toque.assunto), ("corpo", toque.corpo)):
            for achado in VARIAVEL.finditer(texto):
                if achado.group(1) not in sequencia.variaveis:
                    erros.append(f"{toque.rotulo} ({parte}): variável {achado.group(0)} usada e não declarada "
                                 f"na tabela ## Variáveis")
            if TRAVESSAO in texto:
                erros.append(f"{toque.rotulo} ({parte}): travessão (U+2014) no texto da sequência")
    return erros


def selecionar(linhas: list[dict[str, str]], cabecalho: list[str], args) -> tuple[list[tuple[int, dict]], str | None]:
    numeradas = list(enumerate(linhas, start=1))
    if args.linha is not None:
        if not 1 <= args.linha <= len(linhas):
            return [], f"--linha {args.linha} fora do intervalo (o CSV tem {len(linhas)} linha(s) de dados)"
        return [numeradas[args.linha - 1]], None
    if args.dominio:
        coluna = next((c for c in COLUNAS_DOMINIO if c in cabecalho), None)
        if not coluna:
            return [], "o CSV não tem coluna domain nem dominio"
        alvo = normalize_domain(args.dominio)
        achadas = [(n, l) for n, l in numeradas if normalize_domain(l.get(coluna, "")) == alvo]
        if not achadas:
            return [], f"nenhum contato com o domínio {alvo}"
        return achadas, None
    if args.amostra is not None:
        if args.por:
            if args.por not in cabecalho:
                return [], f"coluna '{args.por}' não existe no CSV"
            contagem: dict[str, int] = {}
            escolhidas = []
            for n, linha in numeradas:
                grupo = linha.get(args.por, "")
                if contagem.get(grupo, 0) < args.amostra:
                    contagem[grupo] = contagem.get(grupo, 0) + 1
                    escolhidas.append((n, linha))
            return escolhidas, None
        return numeradas[: args.amostra], None
    return numeradas, None


def toques_do_contato(sequencia: Sequencia, contato: dict[str, str]) -> tuple[list[Toque], bool]:
    """Um toque por nome, na ordem do arquivo; nas variantes, a do nível do contato.

    Devolve também se o contato caiu na variante de champion por não ter papel reconhecido."""
    papel = (contato.get("papel") or "").strip().lower()
    nivel = NIVEL_POR_PAPEL.get(papel, "champion")
    escolhidos: dict[str, Toque] = {}
    tem_variante = False
    for toque in sequencia.toques:
        if toque.nivel is None:
            escolhidos.setdefault(toque.nome, toque)
        else:
            tem_variante = True
            if toque.nivel == nivel:
                escolhidos[toque.nome] = toque
    return list(escolhidos.values()), tem_variante and papel not in NIVEL_POR_PAPEL


def cabecalho_do_contato(n: int, contato: dict[str, str]) -> str:
    nome = contato.get("nome") or contato.get("primeiro_nome") or "(sem nome)"
    partes = [nome]
    for coluna in ("cargo", "company_name"):
        if contato.get(coluna):
            partes.append(contato[coluna])
    dominio = contato.get("domain") or contato.get("dominio") or ""
    titulo = " · ".join(partes) + (f" ({dominio})" if dominio else "")
    extras = [f"linha {n} do CSV"]
    for coluna in ("segmento", "email", "papel"):
        if contato.get(coluna):
            extras.append(f"{coluna}: {contato[coluna]}")
    return f"## {titulo}\n\n{' · '.join(extras)}"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--sequencia", required=True, help="04-sequencia-email.md")
    parser.add_argument("--contatos", required=True, help="03-contatos.csv")
    grupo = parser.add_mutually_exclusive_group()
    grupo.add_argument("--linha", type=int, help="linha de dados do CSV (1 = primeira)")
    grupo.add_argument("--dominio", help="renderiza os contatos deste domínio")
    grupo.add_argument("--amostra", type=int, help="quantos contatos (por grupo, com --por)")
    parser.add_argument("--por", help="coluna de agrupamento da amostra (ex.: segmento)")
    parser.add_argument("--variante", type=int, default=1, help="opção do spintax (padrão: 1)")
    parser.add_argument("--saida", help="arquivo .md de saída; sem ele, imprime na saída padrão")
    args = parser.parse_args(argv)
    if args.por and args.amostra is None:
        parser.error("--por só vale junto com --amostra")

    try:
        sequencia = ler_sequencia(Path(args.sequencia).read_text(encoding="utf-8-sig"))
        tabela = ler_csv(Path(args.contatos))
    except (OSError, UnicodeDecodeError) as erro:
        print(f"ERRO: não consegui ler a entrada: {erro}", file=sys.stderr)
        return 2

    erros = conferir_sequencia(sequencia)
    avisos: list[str] = []
    for variavel in sequencia.variaveis.values():
        if variavel.coluna not in tabela.cabecalho:
            avisos.append(f"coluna '{variavel.coluna}' da variável {{{{{variavel.nome}}}}} não existe no CSV; "
                          f"todo contato recebe o fallback")

    escolhidos, problema = selecionar(tabela.linhas, tabela.cabecalho, args)
    if problema:
        erros.append(problema)

    blocos = [f"# Render · {Path(args.sequencia).name} · {len(escolhidos)} contato(s)"]
    vistos_ascii: set[tuple[str, str]] = set()
    for n, contato in escolhidos:
        blocos.append(cabecalho_do_contato(n, contato))
        toques, sem_papel = toques_do_contato(sequencia, contato)
        if sem_papel:
            avisos.append(f"linha {n}: contato sem papel reconhecido; recebeu as variantes de champion")
        for toque in toques:
            assunto = renderizar(toque.assunto, sequencia, contato, args.variante)
            corpo = renderizar(toque.corpo, sequencia, contato, args.variante)
            texto = f"Assunto: {assunto}\n\n{corpo}"
            if "{{" in texto or "}}" in texto:
                erros.append(f"linha {n}, {toque.rotulo}: sobrou {{{{ ou }}}} depois do render")
            elif "{" in texto or "}" in texto:
                avisos.append(f"linha {n}, {toque.rotulo}: chave solta depois do render (spintax malformado?)")
            if TRAVESSAO in texto and TRAVESSAO not in toque.assunto + toque.corpo:
                erros.append(f"linha {n}, {toque.rotulo}: travessão (U+2014) vindo do dado do contato")
            for achado in PALAVRAS_ASCII.finditer(texto):
                chave = (toque.nome, achado.group(0).lower())
                if chave not in vistos_ascii:
                    vistos_ascii.add(chave)
                    avisos.append(f"{toque.nome}: '{achado.group(0)}' sem acento (texto em ASCII?)")
            blocos.append(f"### {toque.rotulo}\n\n{texto}")

    saida = "\n\n".join(blocos) + "\n"
    if args.saida:
        Path(args.saida).write_text(saida, encoding="utf-8")
    else:
        sys.stdout.write(saida)

    for aviso in avisos:
        print(f"AVISO: {aviso}", file=sys.stderr)
    for erro in erros:
        print(f"ERRO: {erro}", file=sys.stderr)
    print(f"{len(escolhidos)} contato(s) renderizado(s), {len(erros)} erro(s), {len(avisos)} aviso(s).",
          file=sys.stderr)
    return 1 if erros else 0


if __name__ == "__main__":
    for fluxo in (sys.stdout, sys.stderr):
        try:
            fluxo.reconfigure(encoding="utf-8")
        except (AttributeError, ValueError):
            pass
    sys.exit(main())
