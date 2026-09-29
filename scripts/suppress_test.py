from pathlib import Path

from suppress import main, normalizar_linkedin

CAB_SUPRESSAO = "chave,tipo,motivo,origem,data,adicionado_por,nota\n"
CAB_CONTAS = (
    "dominio,empresa,rodada,segmento,trilha,veredito,tier,score,tecnografia,"
    "fato_abordagem,fonte_url,estagio,atualizado_em,nao_abordar,dono,nota\n"
)
CAB_CONTATOS = (
    "contato_id,dominio,nome,cargo,papel,canal,email,email_status,linkedin_url,"
    "rodada,atualizado_em,nao_abordar,nota\n"
)
CAB_TOQUES = (
    "toque_id,data,contato_id,dominio,canal,ferramenta,rodada,passo,evento,"
    "classificacao,respondido_por,nota\n"
)


def ledger(tmp_path: Path, supressao="", contas="", contatos="", toques="", faltando=()) -> Path:
    pasta = tmp_path / "ledger"
    pasta.mkdir()
    abas = {
        "supressao.csv": CAB_SUPRESSAO + supressao,
        "contas.csv": CAB_CONTAS + contas,
        "contatos.csv": CAB_CONTATOS + contatos,
        "toques.csv": CAB_TOQUES + toques,
    }
    for nome, texto in abas.items():
        if nome not in faltando:
            (pasta / nome).write_text(texto, encoding="utf-8")
    return pasta


def rodar(tmp_path: Path, lista_txt: str, pasta: Path, bom=False, extra=()):
    lista = tmp_path / "lista.csv"
    dados = lista_txt.encode("utf-8")
    if bom:
        dados = b"\xef\xbb\xbf" + dados
    lista.write_bytes(dados)
    saida = tmp_path / "filtrado.csv"
    removidos = tmp_path / "removidos.csv"
    codigo = main(
        ["--lista", str(lista), "--ledger-dir", str(pasta), "--saida", str(saida),
         "--removidos", str(removidos), *extra]
    )
    return codigo, saida, removidos


def linhas(caminho: Path) -> list[str]:
    return caminho.read_bytes().decode("utf-8-sig").splitlines()


def test_normalizar_linkedin():
    assert normalizar_linkedin("http://br.linkedin.com/in/Ana-Souza/?trk=x") == "https://www.linkedin.com/in/ana-souza"
    assert normalizar_linkedin("linkedin.com/in/ana-souza/") == "https://www.linkedin.com/in/ana-souza"
    assert normalizar_linkedin("https://www.linkedin.com/in/ana-souza") == "https://www.linkedin.com/in/ana-souza"
    assert normalizar_linkedin("https://www.linkedin.com/in/jos%C3%A9-lima") == normalizar_linkedin(
        "https://www.linkedin.com/in/josé-lima/"
    )
    assert normalizar_linkedin("") == ""


def test_lista_de_contas_supressao_por_dominio(tmp_path, capsys):
    pasta = ledger(tmp_path, supressao="acme.com.br,dominio,cliente,crm,2026-09-01,,\n")
    codigo, saida, removidos = rodar(
        tmp_path, "empresa,domain\nAcme,https://www.Acme.com.br/\nBeta,beta.com.br\n", pasta
    )
    assert codigo == 0
    assert linhas(saida) == ["empresa,domain", "Beta,beta.com.br"]
    assert linhas(removidos) == [
        "empresa,domain,motivo_supressao",
        "Acme,https://www.Acme.com.br/,supressao:cliente",
    ]
    resumo = capsys.readouterr().out
    assert "Total: 2" in resumo
    assert "supressao:cliente: 1" in resumo
    assert "Mantidos: 1" in resumo


def test_supressao_por_email_e_linkedin(tmp_path):
    pasta = ledger(
        tmp_path,
        supressao=(
            "ana@acme.com.br,email,optout,syndie,2026-09-01,,\n"
            "https://www.linkedin.com/in/bruno-lima,linkedin,negativacao,planilha,2026-09-01,,\n"
        ),
    )
    lista = (
        "domain,nome,email,linkedin_url\n"
        "acme.com.br,Ana Souza,ANA@acme.com.br,\n"
        "beta.com.br,Bruno Lima,,https://linkedin.com/in/Bruno-Lima/\n"
        "beta.com.br,Carla Dias,carla@beta.com.br,https://www.linkedin.com/in/carla-dias\n"
    )
    codigo, saida, removidos = rodar(tmp_path, lista, pasta)
    assert codigo == 0
    assert [l.split(",")[1] for l in linhas(saida)[1:]] == ["Carla Dias"]
    motivos = [l.rsplit(",", 1)[1] for l in linhas(removidos)[1:]]
    assert motivos == ["supressao:optout", "supressao:negativacao"]


def test_nao_abordar_conta_e_contato(tmp_path):
    pasta = ledger(
        tmp_path,
        contas="acme.com.br,Acme,r1,moda,,lista,1,80,,,,Working,2026-09-01,sim,,\n",
        contatos=(
            "beta.com.br:carla-dias,beta.com.br,Carla Dias,CRM,decisor,ambos,carla@beta.com.br,verified,"
            "https://www.linkedin.com/in/carla-dias,r1,2026-09-01,sim,\n"
        ),
    )
    lista = (
        "domain,nome,email,linkedin_url\n"
        "acme.com.br,Ana Souza,ana@acme.com.br,\n"
        "beta.com.br,Carla Dias,,https://www.linkedin.com/in/carla-dias/\n"
        "beta.com.br,Davi Reis,davi@beta.com.br,\n"
    )
    _, saida, removidos = rodar(tmp_path, lista, pasta)
    assert [l.split(",")[1] for l in linhas(saida)[1:]] == ["Davi Reis"]
    motivos = [l.rsplit(",", 1)[1] for l in linhas(removidos)[1:]]
    assert motivos == ["nao_abordar_conta", "nao_abordar_contato"]


