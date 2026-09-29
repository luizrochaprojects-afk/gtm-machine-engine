// Workflow de validação de contas contra o gabarito de ICP do workspace ativo.
// Usado pela skill validar-lista. Não tem regra de cliente embutida: gabarito,
// ofertas, tecnografia alvo, regras de abertura e contas chegam em DADOS.
//
// Três modos, cada um rodado como workflow separado (a verificação adversarial
// nunca é segundo estágio do mesmo pipeline, porque é a primeira coisa cortada
// quando o orçamento acaba):
//   validacao   · 1 agente por conta: pesquisa, critérios com evidência, rascunho da abertura
//   adversarial · 1 agente por conta com score >= limiar: tenta derrubar gate e anti-ICP
//   abertura    · contas P0 e lista agrupadas por vertical: 5 testes + leitura fria
//
// Como a skill preenche:
//   (1) montar o objeto DADOS (formato no comentário abaixo) a partir do workspace;
//   (2) colar o JSON no lugar de `null` entre os marcadores DADOS_EMBUTIDOS
//       (preferido: embutir direto), ou passar como `args` do Workflow;
//   (3) invocar com o Workflow tool. Um modo por invocação.
//
// Armadilhas (testadas em produção):
//   - Date.now(), Math.random() e new Date() sem argumento não existem no script.
//     A data de hoje chega em DADOS.hoje. Datas são comparadas com Date.UTC.
//   - `args` pode chegar como string JSON: tratar com JSON.parse.
//   - O score, o veredito, o tier e a trilha são calculados aqui, no código,
//     a partir dos critérios que o agente marcou. O agente não dá nota.
//
// Formato de DADOS:
// {
//   "modo": "validacao" | "adversarial" | "abertura",
//   "hoje": "AAAA-MM-DD",
//   "rodada": "<nome da rodada>",
//   "cliente": { "definicao_icp": "<parágrafo do gabarito>", "o_que_vende": "<uma frase>" },
//   "gabarito": {
//     "versao": "<n>",
//     "criterios": [ { "id": "F1", "nome": "...", "papel": "gate|qualifica|dimensiona|sinal|pergunta|duro|validacao",
//                      "oferta": null | "<id da oferta>", "como_verificar": "...", "fonte_aceita": "...",
//                      "peso": 30 | null, "validade": 90 | null } ],
//     "faixas": { "P0": 80, "lista": 60, "nutrir": 40 },
//     "teto_sinais": 20,
//     "limiar_adversarial": 60,
//     "tier": [ { "tier": 1, "vereditos": ["P0"], "exige_dimensiona": true },
//               { "tier": 2, "vereditos": ["P0", "lista"], "exige_dimensiona": false },
//               { "tier": 3, "vereditos": ["P0", "lista", "nutrir"], "exige_dimensiona": false } ],
//     "regra_trilha": "<texto do gabarito>"
//   },
//   "ofertas": [ { "id": "...", "nome": "...", "porta_de_entrada": "...", "resumo": "..." } ],
//   "tecnografia_alvo": [ { "nome": "...", "categoria": "...", "leitura": "fit|troca|concorrente" } ],
//   "regras_abertura": "<regras da primeira_frase da doutrina/outbound.md + proibidos da doutrina-cliente.md>",
//   "exemplos_reprovados": [ { "linha": "...", "porque": "...", "reescrita": "..." } ],
//   "teto_busca": { "websearch": 2, "tool_calls": 10 },
//   "items": [ ... ]   // por modo, ver abaixo
// }
// items no modo validacao:   { domain, company_name, website, linkedin_url, employees, industry, seed, tecnografia: [...] }
//   (tecnografia no formato do campo tecnografia de schemas/veredito.schema.json, vindo da detectar-tecnografia)
// items no modo adversarial: { veredito: <objeto do veredito.schema.json>, website, seed }
// items no modo abertura:    { veredito: <objeto do veredito.schema.json>, vertical }

export const meta = {
  name: 'validacao-icp',
  description: 'Valida contas contra o gabarito de ICP do workspace, com pesquisa web, verificação adversarial e revisão da abertura',
  phases: [
    { title: 'Validação', detail: '1 agente por conta: negócio real, critérios do gabarito com evidência, rascunho da abertura' },
    { title: 'Verificação adversarial', detail: 'tenta derrubar gate e anti-ICP nas contas de score alto' },
    { title: 'Abertura', detail: 'passada dos 5 testes por vertical' },
    { title: 'Leitura fria', detail: 'olhos sem contexto leem só a linha e a evidência' },
  ],
}

// >>> DADOS_EMBUTIDOS: substituir null pelo JSON de DADOS <<<
const DADOS_EMBUTIDOS = null
// <<< FIM DADOS_EMBUTIDOS >>>

const DADOS = DADOS_EMBUTIDOS || (typeof args === 'string' ? JSON.parse(args) : args)
if (!DADOS || !DADOS.modo || !Array.isArray(DADOS.items)) {
  throw new Error('DADOS ausente ou incompleto: embutir o JSON ou passar em args')
}
if (!/^\d{4}-\d{2}-\d{2}$/.test(DADOS.hoje || '')) {
  throw new Error('DADOS.hoje precisa estar no formato AAAA-MM-DD')
}

