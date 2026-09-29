"""Normaliza domínio: sem esquema, sem www, sem caminho, sem porta, caixa baixa.

Uso:
    python scripts/normalize_domain.py <valor> [<valor> ...]
    python scripts/normalize_domain.py --csv entrada.csv --coluna domain [--saida saida.csv]

Com valores soltos, imprime um domínio normalizado por linha. Com --csv, normaliza
a coluna indicada e grava o CSV inteiro em --saida (ou na saída padrão, sem BOM,
se --saida faltar). O BOM da entrada é preservado na saída. Email vira o domínio
depois do @. Valor vazio vira vazio.

É a regra de chave `dominio` do ledger (ver schemas/ledger.schema.md).
"""
from __future__ import annotations

import argparse
import csv
import io
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

BOM = b"\xef\xbb\xbf"
_ESQUEMA = re.compile(r"^[a-z][a-z0-9+.-]*://")


def normalize_domain(valor: str | None) -> str:
    """Devolve o domínio normalizado de uma URL, domínio solto ou email."""
    if valor is None:
        return ""
    v = valor.strip().lower()
    if not v:
        return ""
    if v.startswith("mailto:"):
        v = v[len("mailto:"):]
    v = _ESQUEMA.sub("", v)
    if v.startswith("//"):
        v = v[2:]
    v = re.split(r"[/?#]", v, maxsplit=1)[0]
    if "@" in v:
        v = v.rsplit("@", 1)[1]
    v = v.split(":", 1)[0]
    v = v.strip().strip(".")
    if v.startswith("www."):
        v = v[4:]
    return v


@dataclass
class TabelaCsv:
    cabecalho: list[str]
    linhas: list[dict[str, str]] = field(default_factory=list)
    tem_bom: bool = False
    delimitador: str = ","


def ler_csv(caminho: Path) -> TabelaCsv:
    """Lê um CSV em UTF-8 (com ou sem BOM), detectando vírgula, ponto e vírgula ou tab."""
    bruto = Path(caminho).read_bytes()
    tem_bom = bruto.startswith(BOM)
    texto = bruto.decode("utf-8-sig")
    primeira = texto.split("\n", 1)[0]
    delimitador = max([",", ";", "\t"], key=primeira.count) if primeira else ","
    if primeira.count(delimitador) == 0:
        delimitador = ","
    leitor = csv.DictReader(io.StringIO(texto, newline=""), delimiter=delimitador)
    cabecalho = list(leitor.fieldnames or [])
    linhas = [{k: (v if v is not None else "") for k, v in linha.items() if k is not None} for linha in leitor]
    return TabelaCsv(cabecalho=cabecalho, linhas=linhas, tem_bom=tem_bom, delimitador=delimitador)


def csv_em_texto(cabecalho: list[str], linhas: list[dict[str, str]], delimitador: str = ",") -> str:
    buffer = io.StringIO(newline="")
    escritor = csv.DictWriter(
        buffer, fieldnames=cabecalho, delimiter=delimitador, lineterminator="\n", extrasaction="ignore"
    )
    escritor.writeheader()
    for linha in linhas:
        escritor.writerow({k: linha.get(k, "") for k in cabecalho})
    return buffer.getvalue()


def gravar_csv(caminho: Path, cabecalho: list[str], linhas: list[dict[str, str]],
               tem_bom: bool = False, delimitador: str = ",") -> None:
    dados = csv_em_texto(cabecalho, linhas, delimitador).encode("utf-8")
    Path(caminho).write_bytes((BOM if tem_bom else b"") + dados)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("valores", nargs="*", help="URLs, domínios ou emails")
    parser.add_argument("--csv", help="CSV de entrada")
    parser.add_argument("--coluna", default="domain", help="coluna a normalizar (padrão: domain)")
    parser.add_argument("--saida", help="CSV de saída; sem ele, imprime na saída padrão")
    args = parser.parse_args(argv)

    if not args.csv:
        if not args.valores:
            parser.error("informe valores ou --csv")
        for valor in args.valores:
            print(normalize_domain(valor))
        return 0

    try:
        tabela = ler_csv(Path(args.csv))
    except (OSError, UnicodeDecodeError) as erro:
        print(f"ERRO: não consegui ler {args.csv}: {erro}", file=sys.stderr)
        return 2
    if args.coluna not in tabela.cabecalho:
        print(f"ERRO: coluna '{args.coluna}' não existe em {args.csv}. Colunas: {', '.join(tabela.cabecalho)}",
              file=sys.stderr)
        return 1

    alterados = 0
    for linha in tabela.linhas:
        novo = normalize_domain(linha.get(args.coluna, ""))
        if novo != linha.get(args.coluna, ""):
            alterados += 1
        linha[args.coluna] = novo

    if args.saida:
        gravar_csv(Path(args.saida), tabela.cabecalho, tabela.linhas, tabela.tem_bom, tabela.delimitador)
        print(f"{len(tabela.linhas)} linha(s), {alterados} domínio(s) alterado(s). Gravado em {args.saida}",
              file=sys.stderr)
    else:
        sys.stdout.write(csv_em_texto(tabela.cabecalho, tabela.linhas, tabela.delimitador))
    return 0


if __name__ == "__main__":
    for fluxo in (sys.stdout, sys.stderr):
        try:
            fluxo.reconfigure(encoding="utf-8")
        except (AttributeError, ValueError):
            pass
    sys.exit(main())
