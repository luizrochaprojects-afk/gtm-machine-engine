from pathlib import Path

import pytest

from normalize_domain import ler_csv, main, normalize_domain


@pytest.mark.parametrize(
    "entrada, esperado",
    [
        ("https://www.X.com.br/", "x.com.br"),
        ("X.COM.BR", "x.com.br"),
        ("x.com.br/loja", "x.com.br"),
        ("  http://acme.com.br  ", "acme.com.br"),
        ("www.acme.com.br", "acme.com.br"),
        ("https://acme.com.br:8080/loja?utm=1#topo", "acme.com.br"),
        ("acme.com.br?ref=apollo", "acme.com.br"),
        ("ana.souza@Acme.com.br", "acme.com.br"),
        ("mailto:ana@acme.com.br", "acme.com.br"),
        ("loja.acme.com.br", "loja.acme.com.br"),
        ("//www.acme.com/", "acme.com"),
        ("", ""),
        ("   ", ""),
    ],
)
def test_normalize_domain(entrada, esperado):
    assert normalize_domain(entrada) == esperado


def test_none_vira_vazio():
    assert normalize_domain(None) == ""


def test_cli_valores(capsys):
    assert main(["https://www.Acme.com.br/", "ACME.COM"]) == 0
    assert capsys.readouterr().out.splitlines() == ["acme.com.br", "acme.com"]


def escrever(caminho: Path, texto: str, bom: bool) -> None:
    dados = texto.encode("utf-8")
    if bom:
        dados = b"\xef\xbb\xbf" + dados
    caminho.write_bytes(dados)


def test_cli_csv_preserva_bom_e_acento(tmp_path):
    entrada = tmp_path / "lista.csv"
    saida = tmp_path / "saida.csv"
    escrever(entrada, "empresa,domain\nAcme Ação,https://www.Acme.com.br/\nBeta,beta.com/loja\n", bom=True)
    assert main(["--csv", str(entrada), "--coluna", "domain", "--saida", str(saida)]) == 0
    bruto = saida.read_bytes()
    assert bruto.startswith(b"\xef\xbb\xbf")
    texto = bruto.decode("utf-8-sig")
    assert "Acme Ação,acme.com.br" in texto
    assert "Beta,beta.com" in texto


def test_cli_csv_sem_bom_continua_sem_bom(tmp_path):
    entrada = tmp_path / "lista.csv"
    saida = tmp_path / "saida.csv"
    escrever(entrada, "domain\nWWW.ACME.COM\n", bom=False)
    assert main(["--csv", str(entrada), "--coluna", "domain", "--saida", str(saida)]) == 0
    bruto = saida.read_bytes()
    assert not bruto.startswith(b"\xef\xbb\xbf")
    assert bruto.decode("utf-8").splitlines() == ["domain", "acme.com"]


def test_cli_csv_coluna_inexistente(tmp_path):
    entrada = tmp_path / "lista.csv"
    escrever(entrada, "empresa\nAcme\n", bom=False)
    assert main(["--csv", str(entrada), "--coluna", "domain"]) == 1


def test_ler_csv_ponto_e_virgula(tmp_path):
    entrada = tmp_path / "lista.csv"
    escrever(entrada, "empresa;domain\nAcme;acme.com\n", bom=False)
    tabela = ler_csv(entrada)
    assert tabela.cabecalho == ["empresa", "domain"]
    assert tabela.linhas[0]["domain"] == "acme.com"
    assert tabela.delimitador == ";"