const G = DADOS.gabarito
const OFERTAS = DADOS.ofertas || []
const HOJE = DADOS.hoje
const FAIXAS = G.faixas || { P0: 80, lista: 60, nutrir: 40 }
const TETO_SINAIS = G.teto_sinais == null ? 20 : G.teto_sinais
const LIMIAR_ADV = G.limiar_adversarial == null ? 60 : G.limiar_adversarial
const TIER_REGRAS = G.tier || [
  { tier: 1, vereditos: ['P0'], exige_dimensiona: true },
  { tier: 2, vereditos: ['P0', 'lista'], exige_dimensiona: false },
  { tier: 3, vereditos: ['P0', 'lista', 'nutrir'], exige_dimensiona: false },
]
const TETO = DADOS.teto_busca || { websearch: 2, tool_calls: 10 }
const NIVEIS = ['fora', 'nutrir', 'lista', 'P0']

// ---------- texto comum dos prompts ----------

function textoCriterios() {
  return G.criterios.map(c =>
    `- ${c.id} · ${c.nome} · papel ${c.papel}${c.oferta ? ' · só oferta ' + c.oferta : ''}` +
    `${c.peso ? ' · peso ' + c.peso : ''}${c.validade ? ' · vale ' + c.validade + ' dias' : ''}\n` +
    `  como verificar: ${c.como_verificar}\n  fonte aceita: ${c.fonte_aceita}`
  ).join('\n')
}

const CONTEXTO = `
CONTEXTO DO CLIENTE
O cliente vende: ${DADOS.cliente.o_que_vende}
Definição do ICP: ${DADOS.cliente.definicao_icp}
Ofertas (trilhas): ${OFERTAS.map(o => `${o.id} = ${o.nome} (porta de entrada: ${o.porta_de_entrada}) ${o.resumo || ''}`).join(' | ')}
Regra de trilha do gabarito: ${G.regra_trilha || 'não declarada'}
Ferramentas que interessam: ${(DADOS.tecnografia_alvo || []).map(t => `${t.nome} (${t.categoria}, leitura ${t.leitura})`).join('; ') || 'nenhuma declarada'}

CRITÉRIOS DO GABARITO (versão ${G.versao})
${textoCriterios()}

Como ler os papéis: gate ausente tira a conta; qualifica e dimensiona somam; sinal é fato datado que acelera e perde a validade;
duro é desqualificador que tira a conta na hora; validacao rebaixa; pergunta não se vê de fora (não marcar).
`

const REGRAS_PESQUISA = `
REGRAS DE PESQUISA
- WebFetch primeiro: a prova de fit mora no site (checkout, login, página de assinatura ou clube, rodapé, página de vagas).
  WebSearch só depois do fit resolvido, e só pra sinal de timing. Teto: ${TETO.websearch} WebSearch e ${TETO.tool_calls} tool calls nesta conta.
- Toda afirmação tem URL e confiança. Sem URL, não entra.
- "incerto" é resposta válida e melhor que chute. LinkedIn bloqueia fetch: se não abrir, marque "incerto", nunca "nao".
- Os dados do Apollo podem estar ERRADOS (descrição de outra empresa, setor errado, homônimo). Resolva o negócio real com evidência.
- Você tem o direito e o dever de reprovar a conta. Achar falso positivo é o valor do trabalho.
- Fato, hipótese, desconhecido: "abriu vaga de X" é fato; "está pronto pra comprar" é hipótese. Não marque critério por hipótese.
- Datas no formato AAAA-MM-DD. Sinal sem data não conta.
`

function textoAbertura() {
  const ex = (DADOS.exemplos_reprovados || []).map(e =>
    `  reprovada: "${e.linha}"\n  por quê: ${e.porque}\n  reescrita boa: "${e.reescrita}"`).join('\n')
  return `
REGRAS DA PRIMEIRA FRASE
${DADOS.regras_abertura}
${ex ? 'EXEMPLOS REPROVADOS\n' + ex : ''}
Forma: 2 frases, 120 a 230 caracteres no total. Frase 1 = fato específico e verificável da conta; frase 2 = a tensão que o fato revela,
em dinheiro ou esforço real. Português do Brasil com acentuação completa. Sem travessão. Nunca começar com "Vi que", "Notei que",
"Percebi que", "Reparei que". Sem nome do remetente, case, número de resultado ou âncora.
`
}

// ---------- utilidades ----------

function diaUTC(s) {
  const m = /^(\d{4})-(\d{2})-(\d{2})$/.exec(s || '')
  return m ? Date.UTC(+m[1], +m[2] - 1, +m[3]) : null
}
function diasEntre(a, b) {
  const x = diaUTC(a), y = diaUTC(b)
  return x == null || y == null ? null : Math.round((y - x) / 86400000)
}
function nivelAbaixo(v) { return NIVEIS[Math.max(0, NIVEIS.indexOf(v) - 1)] }
function vereditoPorScore(s) {
  if (s >= FAIXAS.P0) return 'P0'
  if (s >= FAIXAS.lista) return 'lista'
  if (s >= FAIXAS.nutrir) return 'nutrir'
  return 'fora'
}
function tetoDaFaixa(v) {
  if (v === 'fora') return FAIXAS.nutrir - 1
  if (v === 'nutrir') return FAIXAS.lista - 1
  if (v === 'lista') return FAIXAS.P0 - 1
  return 100
}
function juntarObs(...partes) { return partes.filter(p => p && String(p).trim()).join(' | ') }

