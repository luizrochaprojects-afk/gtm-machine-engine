import copy
import json
from pathlib import Path

import pytest

from validate_syndie_flow import main

RAIZ = Path(__file__).resolve().parent.parent
REFERENCIAS = RAIZ / "skills" / "syndie-flow-builder" / "references"
VALIDO = REFERENCIAS / "fluxo-convite-dm.json"


def carregar() -> dict:
    return json.loads(VALIDO.read_text(encoding="utf-8"))


def gravar(tmp_path: Path, fluxo: dict) -> str:
    caminho = tmp_path / "fluxo.json"
    caminho.write_text(json.dumps(fluxo, ensure_ascii=False), encoding="utf-8")
    return str(caminho)


def no_do_tipo(fluxo: dict, tipo: str) -> dict:
    return next(n for n in fluxo["flow"]["nodes"] if n["type"] == tipo)


@pytest.mark.parametrize("arquivo", ["fluxo-convite-dm.json", "fluxo-lembrete.json"])
def test_referencias_sao_validas(arquivo, capsys):
    assert main([str(REFERENCIAS / arquivo)]) == 0
    assert "OK" in capsys.readouterr().out


def test_aresta_quebrada(tmp_path, capsys):
    fluxo = carregar()
    fluxo["flow"]["edges"][0]["target"] = "send_invite-999"
    assert main([gravar(tmp_path, fluxo)]) == 1
    saida = capsys.readouterr().out
    assert "send_invite-999" in saida
    assert "não existe" in saida


def test_prompt_longo(tmp_path, capsys):
    fluxo = carregar()
    convite = no_do_tipo(fluxo, "send_invite")
    convite["data"]["config"]["customGuidelines"] = "a" * 1001
    assert main([gravar(tmp_path, fluxo)]) == 1
    saida = capsys.readouterr().out
    assert convite["id"] in saida
    assert "1001" in saida


def test_variavel_custom(tmp_path, capsys):
    fluxo = carregar()
    dm = no_do_tipo(fluxo, "send_followup")
    dm["data"]["config"]["message"] = "Oi {{first_name}}, como vai a {{empresa}}?"
    assert main([gravar(tmp_path, fluxo)]) == 1
    saida = capsys.readouterr().out
    assert dm["id"] in saida
    assert "{{empresa}}" in saida


def test_chave_simples_suspeita(tmp_path, capsys):
    fluxo = carregar()
    dm = no_do_tipo(fluxo, "send_followup")
    dm["data"]["config"]["message"] = "Oi {first_name}, tudo certo?"
    assert main([gravar(tmp_path, fluxo)]) == 1
    assert "{first_name}" in capsys.readouterr().out


def test_nota_de_convite_longa(tmp_path, capsys):
    fluxo = carregar()
    convite = no_do_tipo(fluxo, "send_invite")
    convite["data"]["config"]["message"] = "b" * 301
    assert main([gravar(tmp_path, fluxo)]) == 1
    assert convite["id"] in capsys.readouterr().out


def test_no_solto(tmp_path, capsys):
    fluxo = carregar()
    solto = copy.deepcopy(no_do_tipo(fluxo, "like_post"))
    solto["id"] = "like_post-4242"
    fluxo["flow"]["nodes"].append(solto)
    fluxo["metadata"]["nodeCount"] += 1
    assert main([gravar(tmp_path, fluxo)]) == 1
    saida = capsys.readouterr().out
    assert "like_post-4242" in saida
    assert "solto" in saida


def test_contagem_errada(tmp_path, capsys):
    fluxo = carregar()
    fluxo["metadata"]["nodeCount"] = 7
    fluxo["metadata"]["edgeCount"] = 99
    assert main([gravar(tmp_path, fluxo)]) == 1
    saida = capsys.readouterr().out
    assert "nodeCount" in saida
    assert "edgeCount" in saida


def test_condicao_sem_ramo_no(tmp_path, capsys):
    fluxo = carregar()
    condicao = no_do_tipo(fluxo, "linkedin_request_accepted")
    aresta = next(e for e in fluxo["flow"]["edges"]
                  if e["source"] == condicao["id"] and e.get("sourceHandle") == "no")
    aresta["sourceHandle"] = "yes"
    assert main([gravar(tmp_path, fluxo)]) == 1
    assert condicao["id"] in capsys.readouterr().out


def test_merge_inexistente(tmp_path, capsys):
    fluxo = carregar()
    condicao = no_do_tipo(fluxo, "is_replied_on_linkedin")
    condicao["data"]["mergeNodeId"] = "merge-31337"
    assert main([gravar(tmp_path, fluxo)]) == 1
    assert "merge-31337" in capsys.readouterr().out


def test_id_duplicado(tmp_path, capsys):
    fluxo = carregar()
    nos = fluxo["flow"]["nodes"]
    nos.append(copy.deepcopy(nos[1]))
    fluxo["metadata"]["nodeCount"] += 1
    assert main([gravar(tmp_path, fluxo)]) == 1
    assert "duplicado" in capsys.readouterr().out


def test_schema_reprova_tipo_desconhecido(tmp_path, capsys):
    fluxo = carregar()
    fluxo["version"] = "2.0.0"
    assert main([gravar(tmp_path, fluxo)]) == 1
    assert "schema" in capsys.readouterr().out


def test_arquivo_inexistente(tmp_path):
    assert main([str(tmp_path / "nao-existe.json")]) == 2


def test_json_invalido(tmp_path):
    caminho = tmp_path / "quebrado.json"
    caminho.write_text("{ não é json", encoding="utf-8")
    assert main([str(caminho)]) == 2
