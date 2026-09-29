"""Tira da lista quem não pode ser abordado, com o motivo de cada remoção.

Uso:
    python scripts/suppress.py --lista lista.csv --ledger-dir <pasta> \\
        --saida filtrado.csv --removidos removidos.csv \\
        [--col-dominio domain] [--col-email email] [--col-linkedin linkedin_url] \
        [--nivel auto|contas|contatos]

A pasta do ledger tem o snapshot CSV das abas `supressao.csv`, `contas.csv`,
`contatos.csv` e `toques.csv`, com os cabeçalhos de schemas/ledger.schema.md.
Aba ausente conta como vazia (com aviso em stderr).

Regras, na ordem (a primeira que casar vira o motivo em `motivo_supressao`):
  1. chave na aba supressao (dominio, email ou linkedin) → supressao:<motivo>
  2. conta com nao_abordar = sim                           → nao_abordar_conta
  3. contato com nao_abordar = sim (por email ou linkedin) → nao_abordar_contato
  4. já recebeu toque `enviado` e nenhuma `resposta`       → toque_sem_resposta
     Lista de contatos: por contato_id, achado em contatos.csv pelo email ou
     pelo linkedin. Lista de contas: por domínio.

--nivel diz se a lista é de contas ou de contatos. Em `auto` (padrão), é de
contatos quando tem coluna de email ou linkedin. Lista de contas com
`linkedin_url` da página da empresa (ex.: 01-lista-crua.csv) precisa de
`--nivel contas`, senão a regra 4 procuraria pessoa e deixaria passar a conta.

Imprime o resumo: total, removidos por motivo, mantidos. A saída sai com BOM
se a lista de entrada tinha BOM.
"""
from __future__ import annotations

import argparse
import sys
from collections import Counter, defaultdict
from pathlib import Path
from urllib.parse import unquote

from normalize_domain import TabelaCsv, gravar_csv, ler_csv, normalize_domain

ABAS = ("supressao", "contas", "contatos", "toques")
COLUNA_MOTIVO = "motivo_supressao"
ALIASES_DOMINIO = ("domain", "dominio", "website", "site")


def limpar(valor: str | None) -> str:
    """Tira espaço e o prefixo `'` que o Sheets usa pra forçar texto."""
    v = (valor or "").strip()
    if v.startswith("'"):
        v = v[1:].strip()
    return v


def normalizar_email(valor: str | None) -> str:
    return limpar(valor).lower()


def normalizar_linkedin(valor: str | None) -> str:
    """https://www.linkedin.com/in/<slug>, caixa baixa, sem barra final nem query."""
    v = unquote(limpar(valor)).lower()
    if not v:
        return ""
    v = v.split("?", 1)[0].split("#", 1)[0]
    marcador = "linkedin.com/in/"
    if marcador in v:
        slug = v.split(marcador, 1)[1].split("/", 1)[0]
        return f"https://www.linkedin.com/in/{slug}" if slug else ""
    return v.rstrip("/")


def sim(valor: str | None) -> bool:
    return limpar(valor).lower() == "sim"


def ler_aba(pasta: Path, nome: str) -> list[dict[str, str]]:
    caminho = pasta / f"{nome}.csv"
    if not caminho.is_file():
        print(f"AVISO: {caminho} não existe; aba '{nome}' tratada como vazia.", file=sys.stderr)
        return []
    return ler_csv(caminho).linhas


class Ledger:
    """Índices do snapshot do ledger usados pelas regras de supressão."""

    def __init__(self, abas: dict[str, list[dict[str, str]]]):
        self.supressao: dict[tuple[str, str], str] = {}
        for linha in abas.get("supressao", []):
            tipo = limpar(linha.get("tipo")).lower()
            chave = limpar(linha.get("chave"))
            if not tipo or not chave:
                continue
            if tipo == "dominio":
                chave = normalize_domain(chave)
            elif tipo == "email":
                chave = normalizar_email(chave)
            elif tipo == "linkedin":
                chave = normalizar_linkedin(chave)
            motivo = limpar(linha.get("motivo")) or "sem_motivo"
            self.supressao.setdefault((tipo, chave), motivo)

        self.contas_bloqueadas = {
            normalize_domain(limpar(l.get("dominio"))) for l in abas.get("contas", []) if sim(l.get("nao_abordar"))
        }

        self.ids_por_email: dict[str, set[str]] = defaultdict(set)
        self.ids_por_linkedin: dict[str, set[str]] = defaultdict(set)
        self.emails_bloqueados: set[str] = set()
        self.linkedins_bloqueados: set[str] = set()
        for linha in abas.get("contatos", []):
            cid = limpar(linha.get("contato_id"))
            email = normalizar_email(linha.get("email"))
            linkedin = normalizar_linkedin(linha.get("linkedin_url"))
            if email:
                self.ids_por_email[email].add(cid)
            if linkedin:
                self.ids_por_linkedin[linkedin].add(cid)
            if sim(linha.get("nao_abordar")):
                if email:
                    self.emails_bloqueados.add(email)
                if linkedin:
                    self.linkedins_bloqueados.add(linkedin)

        eventos_contato: dict[str, set[str]] = defaultdict(set)
        eventos_dominio: dict[str, set[str]] = defaultdict(set)
        for linha in abas.get("toques", []):
            evento = limpar(linha.get("evento")).lower()
            cid = limpar(linha.get("contato_id"))
            dominio = normalize_domain(limpar(linha.get("dominio")))
            if not dominio and ":" in cid:
                dominio = normalize_domain(cid.split(":", 1)[0])
            if cid:
                eventos_contato[cid].add(evento)
            if dominio:
                eventos_dominio[dominio].add(evento)
        self.contatos_sem_resposta = {c for c, ev in eventos_contato.items() if "enviado" in ev and "resposta" not in ev}
        self.dominios_sem_resposta = {d for d, ev in eventos_dominio.items() if "enviado" in ev and "resposta" not in ev}

    def motivo(self, dominio: str, email: str, linkedin: str, lista_de_contatos: bool) -> str | None:
        for tipo, chave in (("dominio", dominio), ("email", email), ("linkedin", linkedin)):
            if chave and (tipo, chave) in self.supressao:
                return f"supressao:{self.supressao[(tipo, chave)]}"
        if dominio and dominio in self.contas_bloqueadas:
            return "nao_abordar_conta"
        if (email and email in self.emails_bloqueados) or (linkedin and linkedin in self.linkedins_bloqueados):
            return "nao_abordar_contato"
        if lista_de_contatos:
            ids = set()
            if email:
                ids |= self.ids_por_email.get(email, set())
            if linkedin:
                ids |= self.ids_por_linkedin.get(linkedin, set())
            if ids & self.contatos_sem_resposta:
                return "toque_sem_resposta"
        elif dominio and dominio in self.dominios_sem_resposta:
            return "toque_sem_resposta"
        return None