// QA mecânico da primeira_frase. Não substitui a leitura editorial.
const ASCII_SUSPEITO = /\b(voce|voces|nao|tambem|entao|ninguem|alguem|porem|publico|unico|proprio|propria|numero|historico|operacao|informacao|comunicacao|ja|sera|estao)\b/i
const ABERTURA_BANIDA = /^\s*(vi que|notei que|percebi que|reparei que|espero que|passando pra|dei uma olhada)/i
function qaFrase(f) {
  if (!f) return null
  const t = f.trim()
  if (t.length < 120 || t.length > 230) return `tamanho ${t.length} fora de 120 a 230`
  const frases = t.split(/(?<=[.!?])\s+/).filter(s => s.trim())
  if (frases.length !== 2) return `${frases.length} frases em vez de 2`
  if (t.includes('\u2014')) return 'travessão'
  if (ABERTURA_BANIDA.test(t)) return 'abertura banida'
  if (/\{\{|\}\}/.test(t)) return 'merge tag na frase'
  if (ASCII_SUSPEITO.test(t)) return 'palavra sem acento'
  return null
}

// ---------- cálculo do veredito (determinístico) ----------
// crit: { [id]: { met: 'sim'|'nao'|'incerto', evidencia_idx: [..] } }
// evid: evidencias[] do veredito
function pontuar(crit, evid, trilhaSugerida) {
  const C = G.criterios
  const met = id => (crit[id] && crit[id].met) || 'incerto'
  const notas = []

  // desqualificador duro
  const duro = C.find(c => c.papel === 'duro' && met(c.id) === 'sim')
  const gatesComuns = C.filter(c => c.papel === 'gate' && !c.oferta)
  const gateComumAusente = gatesComuns.find(c => met(c.id) === 'nao')
  const gateComumIncerto = gatesComuns.some(c => met(c.id) === 'incerto')

  // ofertas possíveis (nenhum gate da oferta ausente) e elegíveis (todos os gates da oferta confirmados)
  const idsOferta = OFERTAS.map(o => o.id)
  const gatesDe = o => C.filter(c => c.papel === 'gate' && c.oferta === o)
  const possiveis = idsOferta.filter(o => !gatesDe(o).some(c => met(c.id) === 'nao'))
  const elegiveis = possiveis.filter(o => gatesDe(o).every(c => met(c.id) === 'sim'))

  // fit por oferta: critérios comuns + os da oferta, normalizado a 100
  const fitDe = o => {
    const conj = C.filter(c => ['gate', 'qualifica', 'dimensiona'].includes(c.papel) && (!c.oferta || c.oferta === o) && c.peso)
    const tot = conj.reduce((s, c) => s + c.peso, 0)
    const pts = conj.filter(c => met(c.id) === 'sim').reduce((s, c) => s + c.peso, 0)
    return { fit: tot ? Math.round((100 * pts) / tot) : 0, dimensiona: conj.filter(c => c.papel === 'dimensiona').every(c => met(c.id) === 'sim') }
  }
  // sem oferta possível (ou sem ofertas), o fit sai só dos critérios comuns
  const candidatas = possiveis.length ? possiveis : [null]
  let melhor = null
  for (const o of candidatas) {
    const r = fitDe(o)
    if (!melhor || r.fit > melhor.fit) melhor = { oferta: o, ...r }
  }

  // bônus de sinais válidos na data
  let bonus = 0
  for (const c of C.filter(c => c.papel === 'sinal' && met(c.id) === 'sim')) {
    const idx = (crit[c.id].evidencia_idx || []).filter(i => evid[i])
    const datas = idx.map(i => evid[i].data).filter(Boolean)
    if (!datas.length) { notas.push(`sinal ${c.id} sem data, não somou`); continue }
    const idade = Math.min(...datas.map(d => diasEntre(d, HOJE)).filter(x => x != null))
    if (c.validade && idade > c.validade) { notas.push(`sinal ${c.id} vencido (${idade} dias)`); continue }
    bonus += c.peso || 0
  }
  bonus = Math.min(bonus, TETO_SINAIS)

  let score = Math.min(100, melhor.fit + bonus)
  let veredito = vereditoPorScore(score)
  let is_anti_icp = false
  let motivo_anti_icp = ''

  if (duro) {
    is_anti_icp = true
    motivo_anti_icp = `${duro.id} · ${duro.nome}`
    veredito = 'fora'
  } else if (gateComumAusente) {
    veredito = 'fora'
    notas.push(`gate ${gateComumAusente.id} ausente`)
  } else if (idsOferta.length && C.some(c => c.papel === 'gate' && c.oferta) && !possiveis.length) {
    veredito = 'fora'
    notas.push('nenhuma oferta com gates atendidos')
  } else {
    const gateIncerto = gateComumIncerto || (melhor.oferta && gatesDe(melhor.oferta).some(c => met(c.id) === 'incerto'))
    if (gateIncerto && veredito === 'P0') { veredito = 'lista'; notas.push('gate incerto: teto lista') }
    const val = C.filter(c => c.papel === 'validacao' && met(c.id) === 'sim')
    for (const v of val) { veredito = nivelAbaixo(veredito); notas.push(`rebaixada por ${v.id} · ${v.nome}`) }
  }
  // score fica dentro da faixa do veredito final (rebaixada por regra = score no teto da faixa nova)
  score = Math.max(0, Math.min(score, tetoDaFaixa(veredito)))

  // tier
  let tier = null
  if (veredito !== 'fora') {
    for (const r of TIER_REGRAS) {
      if (r.vereditos.includes(veredito) && (!r.exige_dimensiona || melhor.dimensiona)) { tier = r.tier; break }
    }
    if (tier == null) tier = 3
  }

  // trilha
  let trilha = 'incerta'
  if (idsOferta.length === 1) trilha = idsOferta[0]
  else if (elegiveis.length === 1) trilha = elegiveis[0]
  else if (elegiveis.length > 1 && idsOferta.length === 2) trilha = 'ambas'
  else if (elegiveis.length > 1 && elegiveis.includes(trilhaSugerida)) trilha = trilhaSugerida
  else if (!elegiveis.length && possiveis.length === 1 && possiveis[0] === trilhaSugerida) trilha = trilhaSugerida

  const gateIncertoFinal = gateComumIncerto || (melhor.oferta && gatesDe(melhor.oferta).some(c => met(c.id) === 'incerto'))
  return { score, veredito, tier, trilha, is_anti_icp, motivo_anti_icp, notas, gateIncerto: !!gateIncertoFinal }
}

