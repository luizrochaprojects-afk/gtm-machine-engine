"""Falha se aparecer termo de cliente em qualquer arquivo do repositório.

Uso:
    python scripts/check_sanitize.py [--raiz .] [--termos scripts/termos-clientes.txt]

Lê um termo por linha (linhas vazias e começadas por # são ignoradas).
A busca ignora maiúsculas e acentos e olha o conteúdo e o caminho de cada arquivo.
Sai com código 1 se achar algo.

Quais arquivos entram:
- Se a raiz é um repositório git, todo arquivo que o git versionaria: os já
  versionados e os novos que o .gitignore não exclui. Assim `clientes/*` e a
  própria lista de termos, que são ignorados, ficam de fora.
- Sem git, todo arquivo abaixo da raiz, menos `.git/`, caches e o conteúdo de
  `clientes/` (workspaces de cliente, que nunca entram no git do motor).

Arquivo binário (com byte nulo ou que não é UTF-8) é pulado. A saída nunca
repete o termo: mostra o número dele na lista (termo #N), pra que o relatório
possa ser lido ou colado sem vazar nome de cliente.
"""
from __future__ import annotations

import argparse
import subprocess
import sys
import unicodedata
from collections import Counter
from pathlib import Path

IGNORAR = {"termos-clientes.txt"}
PASTAS_IGNORADAS = {".git", "__pycache__", ".pytest_cache", ".venv", "venv", "node_modules"}
PASTA_CLIENTES = "clientes"


def normalizar(texto: str) -> str:
    sem_acento = unicodedata.normalize("NFKD", texto)
    sem_acento = "".join(c for c in sem_acento if not unicodedata.combining(c))
    return sem_acento.casefold()


def ler_termos(caminho: Path) -> list[str]:
    termos = []
    for linha in caminho.read_text(encoding="utf-8").splitlines():
        linha = linha.strip()
        if linha and not linha.startswith("#"):
            termos.append(linha)
    return termos


def _arquivos_pelo_git(raiz: Path) -> list[Path] | None:
    """Arquivos que o git versionaria. None se a raiz não é repositório git."""
    if not (raiz / ".git").exists():
        return None
    try:
        saida = subprocess.run(
            ["git", "-C", str(raiz), "ls-files", "--cached", "--others", "--exclude-standard", "-z"],
            capture_output=True,
            check=True,
        ).stdout
    except (OSError, subprocess.CalledProcessError):
        return None
    nomes = sorted({n for n in saida.decode("utf-8").split("\0") if n})
    return [raiz / n for n in nomes]


def _arquivos_pela_pasta(raiz: Path) -> list[Path]:
    arquivos = []
    for p in sorted(raiz.rglob("*")):
        partes = p.relative_to(raiz).parts
        if any(parte in PASTAS_IGNORADAS for parte in partes):
            continue
        if partes[0] == PASTA_CLIENTES and len(partes) > 1 and partes[1] != ".gitkeep":
            continue
        arquivos.append(p)
    return arquivos


def arquivos_do_repo(raiz: Path, ignorar: set[Path] | None = None):
    ignorar = ignorar or set()
    candidatos = _arquivos_pelo_git(raiz)
    if candidatos is None:
        candidatos = _arquivos_pela_pasta(raiz)
    for p in candidatos:
        if not p.is_file() or p.name in IGNORAR or p.resolve() in ignorar:
            continue
        yield p


def ler_texto(arquivo: Path) -> list[str] | None:
    """Linhas do arquivo, ou None se for binário."""
    dados = arquivo.read_bytes()
    if b"\0" in dados:
        return None
    try:
        return dados.decode("utf-8-sig").splitlines()
    except UnicodeDecodeError:
        return None


def procurar(raiz: Path, termos: list[str], ignorar: set[Path] | None = None) -> list[tuple[Path, int, int]]:
    """Lista de (arquivo relativo, linha, número do termo). Linha 0 = o caminho do arquivo."""
    termos_norm = [(i, normalizar(t)) for i, t in enumerate(termos, start=1)]
    achados = []
    for arquivo in arquivos_do_repo(raiz, ignorar):
        relativo = arquivo.relative_to(raiz)
        caminho_norm = normalizar(relativo.as_posix())
        for i, norm in termos_norm:
            if norm in caminho_norm:
                achados.append((relativo, 0, i))
        linhas = ler_texto(arquivo)
        if linhas is None:
            continue
        for n, linha in enumerate(linhas, start=1):
            linha_norm = normalizar(linha)
            for i, norm in termos_norm:
                if norm in linha_norm:
                    achados.append((relativo, n, i))
    return achados


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--raiz", default=".", help="raiz do repositório")
    parser.add_argument("--termos", default="scripts/termos-clientes.txt")
    args = parser.parse_args(argv)

    raiz = Path(args.raiz).resolve()
    caminho_termos = Path(args.termos)
    if not caminho_termos.is_absolute():
        caminho_termos = raiz / caminho_termos
    if not caminho_termos.is_file():
        print(f"ERRO: lista de termos não encontrada em {caminho_termos}", file=sys.stderr)
        return 2

    termos = ler_termos(caminho_termos)
    achados = procurar(raiz, termos, ignorar={caminho_termos.resolve()})
    for arquivo, linha, i in achados:
        onde = "caminho do arquivo" if linha == 0 else str(linha)
        print(f"{arquivo.as_posix()}:{onde}: termo #{i}")
    if achados:
        print(f"\nFALHOU: {len(achados)} ocorrência(s) de termo de cliente no repositório.")
        for i, total in sorted(Counter(i for _, _, i in achados).items()):
            print(f"  termo #{i}: {total}")
        print("O número é a posição do termo na lista, sem contar linhas vazias e comentários.")
        return 1
    print(f"OK: nenhum dos {len(termos)} termos aparece no repositório.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