def resolver_coluna(cabecalho: list[str], pedida: str, aliases: tuple[str, ...] = ()) -> str | None:
    if pedida in cabecalho:
        return pedida
    for alias in aliases:
        if alias in cabecalho:
            return alias
    return None


def filtrar(tabela: TabelaCsv, ledger: Ledger, col_dominio: str | None, col_email: str | None,
            col_linkedin: str | None) -> tuple[list[dict[str, str]], list[dict[str, str]]]:
    lista_de_contatos = bool(col_email or col_linkedin)
    mantidos, removidos = [], []
    for linha in tabela.linhas:
        email = normalizar_email(linha.get(col_email)) if col_email else ""
        linkedin = normalizar_linkedin(linha.get(col_linkedin)) if col_linkedin else ""
        dominio = normalize_domain(linha.get(col_dominio)) if col_dominio else ""
        if not dominio and "@" in email:
            dominio = normalize_domain(email)
        motivo = ledger.motivo(dominio, email, linkedin, lista_de_contatos)
        if motivo:
            removidos.append({**linha, COLUNA_MOTIVO: motivo})
        else:
            mantidos.append(linha)
    return mantidos, removidos


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--lista", required=True, help="CSV da lista (contas ou contatos)")
    parser.add_argument("--ledger-dir", required=True, help="pasta com o snapshot CSV das abas do ledger")
    parser.add_argument("--saida", required=True, help="CSV filtrado")
    parser.add_argument("--removidos", required=True, help="CSV dos removidos, com motivo_supressao")
    parser.add_argument("--col-dominio", default="domain")
    parser.add_argument("--col-email", default="email")
    parser.add_argument("--col-linkedin", default="linkedin_url")
    parser.add_argument("--nivel", choices=("auto", "contas", "contatos"), default="auto",
                        help="lista de contas ou de contatos (auto: decide pelas colunas)")
    args = parser.parse_args(argv)

    try:
        tabela = ler_csv(Path(args.lista))
    except (OSError, UnicodeDecodeError) as erro:
        print(f"ERRO: não consegui ler {args.lista}: {erro}", file=sys.stderr)
        return 2

    pasta = Path(args.ledger_dir)
    if not pasta.is_dir():
        print(f"AVISO: pasta do ledger {pasta} não existe; todas as abas tratadas como vazias.", file=sys.stderr)
        abas = {nome: [] for nome in ABAS}
    else:
        abas = {nome: ler_aba(pasta, nome) for nome in ABAS}
    ledger = Ledger(abas)

    col_dominio = resolver_coluna(tabela.cabecalho, args.col_dominio,
                                  ALIASES_DOMINIO if args.col_dominio == "domain" else ())
    col_email = resolver_coluna(tabela.cabecalho, args.col_email)
    col_linkedin = resolver_coluna(tabela.cabecalho, args.col_linkedin)
    if args.nivel == "contas":
        col_email = col_linkedin = None
    elif args.nivel == "contatos" and not (col_email or col_linkedin):
        print("ERRO: --nivel contatos pede coluna de email ou linkedin na lista.", file=sys.stderr)
        return 1
    if not (col_dominio or col_email or col_linkedin):
        print("ERRO: a lista não tem coluna de domínio, email nem linkedin.", file=sys.stderr)
        return 1
    if not col_dominio:
        print(f"AVISO: coluna de domínio '{args.col_dominio}' não existe; uso o domínio do email.", file=sys.stderr)

    mantidos, removidos = filtrar(tabela, ledger, col_dominio, col_email, col_linkedin)
    gravar_csv(Path(args.saida), tabela.cabecalho, mantidos, tabela.tem_bom, tabela.delimitador)
    gravar_csv(Path(args.removidos), tabela.cabecalho + [COLUNA_MOTIVO], removidos, tabela.tem_bom,
               tabela.delimitador)

    tipo = "contatos" if (col_email or col_linkedin) else "contas"
    print(f"Lista de {tipo}: {args.lista}")
    print(f"Total: {len(tabela.linhas)}")
    print(f"Removidos: {len(removidos)}")
    for motivo, qtd in sorted(Counter(r[COLUNA_MOTIVO] for r in removidos).items()):
        print(f"  {motivo}: {qtd}")
    print(f"Mantidos: {len(mantidos)}")
    return 0


if __name__ == "__main__":
    for fluxo in (sys.stdout, sys.stderr):
        try:
            fluxo.reconfigure(encoding="utf-8")
        except (AttributeError, ValueError):
            pass
    sys.exit(main())