// monta o objeto final no formato de schemas/veredito.schema.json
function montarVeredito(base, r, extra) {
  const v = {
    domain: base.domain,
    company_name: base.company_name,
    veredito: r.veredito,
    tier: r.tier,
    trilha: r.trilha,
    score: r.score,
    is_anti_icp: r.is_anti_icp,
    criterios: extra.criterios,
    evidencias: extra.evidencias,
    tecnografia: extra.tecnografia,
    primeira_frase: '',
    adversarial: extra.adversarial || { rodou: false },
    revisar_no_h1: false,
    obs: '',
  }
  if (r.is_anti_icp) v.motivo_anti_icp = r.motivo_anti_icp
  let obs = extra.obs || ''
  if (['P0', 'lista'].includes(r.veredito) && extra.primeira_frase) {
    const erro = qaFrase(extra.primeira_frase)
    const idx = extra.primeira_frase_evidencia_idx
    const refutado = (v.adversarial.fatos_refutados || []).includes((v.evidencias[idx] || {}).fato)
    if (erro) obs = juntarObs(obs, `primeira_frase reprovada no QA mecânico (${erro}), reescrever`)
    else if (idx == null || idx < 0 || !v.evidencias[idx]) obs = juntarObs(obs, 'primeira_frase sem evidência apontada, reescrever')
    else if (refutado) obs = juntarObs(obs, 'fato da primeira_frase refutado, reescrever')
    else { v.primeira_frase = extra.primeira_frase.trim(); v.primeira_frase_evidencia_idx = idx }
  }
  v.obs = juntarObs(obs, r.notas.join('; '))
  v.revisar_no_h1 = r.veredito === 'P0' || r.gateIncerto || !!extra.revisar
  return v
}

// ---------- schemas de saída dos agentes ----------

