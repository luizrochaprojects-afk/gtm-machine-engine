from pathlib import Path

from render_email import ler_sequencia, main, resolver_spintax

SEQUENCIA = """# Sequência · 2026-10-01-r1-moda-retencao · moda · retenção

Versão da máquina: 2026-10-01 · juiz: 8,5 · rodadas de revisão: 2

## Variáveis

| variável | coluna | fallback |
|---|---|---|
| first_name | primeiro_nome | tudo bem |
| company | company_name | vocês |
| primeira_frase | primeira_frase | A recompra de moda costuma cair depois da segunda compra. |

## D1

Assunto: recompra na {{company}}

{Oi|Olá} {{first_name}},

{{primeira_frase}}

Hoje vocês sabem quantos clientes da {{company}} compraram só uma vez?

## D4

Assunto: (mesma thread)

{{first_name}}, uma coisa que faltou: a régua de reposição também pesa.

## D8

Assunto: (mesma thread)

Última ideia sobre a {{company}}: o cupom vai para quem já ia voltar.

## D13

Assunto: encerrando por aqui

Se não for prioridade agora, sem problema.

## Notas do juiz

Aqui tem {{variavel_do_juiz}} e \u2014 que o render ignora.
"""

CABECALHO = "domain,nome,primeiro_nome,cargo,company_name,segmento,primeira_frase\n"


def montar(tmp_path: Path, sequencia: str = SEQUENCIA, contatos: str | None = None, bom=True):
    seq = tmp_path / "04-sequencia-email.md"
    seq.write_text(sequencia, encoding="utf-8")
    if contatos is None:
        contatos = (
            CABECALHO
            + "acme.com.br,Ana Souza,Ana,Head de CRM,Acme Moda,moda,A Acme abriu a terceira loja em setembro.\n"
            + "beta.com.br,Bruno Lima,,Gerente de E-commerce,,moda,\n"
            + "gama.com.br,Carla Dias,Carla,Diretora,Gama Pet,pet,\n"
        )
    csv = tmp_path / "03-contatos.csv"
    dados = contatos.encode("utf-8")
    csv.write_bytes((b"\xef\xbb\xbf" if bom else b"") + dados)
    return seq, csv


def rodar(tmp_path, *extra, **kw):
    seq, csv = montar(tmp_path, **kw)
    saida = tmp_path / "out.md"
    codigo = main(["--sequencia", str(seq), "--contatos", str(csv), "--saida", str(saida), *extra])
    texto = saida.read_text(encoding="utf-8") if saida.exists() else ""
    return codigo, texto


def test_render_basico_com_acento_e_spintax(tmp_path):
    codigo, texto = rodar(tmp_path, "--linha", "1")
    assert codigo == 0
    assert "Oi Ana," in texto
    assert "Assunto: recompra na Acme Moda" in texto
    assert "A Acme abriu a terceira loja em setembro." in texto
    assert "régua de reposição" in texto
    assert "Assunto: (mesma thread)" in texto
    for toque in ("D1", "D4", "D8", "D13"):
        assert f"### {toque}" in texto
    assert "Bruno" not in texto


def test_variavel_vazia_usa_fallback(tmp_path):
    codigo, texto = rodar(tmp_path, "--dominio", "https://www.Beta.com.br/")
    assert codigo == 0
    assert "Oi tudo bem," in texto
    assert "Assunto: recompra na vocês" in texto
    assert "A recompra de moda costuma cair depois da segunda compra." in texto


def test_nenhuma_chave_sobra(tmp_path):
    codigo, texto = rodar(tmp_path)
    assert codigo == 0
    assert "{{" not in texto and "}}" not in texto
    assert "{Oi" not in texto
    assert "variavel_do_juiz" not in texto
    assert "\u2014" not in texto


def test_variante_escolhe_outra_opcao(tmp_path):
    codigo, texto = rodar(tmp_path, "--linha", "1", "--variante", "2")
    assert codigo == 0
    assert "Olá Ana," in texto


def test_resolver_spintax_nao_mexe_em_variavel():
    assert resolver_spintax("{Oi|Olá} {{first_name}}", 1) == "Oi {{first_name}}"
    assert resolver_spintax("{Oi|Olá|E aí} x", 3) == "E aí x"
    # variante maior que o número de opções volta ao início: 5 → 1ª de 2
    assert resolver_spintax("{Oi|Olá} x", 5) == "Oi x"
    assert resolver_spintax("{Oi|Olá} x", 4) == "Olá x"


def test_variavel_nao_declarada_falha(tmp_path, capsys):
    seq = SEQUENCIA.replace("Última ideia", "{{cargo}}, última ideia")
    codigo, _ = rodar(tmp_path, sequencia=seq)
    assert codigo == 1
    assert "{{cargo}}" in capsys.readouterr().err


