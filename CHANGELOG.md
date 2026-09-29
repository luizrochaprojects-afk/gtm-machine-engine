# CHANGELOG

Formato: `versão · data · mudança · origem`. Origem diz de onde veio a mudança (cliente zero, cliente N anonimizado, decisão do mantenedor). Cada workspace declara no próprio `CLAUDE.md` a versão do motor que usa.

## v0.1.0 · 2026-10-02 · primeira versão · origem: cliente zero

Entrada final (o que a rodada do cliente zero corrigiu e o que ficou pra S2) será escrita depois dessa rodada.

Motor:

- Estrutura, `README.md`, `CLAUDE.md` (três regras), `.gitignore`.
- Doutrina de ofício: `_protocolo.md` (com promoção cliente → motor), `outbound.md`, `escrita.md`, `ai-tells.md`, `producao-com-agentes.md`. Separada linha a linha da doutrina do cliente zero; a parte de cliente foi pro workspace dele.
- Schemas: `cliente.schema.yaml`, `ledger.schema.md` (a partir de um ledger testado), `gabarito.schema.md`, `veredito.schema.json`, `contato.schema.json`, `syndie-flow.schema.json` (validado contra dois fluxos reais exportados), `syndie-upload.schema.md`, `apollo-import.schema.md`, `sequencia-email.schema.md`, `diff.template.md`.
- Template de workspace em `templates/workspace/`.
- Adaptadores: `apollo`, `syndie`, `google-sheets`, `account-guardian` (import em lote só de contas, pela interface; contatos um a um).
- Scripts com testes: `check_sanitize.py`, `normalize_domain.py`, `suppress.py` (com `--nivel contas|contatos`), `validate_syndie_flow.py`, `render_email.py`.
- 13 skills: `setup-workspace`, `voz-do-cliente`, `montar-tam`, `validar-lista`, `detectar-tecnografia`, `mapear-comite`, `copy-email`, `juiz-de-copy`, `apollo-sequence-builder`, `syndie-flow-builder` (com dois fluxos de referência anonimizados), `qa-lancamento`, `registrar-ledger`, `loop-de-licoes`.

Playbooks:

- `playbooks/onboarding.md` e `playbooks/checklist-acesso.md`.

Teste de cliente novo: workspace e ledger de um cliente fictício gerados pela `setup-workspace` sem nenhum dado do cliente zero; apagados depois. O teste corrigiu:

- `adapters/google-sheets/README.md`: máscara de campos do `repeatCell` com parênteses é recusada pelo conector; trocada por caminhos completos. Confirmado que `create_file` cria planilha sem conteúdo.
- `schemas/cliente.schema.yaml`: `supressao` aceita lista vazia, como a `setup-workspace` já dizia.

Incorporado de playbooks públicos de GTM (decisão do mantenedor):

- `qa-lancamento`: SPF, DKIM e DMARC do domínio remetente; só email `verified`, sem caixa genérica.
- `doutrina/outbound.md`: seção de entregabilidade (teto de bounce de 2%, 30 por caixa, domínio secundário como padrão) e hipótese de mensagem por nível do contato.
- `copy-email`, `schemas/sequencia-email.schema.md`, `scripts/render_email.py`: D1 em duas variantes, decisor e champion [hipótese]; `apollo-sequence-builder` cria uma sequência por nível.
- `juiz-de-copy`: o comprador cético é sintético, montado da extração da `voz-do-cliente`, com cada reação ligada a uma citação.
- `apollo-sequence-builder`: `sequence_same_company_in_same_campaign` ligado; desligado, o Apollo recusava o segundo contato da mesma conta.

Edição pública (decisão do mantenedor):

- `check_sanitize.py` varre todo arquivo que o git versionaria, não só as pastas do motor, olha também o caminho do arquivo e mostra o número do termo em vez do termo.
- `README.md` em inglês; o original em português está em `README.pt-BR.md`.

Ainda não validado: nenhuma skill rodou numa rodada real. A validação é a r1 do cliente zero.