const EVID = {
  type: 'object', additionalProperties: false,
  required: ['fato', 'url', 'confianca', 'data'],
  properties: {
    fato: { type: 'string', minLength: 1 },
    url: { type: 'string', pattern: '^https?://' },
    confianca: { type: 'string', enum: ['alta', 'media', 'baixa'] },
    data: { type: 'string', pattern: '^(\\d{4}-\\d{2}-\\d{2})?$', description: 'AAAA-MM-DD do fato (ou da checagem, se o fato não tem data). Vazio se não souber.' },
  },
}
const TEC = {
  type: 'object', additionalProperties: false,
  required: ['ferramenta', 'fonte', 'tipo_evidencia', 'confianca', 'leitura'],
  properties: {
    ferramenta: { type: 'string' },
    fonte: { type: 'string', pattern: '^https?://' },
    tipo_evidencia: { type: 'string', enum: ['script_html', 'vaga', 'mencao_publica', 'apollo'] },
    confianca: { type: 'string', enum: ['alta', 'media', 'baixa'] },
    leitura: { type: 'string', enum: ['fit', 'troca', 'concorrente'] },
  },
}
const AVAL = {
  type: 'object', additionalProperties: false,
  required: ['domain', 'negocio_real', 'dominio_confere', 'evidencias', 'criterios', 'trilha_sugerida', 'trilha_motivo',
    'primeira_frase', 'primeira_frase_evidencia_idx', 'tecnografia_nova', 'sem_verificacao', 'confianca'],
  properties: {
    domain: { type: 'string' },
    negocio_real: { type: 'string', description: 'O que a empresa vende e pra quem, em uma frase, com o conflito do Apollo resolvido.' },
    dominio_confere: { type: 'string', enum: ['sim', 'nao', 'incerto'], description: 'O domínio da lista é mesmo desta empresa?' },
    evidencias: { type: 'array', items: EVID },
    criterios: {
      type: 'array',
      items: {
        type: 'object', additionalProperties: false,
        required: ['id', 'met', 'evidencia_idx', 'nota'],
        properties: {
          id: { type: 'string' },
          met: { type: 'string', enum: ['sim', 'nao', 'incerto'] },
          evidencia_idx: { type: 'array', items: { type: 'integer', minimum: 0 } },
          nota: { type: 'string' },
        },
      },
    },
    trilha_sugerida: { type: 'string', description: 'id de oferta, "ambas" ou "incerta"' },
    trilha_motivo: { type: 'string' },
    primeira_frase: { type: 'string', description: 'Rascunho da abertura. Vazio se a conta não passa nos gates.' },
    primeira_frase_evidencia_idx: { type: 'integer', minimum: -1, description: 'Índice em evidencias do fato da frase 1; -1 se sem frase.' },
    tecnografia_nova: { type: 'array', items: TEC, description: 'Só ferramenta da lista de interesse achada agora e que não estava na tecnografia recebida.' },
    sem_verificacao: { type: 'string', description: 'O que ficou sem verificar e por quê.' },
    confianca: { type: 'string', enum: ['alta', 'media', 'baixa'] },
  },
}
const ADV = {
  type: 'object', additionalProperties: false,
  required: ['domain', 'gates', 'anti_icp', 'fatos_refutados_idx', 'evidencias_novas', 'nota'],
  properties: {
    domain: { type: 'string' },
    gates: {
      type: 'array',
      items: {
        type: 'object', additionalProperties: false,
        required: ['id', 'confirmado', 'justificativa', 'url'],
        properties: {
          id: { type: 'string' },
          confirmado: { type: 'string', enum: ['sim', 'nao', 'incerto'] },
          justificativa: { type: 'string' },
          url: { type: 'string' },
        },
      },
    },
    anti_icp: {
      type: 'object', additionalProperties: false,
      required: ['e_anti_icp', 'criterio_id', 'motivo', 'url'],
      properties: {
        e_anti_icp: { type: 'boolean', description: 'true se algum desqualificador duro se aplica' },
        criterio_id: { type: 'string' },
        motivo: { type: 'string' },
        url: { type: 'string' },
      },
    },
    fatos_refutados_idx: { type: 'array', items: { type: 'integer', minimum: 0 }, description: 'Índices em evidencias que são falsos, exagerados ou de outra empresa.' },
    evidencias_novas: { type: 'array', items: EVID },
    nota: { type: 'string' },
  },
}
const ABR = {
  type: 'object', additionalProperties: false, required: ['linhas'],
  properties: {
    linhas: {
      type: 'array',
      items: {
        type: 'object', additionalProperties: false,
        required: ['domain', 'primeira_frase', 'evidencia_idx', 'testes_reprovados', 'nota'],
        properties: {
          domain: { type: 'string' },
          primeira_frase: { type: 'string', description: 'Linha final; vazio se nenhuma versão passa nos 5 testes com os fatos disponíveis.' },
          evidencia_idx: { type: 'integer', minimum: -1 },
          testes_reprovados: { type: 'array', items: { type: 'string', enum: ['intercambiabilidade', 'e_dai', 'culpa', 'como_sabe', 'voz'] } },
          nota: { type: 'string' },
        },
      },
    },
  },
}
const FRIA = {
  type: 'object', additionalProperties: false, required: ['leituras'],
  properties: {
    leituras: {
      type: 'array',
      items: {
        type: 'object', additionalProperties: false,
        required: ['domain', 'aprovada', 'problema'],
        properties: { domain: { type: 'string' }, aprovada: { type: 'boolean' }, problema: { type: 'string' } },
      },
    },
  },
}

// ---------- modo validacao ----------