def test_travessao_falha(tmp_path, capsys):
    seq = SEQUENCIA.replace("sem problema.", "sem problema \u2014 até mais.")
    codigo, _ = rodar(tmp_path, sequencia=seq)
    assert codigo == 1
    assert "travessão" in capsys.readouterr().err


def test_sequencia_sem_quatro_toques_falha(tmp_path, capsys):
    seq = SEQUENCIA.replace("## D8", "## D9")
    codigo, _ = rodar(tmp_path, sequencia=seq)
    assert codigo == 1
    assert "D8" in capsys.readouterr().err


def test_ascii_so_avisa(tmp_path, capsys):
    seq = SEQUENCIA.replace("Se não for prioridade", "Se nao for prioridade")
    codigo, _ = rodar(tmp_path, sequencia=seq)
    assert codigo == 0
    assert "nao" in capsys.readouterr().err


def test_amostra_por_segmento(tmp_path):
    codigo, texto = rodar(tmp_path, "--amostra", "1", "--por", "segmento")
    assert codigo == 0
    assert "Ana Souza" in texto
    assert "Carla Dias" in texto
    assert "Bruno Lima" not in texto


def test_csv_sem_bom_e_acentos(tmp_path):
    contatos = CABECALHO + "acao.com.br,João Araújo,João,Coordenação,Ação Cosméticos,beleza,\n"
    codigo, texto = rodar(tmp_path, contatos=contatos, bom=False)
    assert codigo == 0
    assert "Oi João," in texto
    assert "recompra na Ação Cosméticos" in texto


def test_ler_sequencia_ignora_notas_do_juiz(tmp_path):
    seq, _ = montar(tmp_path)
    sequencia = ler_sequencia(seq.read_text(encoding="utf-8"))
    assert [t.nome for t in sequencia.toques] == ["D1", "D4", "D8", "D13"]
    assert set(sequencia.variaveis) == {"first_name", "company", "primeira_frase"}
    assert all("variavel_do_juiz" not in t.corpo for t in sequencia.toques)


SEQ_VARIANTES = SEQUENCIA.replace(
    "## D1\n\nAssunto: recompra na {{company}}\n\n{Oi|Olá} {{first_name}},\n\n{{primeira_frase}}\n\n"
    "Hoje vocês sabem quantos clientes da {{company}} compraram só uma vez?\n",
    "## D1 · decisor\n\nAssunto: receita da base na {{company}}\n\n{{first_name}}, quanto da receita "
    "da {{company}} vem de quem já comprou?\n\n"
    "## D1 · champion\n\nAssunto: recompra na {{company}}\n\n{{first_name}}, quanto tempo o time "
    "gasta montando a régua de recompra?\n",
)
CONTATOS_PAPEL = (
    "domain,nome,primeiro_nome,cargo,company_name,segmento,primeira_frase,papel\n"
    "acme.com.br,Ana Souza,Ana,CEO,Acme Moda,moda,,decisor\n"
    "acme.com.br,Bruno Lima,Bruno,Head de CRM,Acme Moda,moda,,champion\n"
    "acme.com.br,Carla Dias,Carla,Head de Produto,Acme Moda,moda,,influenciador\n"
)


def test_variante_de_d1_por_papel(tmp_path):
    codigo, texto = rodar(tmp_path, sequencia=SEQ_VARIANTES, contatos=CONTATOS_PAPEL)
    assert codigo == 0
    blocos = texto.split("\n## ")[1:]
    assert "### D1 · decisor" in blocos[0] and "quanto da receita" in blocos[0]
    assert "### D1 · champion" in blocos[1] and "montando a régua" in blocos[1]
    assert "### D1 · champion" in blocos[2]
    for bloco in blocos:
        assert "### D4" in bloco and "### D13" in bloco
        assert bloco.count("### D1 ·") == 1


def test_variante_sem_papel_usa_champion_e_avisa(tmp_path, capsys):
    contatos = CONTATOS_PAPEL.replace(",decisor\n", ",\n")
    codigo, texto = rodar(tmp_path, "--linha", "1", sequencia=SEQ_VARIANTES, contatos=contatos)
    assert codigo == 0
    assert "### D1 · champion" in texto
    assert "sem papel" in capsys.readouterr().err


def test_variante_incompleta_falha(tmp_path, capsys):
    seq = SEQ_VARIANTES.replace("## D1 · champion", "## D2 · champion")
    codigo, _ = rodar(tmp_path, sequencia=seq, contatos=CONTATOS_PAPEL)
    assert codigo == 1
    assert "D1" in capsys.readouterr().err


def test_d1_simples_e_variante_juntos_falha(tmp_path, capsys):
    seq = SEQ_VARIANTES.replace("## D4\n", "## D1\n\nAssunto: x\n\nOi.\n\n## D4\n")
    codigo, _ = rodar(tmp_path, sequencia=seq, contatos=CONTATOS_PAPEL)
    assert codigo == 1
    assert "D1" in capsys.readouterr().err