def test_toque_sem_resposta_em_lista_de_contatos(tmp_path):
    pasta = ledger(
        tmp_path,
        contatos=(
            "acme.com.br:ana-souza,acme.com.br,Ana Souza,CRM,decisor,email,ana@acme.com.br,verified,,r1,2026-09-01,,\n"
            "acme.com.br:bruno-lima,acme.com.br,Bruno Lima,CRM,champion,email,bruno@acme.com.br,verified,,r1,2026-09-01,,\n"
        ),
        toques=(
            "acme.com.br:ana-souza:r1:D1:enviado,2026-09-02 10:00,acme.com.br:ana-souza,acme.com.br,email,apollo,r1,D1,enviado,,,\n"
            "acme.com.br:bruno-lima:r1:D1:enviado,2026-09-02 10:00,acme.com.br:bruno-lima,acme.com.br,email,apollo,r1,D1,enviado,,,\n"
            "acme.com.br:bruno-lima:r1:D1:resposta,2026-09-03 10:00,acme.com.br:bruno-lima,acme.com.br,email,gmail,r1,D1,resposta,positivo,,\n"
        ),
    )
    lista = (
        "domain,nome,email\n"
        "acme.com.br,Ana Souza,ana@acme.com.br\n"
        "acme.com.br,Bruno Lima,bruno@acme.com.br\n"
        "acme.com.br,Carla Dias,carla@acme.com.br\n"
    )
    _, saida, removidos = rodar(tmp_path, lista, pasta)
    assert [l.split(",")[1] for l in linhas(saida)[1:]] == ["Bruno Lima", "Carla Dias"]
    assert linhas(removidos)[1:] == ["acme.com.br,Ana Souza,ana@acme.com.br,toque_sem_resposta"]


def test_toque_sem_resposta_em_lista_de_contas(tmp_path):
    pasta = ledger(
        tmp_path,
        toques=(
            "a,2026-09-02 10:00,acme.com.br:ana-souza,acme.com.br,email,apollo,r1,D1,enviado,,,\n"
            "b,2026-09-02 10:00,beta.com.br:bruno-lima,beta.com.br,email,apollo,r1,D1,enviado,,,\n"
            "c,2026-09-04 10:00,beta.com.br:bruno-lima,beta.com.br,email,gmail,r1,D1,resposta,objecao,,\n"
        ),
    )
    lista = "empresa,domain\nAcme,acme.com.br\nBeta,beta.com.br\nGama,gama.com.br\n"
    _, saida, removidos = rodar(tmp_path, lista, pasta)
    assert linhas(saida) == ["empresa,domain", "Beta,beta.com.br", "Gama,gama.com.br"]
    assert linhas(removidos)[1:] == ["Acme,acme.com.br,toque_sem_resposta"]


def test_nivel_contas_ignora_linkedin_da_empresa(tmp_path, capsys):
    pasta = ledger(
        tmp_path,
        toques="a,2026-09-02 10:00,acme.com.br:ana-souza,acme.com.br,email,apollo,r1,D1,enviado,,,\n",
    )
    lista = (
        "domain,company_name,linkedin_url\n"
        "acme.com.br,Acme,https://www.linkedin.com/company/acme\n"
        "gama.com.br,Gama,https://www.linkedin.com/company/gama\n"
    )
    _, saida, removidos = rodar(tmp_path, lista, pasta, extra=("--nivel", "contas"))
    assert [l.split(",")[0] for l in linhas(saida)[1:]] == ["gama.com.br"]
    assert linhas(removidos)[1].endswith("toque_sem_resposta")
    assert "Lista de contas" in capsys.readouterr().out


def test_nivel_contatos_sem_coluna_de_contato_falha(tmp_path):
    pasta = ledger(tmp_path)
    codigo, _, _ = rodar(tmp_path, "domain\nacme.com.br\n", pasta, extra=("--nivel", "contatos"))
    assert codigo == 1


def test_aba_ausente_avisa_e_nao_falha(tmp_path, capsys):
    pasta = ledger(tmp_path, faltando=("toques.csv", "contatos.csv"))
    codigo, saida, _ = rodar(tmp_path, "domain\nacme.com.br\n", pasta)
    assert codigo == 0
    assert linhas(saida) == ["domain", "acme.com.br"]
    assert "toques.csv" in capsys.readouterr().err


def test_preserva_bom_e_acento(tmp_path):
    pasta = ledger(tmp_path, supressao="beta.com.br,dominio,concorrente,manual,2026-09-01,,\n")
    lista = "empresa,domain\nAção Cosméticos,acao.com.br\nBeta,beta.com.br\n"
    _, saida, removidos = rodar(tmp_path, lista, pasta, bom=True)
    assert saida.read_bytes().startswith(b"\xef\xbb\xbf")
    assert removidos.read_bytes().startswith(b"\xef\xbb\xbf")
    assert linhas(saida)[1] == "Ação Cosméticos,acao.com.br"


def test_coluna_de_dominio_customizada(tmp_path):
    pasta = ledger(tmp_path, supressao="'acme.com.br,dominio,pipeline,crm,2026-09-01,,\n")
    lista = "empresa,site\nAcme,www.acme.com.br\n"
    _, saida, removidos = rodar(tmp_path, lista, pasta, extra=("--col-dominio", "site"))
    assert linhas(saida) == ["empresa,site"]
    assert linhas(removidos)[1] == "Acme,www.acme.com.br,supressao:pipeline"