async function modoValidacao() {
  phase('Validação')
  const ids = new Set(G.criterios.map(c => c.id))
  const verificaveis = G.criterios.filter(c => c.papel !== 'pergunta').map(c => c.id)
  const res = await pipeline(DADOS.items, (c) => agent(
`${CONTEXTO}
${REGRAS_PESQUISA}
${textoAbertura()}

Você é analista de qualificação de contas. Pesquise NA INTERNET a empresa abaixo e verifique cada critério do gabarito.

EMPRESA
- Nome: ${c.company_name}
- Domínio: ${c.domain}
- Site: ${c.website || 'https://' + c.domain}
- LinkedIn: ${c.linkedin_url || 'não informado'}
- Funcionários (Apollo): ${c.employees || 'não informado'}
- Setor (Apollo): ${c.industry || 'não informado'}
- Notas do Apollo e da lista (podem estar ERRADAS, confirme): ${c.seed || 'nenhuma'}
- Tecnografia já detectada (detectar-tecnografia): ${JSON.stringify(c.tecnografia || [])}

TAREFAS
1) Negócio real: o que vende e pra quem. Confirme se o domínio é mesmo desta empresa (dominio_confere).
2) Marque cada critério ${verificaveis.join(', ')} como sim, nao ou incerto, apontando os índices das evidências.
   Critério de ferramenta: use a tecnografia recebida; acrescente em tecnografia_nova só o que achar de novo, com fonte.
3) Sinais: só com data. Desqualificador duro: marque sim se se aplica, com a evidência.
4) trilha_sugerida pela regra de trilha do gabarito, com o motivo.
5) Se nenhum gate está ausente e nenhum desqualificador duro se aplica, escreva o rascunho da primeira_frase ancorado numa
   evidência (primeira_frase_evidencia_idx). Senão, primeira_frase vazia e índice -1.
6) sem_verificacao: o que ficou de fora e por quê.

Responda SÓ com o objeto estruturado.`,
    { label: `val:${c.domain.slice(0, 24)}`, phase: 'Validação', schema: AVAL, agentType: 'general-purpose' }
  ), (a, c) => {
    if (!a) return null
    const crit = {}
    for (const x of a.criterios || []) {
      if (!ids.has(x.id)) continue
      crit[x.id] = { met: x.met, evidencia_idx: (x.evidencia_idx || []).filter(i => i >= 0 && i < a.evidencias.length) }
    }
    const evidencias = a.evidencias.map(e => {
      const o = { fato: e.fato, url: e.url, confianca: e.confianca }
      if (e.data) o.data = e.data
      return o
    })
    const r = pontuar(crit, evidencias, a.trilha_sugerida)
    const criterios = verificaveis.map(id => {
      const x = crit[id] || { met: 'incerto', evidencia_idx: [] }
      const o = { id, met: x.met }
      if (x.evidencia_idx.length) o.evidencia_idx = x.evidencia_idx
      return o
    })
    const tecnografia = [...(c.tecnografia || []), ...(a.tecnografia_nova || [])]
    return montarVeredito(c, r, {
      criterios, evidencias, tecnografia,
      primeira_frase: a.primeira_frase,
      primeira_frase_evidencia_idx: a.primeira_frase_evidencia_idx,
      adversarial: { rodou: false },
      revisar: a.dominio_confere !== 'sim',
      obs: juntarObs(
        `negócio real: ${a.negocio_real}`,
        a.dominio_confere !== 'sim' ? `domínio ${a.dominio_confere === 'nao' ? 'não é' : 'talvez não seja'} desta empresa` : '',
        `trilha: ${a.trilha_motivo}`,
        a.sem_verificacao ? `sem verificação: ${a.sem_verificacao}` : '',
        `confiança ${a.confianca}`,
        r.score >= LIMIAR_ADV && r.veredito !== 'fora' ? 'aguarda verificação adversarial' : ''
      ),
    })
  })
  const ok = res.filter(Boolean)
  log(`${ok.length} de ${DADOS.items.length} contas com veredito; ${DADOS.items.length - ok.length} sem resposta do agente`)
  return ok
}

// ---------- modo adversarial ----------

