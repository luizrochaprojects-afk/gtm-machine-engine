import shutil
import subprocess
from pathlib import Path

import pytest

from check_sanitize import main, normalizar


def montar(tmp_path: Path, conteudo_skill: str) -> Path:
    (tmp_path / "scripts").mkdir()
    (tmp_path / "scripts" / "termos-clientes.txt").write_text(
        "# termos de teste\nClienteFicticio\nJoão Exemplo\n", encoding="utf-8"
    )
    skill = tmp_path / "skills" / "alguma"
    skill.mkdir(parents=True)
    (skill / "SKILL.md").write_text(conteudo_skill, encoding="utf-8")
    return tmp_path


def test_motor_limpo_passa(tmp_path, capsys):
    raiz = montar(tmp_path, "Lê o gabarito do workspace ativo.\n")
    assert main(["--raiz", str(raiz)]) == 0
    assert "OK" in capsys.readouterr().out


def test_termo_de_cliente_falha(tmp_path, capsys):
    raiz = montar(tmp_path, "Exemplo: a clienteficticio usa X.\n")
    assert main(["--raiz", str(raiz)]) == 1
    saida = capsys.readouterr().out
    assert "skills/alguma/SKILL.md:1" in saida.replace("\\", "/")


def test_saida_nao_repete_o_termo(tmp_path, capsys):
    raiz = montar(tmp_path, "Exemplo: a clienteficticio usa X.\n")
    assert main(["--raiz", str(raiz)]) == 1
    saida = capsys.readouterr().out
    assert "termo #1" in saida
    assert "clienteficticio" not in normalizar(saida)


def test_ignora_acento_e_maiuscula(tmp_path):
    raiz = montar(tmp_path, "aprovado pelo JOAO EXEMPLO\n")
    assert main(["--raiz", str(raiz)]) == 1


def test_lista_de_termos_nao_se_acusa(tmp_path):
    raiz = montar(tmp_path, "limpo\n")
    assert main(["--raiz", str(raiz)]) == 0


def test_sem_lista_de_termos_da_erro(tmp_path):
    (tmp_path / "skills").mkdir()
    assert main(["--raiz", str(tmp_path)]) == 2


def test_varre_arquivo_fora_das_pastas_do_motor(tmp_path, capsys):
    raiz = montar(tmp_path, "limpo\n")
    (raiz / "tasks").mkdir()
    (raiz / "tasks" / "plano.md").write_text("reunião com a ClienteFicticio\n", encoding="utf-8")
    (raiz / "notas.cfg").write_text("sem termo\n", encoding="utf-8")
    assert main(["--raiz", str(raiz)]) == 1
    assert "tasks/plano.md:1" in capsys.readouterr().out


def test_varre_qualquer_extensao(tmp_path):
    raiz = montar(tmp_path, "limpo\n")
    (raiz / "config.toml").write_text('dono = "João Exemplo"\n', encoding="utf-8")
    assert main(["--raiz", str(raiz)]) == 1


def test_acusa_termo_no_nome_do_arquivo(tmp_path, capsys):
    raiz = montar(tmp_path, "limpo\n")
    (raiz / "docs").mkdir()
    (raiz / "docs" / "clienteficticio-kickoff.md").write_text("limpo\n", encoding="utf-8")
    assert main(["--raiz", str(raiz)]) == 1
    assert "caminho do arquivo" in capsys.readouterr().out


def test_pula_binario(tmp_path):
    raiz = montar(tmp_path, "limpo\n")
    (raiz / "imagem.png").write_bytes(b"\x89PNG\x00ClienteFicticio\xff")
    assert main(["--raiz", str(raiz)]) == 0


def test_sem_git_pula_workspaces_de_cliente(tmp_path):
    raiz = montar(tmp_path, "limpo\n")
    ws = raiz / "clientes" / "acme"
    ws.mkdir(parents=True)
    (ws / "cliente.yaml").write_text("nome: ClienteFicticio\n", encoding="utf-8")
    (raiz / "clientes" / ".gitkeep").write_text("", encoding="utf-8")
    assert main(["--raiz", str(raiz)]) == 0


@pytest.mark.skipif(shutil.which("git") is None, reason="git não instalado")
def test_com_git_segue_o_gitignore(tmp_path, capsys):
    raiz = montar(tmp_path, "limpo\n")
    subprocess.run(["git", "init", "-q", str(raiz)], check=True)
    (raiz / ".gitignore").write_text("scripts/termos-clientes.txt\nprivado/\n", encoding="utf-8")
    (raiz / "privado").mkdir()
    (raiz / "privado" / "notas.md").write_text("ClienteFicticio\n", encoding="utf-8")
    assert main(["--raiz", str(raiz)]) == 0

    (raiz / "novo.md").write_text("ClienteFicticio\n", encoding="utf-8")
    assert main(["--raiz", str(raiz)]) == 1
    assert "novo.md:1" in capsys.readouterr().out


def test_normalizar():
    assert normalizar("Ação") == "acao"
