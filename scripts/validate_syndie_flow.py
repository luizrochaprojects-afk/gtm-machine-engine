"""Valida um fluxo da Syndie (formato 3.0.0) antes da importação.

Uso:
    python scripts/validate_syndie_flow.py fluxo.json [--schema schemas/syndie-flow.schema.json]

Confere:
  - o JSON contra o schema (precisa do pacote jsonschema; sem ele, esse passo é pulado com aviso);
  - metadata.nodeCount e metadata.edgeCount contra o número real;
  - ids de nó únicos; toda aresta liga nós existentes; id da aresta = <source>-<target>;
  - nenhum nó solto: uma raiz só (único nó sem entrada), todo nó alcançável a partir dela;
  - aresta que sai de condição tem sourceHandle yes/no, e cada condição tem exatamente um yes e um no;
  - todo merge recebe exatamente um targetHandle yes e um no;
  - mergeNodeId aponta pra um merge existente (obrigatório em condição);
  - customGuidelines até o limite do schema (1000); nota de convite (message do send_invite) até 300;
  - só variáveis nativas ({{first_name}}, {{last_name}}, {{company}}, {{title}}, lidas de
    x-limites.variaveis_nativas do schema) em message, customGuidelines e customComment,
    e nenhuma chave simples suspeita como {first_name}.

Imprime um erro por linha, começando pelo id do nó ou da aresta.
Sai com 0 se está tudo certo, 1 se houver erro, 2 se o arquivo ou o schema não abrir.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from collections import defaultdict
from pathlib import Path

SCHEMA_PADRAO = Path(__file__).resolve().parent.parent / "schemas" / "syndie-flow.schema.json"
TIPOS_CONDICAO = {"linkedin_request_accepted", "is_replied_on_linkedin"}
CAMPOS_TEXTO = ("message", "customGuidelines", "customComment")
VARIAVEL = re.compile(r"\{\{\s*([^{}]*?)\s*\}\}")
CHAVE_SIMPLES = re.compile(r"\{[^{}\n]{0,60}\}")


def eh_condicao(no: dict) -> bool:
    meta = (no.get("data") or {}).get("meta") or {}
    return no.get("type") in TIPOS_CONDICAO or meta.get("category") == "condition"


def validar_schema(fluxo: dict, schema: dict) -> list[str]:
    try:
        import jsonschema
    except ImportError:
        print("AVISO: pacote jsonschema não instalado; validação contra o schema pulada "
              "(instale com: pip install jsonschema).", file=sys.stderr)
        return []
    validador = jsonschema.Draft202012Validator(schema)
    nos = (fluxo.get("flow") or {}).get("nodes") if isinstance(fluxo.get("flow"), dict) else None
    erros = []
    for erro in sorted(validador.iter_errors(fluxo), key=lambda e: list(e.absolute_path)):
        caminho = list(erro.absolute_path)
        alvo = "fluxo"
        if len(caminho) >= 3 and caminho[:2] == ["flow", "nodes"] and isinstance(nos, list):
            indice = caminho[2]
            if isinstance(indice, int) and indice < len(nos) and isinstance(nos[indice], dict):
                alvo = nos[indice].get("id", f"nó #{indice}")
        elif len(caminho) >= 3 and caminho[:2] == ["flow", "edges"]:
            arestas = fluxo["flow"].get("edges") or []
            indice = caminho[2]
            if isinstance(indice, int) and indice < len(arestas) and isinstance(arestas[indice], dict):
                alvo = arestas[indice].get("id", f"aresta #{indice}")
        onde = "/".join(str(p) for p in caminho) or "(raiz)"
        mensagem = erro.message if len(erro.message) <= 200 else erro.message[:200] + "..."
        erros.append(f"{alvo}: schema em {onde}: {mensagem}")
    return erros


def validar_textos(no: dict, limites: dict) -> list[str]:
    erros = []
    nid = no.get("id", "?")
    config = (no.get("data") or {}).get("config") or {}
    max_prompt = limites.get("customGuidelines_max_chars", 1000)
    max_convite = limites.get("nota_convite_max_chars", 300)
    nativas = set(limites.get("variaveis_nativas", ["first_name", "last_name", "company", "title"]))

    prompt = config.get("customGuidelines")
    if isinstance(prompt, str) and len(prompt) > max_prompt:
        erros.append(f"{nid}: customGuidelines com {len(prompt)} caracteres (máximo {max_prompt})")
    mensagem = config.get("message")
    if no.get("type") == "send_invite" and isinstance(mensagem, str) and len(mensagem) > max_convite:
        erros.append(f"{nid}: nota de convite (message) com {len(mensagem)} caracteres (máximo {max_convite})")

    for campo in CAMPOS_TEXTO:
        texto = config.get(campo)
        if not isinstance(texto, str) or not texto:
            continue
        for achado in VARIAVEL.finditer(texto):
            nome = achado.group(1)
            if nome not in nativas:
                erros.append(f"{nid}: variável não nativa {achado.group(0)} em {campo} "
                             f"(só {', '.join('{{' + v + '}}' for v in sorted(nativas))})")
        resto = VARIAVEL.sub("", texto)
        for achado in CHAVE_SIMPLES.finditer(resto):
            erros.append(f"{nid}: chave simples suspeita {achado.group(0)} em {campo} (variável usa {{{{...}}}})")
        resto = CHAVE_SIMPLES.sub("", resto)
        if "{" in resto or "}" in resto:
            erros.append(f"{nid}: chave solta em {campo}")
    return erros


def validar_estrutura(fluxo: dict, limites: dict) -> list[str]:
    erros: list[str] = []
    flow = fluxo.get("flow") if isinstance(fluxo.get("flow"), dict) else {}
    nos = [n for n in (flow.get("nodes") or []) if isinstance(n, dict)]
    arestas = [e for e in (flow.get("edges") or []) if isinstance(e, dict)]

    metadata = fluxo.get("metadata") if isinstance(fluxo.get("metadata"), dict) else {}
    if metadata.get("nodeCount") != len(nos):
        erros.append(f"metadata: nodeCount = {metadata.get('nodeCount')}, mas o fluxo tem {len(nos)} nós")
    if metadata.get("edgeCount") != len(arestas):
        erros.append(f"metadata: edgeCount = {metadata.get('edgeCount')}, mas o fluxo tem {len(arestas)} arestas")

    por_id: dict[str, dict] = {}
    for no in nos:
        nid = no.get("id")
        if nid in por_id:
            erros.append(f"{nid}: id de nó duplicado")
        por_id[nid] = no

    entradas: dict[str, list[dict]] = defaultdict(list)
    saidas: dict[str, list[dict]] = defaultdict(list)
    for aresta in arestas:
        aid = aresta.get("id", "?")
        origem, destino = aresta.get("source"), aresta.get("target")
        quebrada = False
        for papel, ref in (("source", origem), ("target", destino)):
            if ref not in por_id:
                erros.append(f"{aid}: {papel} {ref} não existe entre os nós")
                quebrada = True
        if aresta.get("id") != f"{origem}-{destino}":
            erros.append(f"{aid}: id da aresta deveria ser {origem}-{destino}")
        contexto = (aresta.get("data") or {}).get("pluscontext")
        if isinstance(contexto, dict):
            if contexto.get("sourceId") != origem or contexto.get("targetId") != destino:
                erros.append(f"{aid}: pluscontext.sourceId/targetId não batem com source/target")
        if quebrada:
            continue
        saidas[origem].append(aresta)
        entradas[destino].append(aresta)

    # nó solto, raiz única e alcance
    soltos = [nid for nid in por_id if not entradas[nid] and not saidas[nid]]
    for nid in soltos:
        erros.append(f"{nid}: nó solto (sem aresta de entrada nem de saída)")
    raizes = [nid for nid in por_id if not entradas[nid] and nid not in soltos]
    if len(raizes) > 1:
        for nid in raizes:
            erros.append(f"{nid}: mais de uma raiz (nó sem entrada); raízes: {', '.join(raizes)}")
    elif not raizes and len(soltos) < len(por_id):
        erros.append("fluxo: nenhuma raiz (todo nó tem entrada; há ciclo)")
    if len(raizes) == 1:
        vistos, fila = {raizes[0]}, [raizes[0]]
        while fila:
            atual = fila.pop()
            for aresta in saidas[atual]:
                if aresta["target"] not in vistos:
                    vistos.add(aresta["target"])
                    fila.append(aresta["target"])
        for nid in por_id:
            if nid not in vistos and nid not in soltos:
                erros.append(f"{nid}: não é alcançável a partir da raiz {raizes[0]}")

    for nid, no in por_id.items():
        tipo = no.get("type")
        dados = no.get("data") if isinstance(no.get("data"), dict) else {}
        condicao = eh_condicao(no)

        # arestas que saem
        handles = [a.get("sourceHandle") for a in saidas[nid]]
        if condicao:
            if sorted(h for h in handles if h) != ["no", "yes"] or any(h not in ("yes", "no") for h in handles):
                erros.append(f"{nid}: condição precisa de exatamente uma saída yes e uma no (tem: {handles})")
            for aresta in saidas[nid]:
                handle = aresta.get("sourceHandle")
                contexto = (aresta.get("data") or {}).get("pluscontext") or {}
                if handle in ("yes", "no") and contexto and contexto.get("type") != f"branch-{handle}":
                    erros.append(f"{aresta.get('id')}: pluscontext.type deveria ser branch-{handle}")
        else:
            if any(h for h in handles):
                erros.append(f"{nid}: sourceHandle yes/no só pode sair de nó de condição")
            if tipo != "merge" and len(saidas[nid]) > 1:
                erros.append(f"{nid}: nó de ação com {len(saidas[nid])} saídas (máximo 1)")

        # arestas que entram
        alvos = [a.get("targetHandle") for a in entradas[nid]]
        if tipo == "merge":
            if sorted(h for h in alvos if h) != ["no", "yes"] or any(h not in ("yes", "no") for h in alvos):
                erros.append(f"{nid}: merge precisa receber exatamente um targetHandle yes e um no (tem: {alvos})")
        elif any(h for h in alvos):
            erros.append(f"{nid}: targetHandle só pode entrar em merge")

        # mergeNodeId
        if tipo != "merge":
            merge_id = dados.get("mergeNodeId")
            if condicao and not merge_id:
                erros.append(f"{nid}: condição sem mergeNodeId")
            if merge_id:
                alvo = por_id.get(merge_id)
                if alvo is None:
                    erros.append(f"{nid}: mergeNodeId {merge_id} não existe")
                elif alvo.get("type") != "merge":
                    erros.append(f"{nid}: mergeNodeId {merge_id} não é um nó merge")

        erros.extend(validar_textos(no, limites))
    return erros


def validar(fluxo: dict, schema: dict) -> list[str]:
    if not isinstance(fluxo, dict):
        return ["fluxo: o JSON precisa ser um objeto"]
    limites = schema.get("x-limites", {})
    return validar_schema(fluxo, schema) + validar_estrutura(fluxo, limites)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("fluxo", help="JSON do fluxo exportado ou gerado")
    parser.add_argument("--schema", default=str(SCHEMA_PADRAO), help="schema do fluxo")
    args = parser.parse_args(argv)

    try:
        schema = json.loads(Path(args.schema).read_text(encoding="utf-8"))
    except (OSError, ValueError) as erro:
        print(f"ERRO: não consegui abrir o schema {args.schema}: {erro}", file=sys.stderr)
        return 2
    try:
        fluxo = json.loads(Path(args.fluxo).read_text(encoding="utf-8-sig"))
    except (OSError, ValueError) as erro:
        print(f"ERRO: não consegui abrir {args.fluxo}: {erro}", file=sys.stderr)
        return 2

    erros = validar(fluxo, schema)
    for erro in erros:
        print(erro)
    if erros:
        print(f"\nFALHOU: {len(erros)} erro(s) em {args.fluxo}.")
        return 1
    flow = fluxo["flow"]
    print(f"OK: {args.fluxo} ({len(flow['nodes'])} nós, {len(flow['edges'])} arestas).")
    return 0


if __name__ == "__main__":
    for fluxo_saida in (sys.stdout, sys.stderr):
        try:
            fluxo_saida.reconfigure(encoding="utf-8")
        except (AttributeError, ValueError):
            pass
    sys.exit(main())