async function modoAdversarial() {
  phase('Verificação adversarial')
  const itens = DADOS.items.filter(i => i.veredito.veredito !== 'fora' && i.veredito.score >= LIMIAR_ADV)
  const pulados = DADOS.items.length - itens.length
  if (pulados) log(`${pulados} contas abaixo do limiar ${LIMIAR_ADV} ou fora: sem verificação adversarial`)
  const gates = G.criterios.filter(c => c.papel === 'gate')
  const duros = G.criterios.filter(c => c.papel === 'duro')

  const res = await pipeline(itens, (it) => {
    const v = it.veredito
    const ev = v.evidencias.map((e, i) => `  [${i}] ${e.fato} (${e.url}, ${e.confianca}${e.data ? ', ' + e.data : ''})`).join('\n')
    return agent(
`${CONTEXTO}
${REGRAS_PESQUISA}

VERIFICAÇÃO ADVERSARIAL. Uma primeira passada deu à conta "${v.company_name}" (${it.website || v.domain}) o veredito ${v.veredito},
score ${v.score}, trilha ${v.trilha}. Observações da primeira passada: ${v.obs}

EVIDÊNCIAS ALEGADAS
${ev}

Sua missão é TENTAR DERRUBAR. Pesquise de novo, cético:
1) Cada gate (${gates.map(g => g.id + ' ' + g.nome).join('; ')}): o fato existe MESMO, ou foi inferência otimista?
   Na dúvida, "incerto".
2) Algum desqualificador duro (${duros.map(d => d.id + ' ' + d.nome).join('; ') || 'nenhum declarado'}) se aplica?
   É comprador de verdade ou é agência, parceiro, B2B disfarçado, compra única?
3) Aponte os índices das evidências falsas, exageradas, desatualizadas ou de outra empresa (fatos_refutados_idx).
   Número que você não consegue confirmar é refutado.
4) evidencias_novas: o que você achou que muda a leitura, com URL.

Responda SÓ com o objeto estruturado.`,
      { label: `adv:${v.domain.slice(0, 24)}`, phase: 'Verificação adversarial', schema: ADV, agentType: 'general-purpose' })
  }, (a, it) => {
    const v = JSON.parse(JSON.stringify(it.veredito))
    if (!a) {
      v.adversarial = { rodou: false, nota: 'agente adversarial sem resposta' }
      v.revisar_no_h1 = true
      const semAguarda = String(v.obs || '').split(' | ').filter(p => p !== 'aguarda verificação adversarial').join(' | ')
      v.obs = juntarObs(semAguarda, 'verificação adversarial não rodou')
      return v
    }
    const antes = v.veredito
    const refutadosIdx = (a.fatos_refutados_idx || []).filter(i => v.evidencias[i])
    const refutados = refutadosIdx.map(i => v.evidencias[i].fato)
    const novas = (a.evidencias_novas || []).map(e => { const o = { fato: e.fato, url: e.url, confianca: e.confianca }; if (e.data) o.data = e.data; return o })
    const evidencias = [...v.evidencias, ...novas]

    // critério cuja única sustentação foi refutada volta a incerto
    const crit = {}
    for (const c of v.criterios || []) {
      const idx = (c.evidencia_idx || []).filter(i => !refutadosIdx.includes(i))
      crit[c.id] = { met: c.met, evidencia_idx: idx }
      if (c.met === 'sim' && (c.evidencia_idx || []).length && !idx.length) crit[c.id].met = 'incerto'
    }
    for (const g of a.gates || []) {
      if (!crit[g.id]) continue
      if (g.confirmado === 'nao') crit[g.id].met = 'nao'
      else if (g.confirmado === 'incerto' && crit[g.id].met === 'sim') crit[g.id].met = 'incerto'
    }
    if (a.anti_icp.e_anti_icp && crit[a.anti_icp.criterio_id]) crit[a.anti_icp.criterio_id].met = 'sim'

    let r = pontuar(crit, evidencias, v.trilha)
    if (a.anti_icp.e_anti_icp && !r.is_anti_icp) {
      r = { ...r, veredito: 'fora', tier: null, score: Math.min(r.score, FAIXAS.nutrir - 1), is_anti_icp: true, motivo_anti_icp: a.anti_icp.motivo }
    }
    // na dúvida sobre gate, rebaixa
    if ((a.gates || []).some(g => g.confirmado === 'incerto') && r.veredito === antes && antes !== 'fora') {
      const novo = nivelAbaixo(antes)
      r = { ...r, veredito: novo, score: Math.min(r.score, tetoDaFaixa(novo)), notas: [...r.notas, 'gate incerto na adversarial: rebaixada'] }
      if (novo === 'fora') r.tier = null
    }
    const resultado = r.veredito === 'fora' && antes !== 'fora' ? 'derrubado'
      : NIVEIS.indexOf(r.veredito) < NIVEIS.indexOf(antes) ? 'rebaixado' : 'mantido'
    const criterios = Object.keys(crit).map(id => {
      const o = { id, met: crit[id].met }
      if (crit[id].evidencia_idx.length) o.evidencia_idx = crit[id].evidencia_idx
      return o
    })
    const adversarial = { rodou: true, resultado, fatos_refutados: refutados, nota: a.nota }
    const obsBase = String(v.obs || '').split(' | ').filter(p => p !== 'aguarda verificação adversarial').join(' | ')
    return montarVeredito(v, r, {
      criterios, evidencias, tecnografia: v.tecnografia,
      primeira_frase: v.primeira_frase,
      primeira_frase_evidencia_idx: v.primeira_frase_evidencia_idx,
      adversarial,
      revisar: v.revisar_no_h1 || resultado !== 'mantido' || refutados.length > 0,
      obs: juntarObs(obsBase, `adversarial: ${resultado}${refutados.length ? ', ' + refutados.length + ' fato(s) refutado(s)' : ''}`,
        a.anti_icp.e_anti_icp ? `anti-ICP: ${a.anti_icp.motivo}` : ''),
    })
  })

  const porDominio = {}
  for (const v of res.filter(Boolean)) porDominio[v.domain] = v
  return DADOS.items.map(i => porDominio[i.veredito.domain] || (() => {
    const v = JSON.parse(JSON.stringify(i.veredito))
    if (!v.adversarial) v.adversarial = { rodou: false }
    return v
  })())
}

// ---------- modo abertura ----------

async function modoAbertura() {
  const alvo = DADOS.items.filter(i => ['P0', 'lista'].includes(i.veredito.veredito))
  const porVertical = {}
  for (const i of alvo) (porVertical[i.vertical || 'sem-vertical'] ||= []).push(i)
  const grupos = []
  for (const [vert, lista] of Object.entries(porVertical)) {
    for (let k = 0; k < lista.length; k += 8) grupos.push({ vertical: vert, contas: lista.slice(k, k + 8) })
  }
  log(`${alvo.length} contas P0 e lista em ${grupos.length} grupos por vertical`)

  const bloco = (i) => {
    const v = i.veredito
    const refut = (v.adversarial && v.adversarial.fatos_refutados) || []
    const ev = v.evidencias.map((e, k) => refut.includes(e.fato) ? null : `    [${k}] ${e.fato} (${e.data || 'sem data'})`).filter(Boolean).join('\n')
    return `- ${v.company_name} (${v.domain}) · trilha ${v.trilha}\n  rascunho: "${v.primeira_frase || ''}"\n  evidências utilizáveis:\n${ev}\n  PROIBIDO usar: ${refut.join(' / ') || 'nada'}`
  }

  phase('Abertura')
  const res = await pipeline(grupos, (g) => agent(
`${CONTEXTO}
${textoAbertura()}

Você revisa a primeira frase de um grupo de contas da mesma vertical (${g.vertical}). Contas parecidas colidem: cada linha
precisa servir só pra sua conta.

Aplique os 5 testes a cada rascunho e reescreva o que reprovar:
1) intercambiabilidade: trocando o nome por outra conta da mesma vertical, a frase ainda faz sentido? Então reprova.
2) "e daí?": a frase 2 termina em dinheiro ou esforço real do prospect?
3) culpa: soa como auditoria, puxão de orelha, ou atribui motivação a uma decisão da conta?
4) "como você sabe?": todo fato está nas evidências utilizáveis? Nenhum número sem evidência.
5) voz: parece gente escrevendo pra um par, sem jargão, sem pitch por negação, sem máxima de palestra?
Use só as evidências utilizáveis. Nunca use fato da lista PROIBIDO. Se nenhuma versão passa, primeira_frase vazia e índice -1.
Reescrita também passa pelos 5 testes.

CONTAS
${g.contas.map(bloco).join('\n')}

Responda SÓ com o objeto estruturado, uma linha por conta.`,
    { label: `abr:${g.vertical.slice(0, 16)}`, phase: 'Abertura', schema: ABR, agentType: 'general-purpose' }
  ), (r, g) => {
    if (!r) return null
    const linhas = r.linhas.filter(l => l.primeira_frase)
    if (!linhas.length) return { r, fria: { leituras: [] } }
    const porDom = {}
    for (const i of g.contas) porDom[i.veredito.domain] = i.veredito
    const itens = linhas.map(l => {
      const ev = (porDom[l.domain] || { evidencias: [] }).evidencias[l.evidencia_idx]
      return `- ${l.domain}\n  linha: "${l.primeira_frase}"\n  evidência: ${ev ? ev.fato : 'nenhuma'}`
    }).join('\n')
    return agent(
`Você lê pela primeira vez aberturas de email frio, sem nenhum outro contexto. Pra cada linha, diga se ela pode ir pra um
prospect: gramática certa, acentuação completa, sentido claro na primeira leitura, e o fato da linha bate com a evidência
(sem exagero, sem número a mais, sem atribuir motivo). Se reprovar, diga o problema em uma frase.

${itens}

Responda SÓ com o objeto estruturado.`,
      { label: `fria:${g.vertical.slice(0, 16)}`, phase: 'Leitura fria', schema: FRIA, agentType: 'general-purpose' }
    ).then(fria => ({ r, fria: fria || { leituras: [] } }))
  })

  const novas = {}
  for (const x of res.filter(Boolean)) {
    const fria = {}
    for (const l of x.fria.leituras || []) fria[l.domain] = l
    for (const l of x.r.linhas) novas[l.domain] = { ...l, fria: fria[l.domain] }
  }

  return DADOS.items.map(i => {
    const v = JSON.parse(JSON.stringify(i.veredito))
    const n = novas[v.domain]
    if (!n || !['P0', 'lista'].includes(v.veredito)) return v
    const refut = (v.adversarial && v.adversarial.fatos_refutados) || []
    delete v.primeira_frase_evidencia_idx
    v.primeira_frase = ''
    const motivos = []
    const erro = qaFrase(n.primeira_frase)
    const ev = v.evidencias[n.evidencia_idx]
    if (!n.primeira_frase) motivos.push(`nenhuma versão passou nos 5 testes (${n.testes_reprovados.join(', ')})`)
    else if (erro) motivos.push(`QA mecânico: ${erro}`)
    else if (!ev) motivos.push('sem evidência apontada')
    else if (refut.includes(ev.fato)) motivos.push('fato refutado')
    else {
      v.primeira_frase = n.primeira_frase.trim()
      v.primeira_frase_evidencia_idx = n.evidencia_idx
      if (n.fria && !n.fria.aprovada) motivos.push(`leitura fria: ${n.fria.problema}`)
    }
    const obsBase = String(v.obs || '').split(' | ').filter(p => !/^primeira_frase|^abertura:|^fato da primeira_frase/.test(p)).join(' | ')
    v.obs = juntarObs(obsBase, motivos.length ? `abertura: ${motivos.join('; ')}` : '')
    if (motivos.length) v.revisar_no_h1 = true
    return v
  })
}

// ---------- execução ----------

let saida
if (DADOS.modo === 'validacao') saida = await modoValidacao()
else if (DADOS.modo === 'adversarial') saida = await modoAdversarial()
else if (DADOS.modo === 'abertura') saida = await modoAbertura()
else throw new Error(`modo desconhecido: ${DADOS.modo}`)

return saida
