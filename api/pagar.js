// Pagamento transparente (o cliente não sai do site).
// POST /api/pagar  → cria o pedido + cobrança no Asaas e devolve QR Code PIX, linha do boleto ou resultado do cartão.
// GET  /api/pagar?c=CODIGO → status do pagamento (consulta o Asaas).
// Dados de cartão NÃO são gravados nem registrados em log: passam direto para o Asaas.
const { calcular } = require('./_taxas');
const db = require('./_db');
const A = require('./_auth');
const r2 = v => Math.round(v * 100) / 100;
const base = () => (process.env.ASAAS_ENV || 'production') === 'sandbox' ? 'https://api-sandbox.asaas.com/v3' : 'https://api.asaas.com/v3';
function hojeSP(dias) {
  const d = new Date(Date.now() - 3 * 3600e3 + (dias || 0) * 86400e3);
  return d.toISOString().slice(0, 10);
}
async function asaas(method, path, body) {
  const r = await fetch(base() + path, { method, headers: { 'Content-Type': 'application/json', access_token: process.env.ASAAS_API_KEY, 'User-Agent': 'NotaPerfumaria' }, body: body ? JSON.stringify(body) : undefined });
  const d = await r.json().catch(() => ({}));
  if (!r.ok) { const msg = (d.errors && d.errors.map(e => e.description).join(' ')) || ('Asaas ' + r.status); const e = new Error(msg); e.asaas = true; throw e; }
  return d;
}

module.exports = async (req, res) => {
  res.setHeader('Cache-Control', 'no-store');
  if (!process.env.ASAAS_API_KEY) return res.status(503).json({ error: 'Pagamento indisponível no momento.' });

  // ---------- status ----------
  if (req.method === 'GET') {
    const cod = String(req.query.c || '').replace(/[^A-Z0-9]/gi, '').toUpperCase();
    try {
      const p = await db.rpc('pedido_status', { p_codigo: cod });
      if (!p) return res.status(404).json({ error: 'Pedido não encontrado' });
      if (p.status !== 'aguardando_pagamento' || !p.ref || !/^pay_/.test(p.ref)) return res.status(200).json({ status: p.status });
      const s = await asaas('GET', '/payments/' + p.ref + '/status');
      const pago = ['RECEIVED', 'CONFIRMED', 'RECEIVED_IN_CASH'].includes(s.status);
      return res.status(200).json({ status: pago ? 'pago' : p.status, asaas: s.status });
    } catch (e) { return res.status(200).json({ status: 'desconhecido' }); }
  }
  if (req.method !== 'POST') return res.status(405).end();

  const b = A.body(req);
  const metodo = ['PIX', 'BOLETO', 'CARD'].includes(b.metodo) ? b.metodo : 'PIX';
  const nParc = Math.max(1, Math.min(12, parseInt(b.parcelas, 10) || 1));
  const pixOff = Number(process.env.PIX_OFF || 0.10);
  const frete = Math.max(0, r2(Number(b.frete && b.frete.preco) || 0));
  const freteNome = String((b.frete && b.frete.nome) || 'Frete').slice(0, 40);
  const end = b.endereco || {};
  const endTxt = String(end.texto || '').slice(0, 200);
  const cepEnt = String(end.cep || '').replace(/\D/g, '');

  // ---------- pagador ----------
  const tok = A.getCookie(req, 'nota_cli');
  let pg = b.cliente || {};
  if (tok) { const d = await db.rpc('cli_dados', { p_tok: tok }).catch(() => null); if (d) pg = Object.assign({}, d, { nome: pg.nome || d.nome }); }
  const nome = String(pg.nome || '').trim().replace(/\s+/g, ' ').slice(0, 100);
  const cpf = String(pg.cpf || '').replace(/\D/g, '');
  const email = String(pg.email || '').trim().toLowerCase().slice(0, 120);
  const fone = String(pg.whatsapp || '').replace(/\D/g, '').replace(/^55(?=\d{10,11}$)/, '');
  if (nome.split(' ').length < 2) return res.status(400).json({ error: 'Informe nome e sobrenome.' });
  if (!A.cpfValido(cpf)) return res.status(400).json({ error: 'CPF inválido.' });
  if (!/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(email)) return res.status(400).json({ error: 'E-mail inválido.' });
  if (fone.length < 10 || fone.length > 11) return res.status(400).json({ error: 'WhatsApp inválido (DDD + número).' });
  if (cepEnt.length !== 8 || !end.numero) return res.status(400).json({ error: 'Endereço de entrega incompleto.' });

  // ---------- itens com preço do banco ----------
  let linhasReq = (Array.isArray(b.cart) ? b.cart : []).map(l => ({ id: parseInt(l.id, 10), q: Math.min(10, Math.max(1, parseInt(l.q, 10) || 1)) })).filter(l => Number.isFinite(l.id)).slice(0, 30);
  if (!linhasReq.length) return res.status(400).json({ error: 'Carrinho vazio.' });
  let prods;
  try { prods = await db.select('produtos', 'select=id,marca,nome,preco,ativo&id=in.(' + linhasReq.map(l => l.id).join(',') + ')'); }
  catch (e) { return res.status(503).json({ error: 'Catálogo indisponível. Tente de novo.' }); }
  const linhas = [];
  for (const l of linhasReq) {
    const p = prods.find(x => x.id === l.id);
    if (!p || !p.ativo || p.preco == null) return res.status(400).json({ error: 'Um dos produtos não está disponível para compra online.' });
    linhas.push({ id: p.id, marca: p.marca, nome: p.nome, q: l.q, unit: metodo === 'PIX' ? r2(Number(p.preco) * (1 - pixOff)) : r2(Number(p.preco)) });
  }
  const subtotal = r2(linhas.reduce((s, l) => s + l.unit * l.q, 0));
  const qtd = linhas.reduce((s, l) => s + l.q, 0);
  const c = calcular(r2(subtotal + frete), metodo, metodo === 'CARD' ? nParc : 1);
  const resumo = linhas.length === 1 ? (linhas[0].marca + ' ' + linhas[0].nome) : (qtd + ' itens: ' + linhas.map(l => (l.q > 1 ? l.q + 'x ' : '') + l.nome).join(', '));

  // ---------- cartão: validação básica antes de criar qualquer coisa ----------
  let cartao = null;
  if (metodo === 'CARD') {
    const k = b.cartao || {};
    cartao = { holderName: String(k.nome || '').trim().slice(0, 60), number: String(k.numero || '').replace(/\D/g, ''), expiryMonth: String(k.mes || '').padStart(2, '0'), expiryYear: String(k.ano || '').length === 2 ? '20' + k.ano : String(k.ano || ''), ccv: String(k.cvv || '').replace(/\D/g, '') };
    if (cartao.number.length < 13 || cartao.number.length > 19 || !/^\d{2}$/.test(cartao.expiryMonth) || !/^\d{4}$/.test(cartao.expiryYear) || cartao.ccv.length < 3 || cartao.holderName.length < 3)
      return res.status(400).json({ error: 'Confira os dados do cartão.' });
  }

  try {
    // pedido
    const pedido = { produto_id: linhas.length === 1 ? linhas[0].id : null, produto_nome: resumo.slice(0, 160), quantidade: qtd, valor_unit: linhas.length === 1 ? linhas[0].unit : subtotal,
      frete, frete_nome: frete > 0 ? freteNome : null, taxa: c.taxa || 0, total: c.total, metodo, parcelas: c.n || 1, endereco: endTxt || null,
      itens: linhas.map(l => ({ id: l.id, marca: l.marca, nome: l.nome, quantidade: l.q, valor_unit: l.unit })), ref: String(b.ref || A.getCookie(req, 'nota_ref') || '').replace(/[^A-Za-z0-9]/g, '').slice(0, 20) };
    const codigo = await db.rpc('pedido_criar', { p: pedido, p_tok: tok || '' });
    db.rpc('pedido_pagador', { p_codigo: codigo, p_cpf: cpf, p_nome: nome }).catch(() => {});
    db.rpc('lead_registrar', { p: { nome, whatsapp: '55' + fone, email, origem: 'compra' } }).catch(() => {});
    db.rpc('evento_registrar', { p: { tipo: 'checkout', produto_id: pedido.produto_id, produto_nome: resumo.slice(0, 120), pagina: metodo + (c.n > 1 ? ' ' + c.n + 'x' : ''), referencia: String(c.total) } }).catch(() => {});

    // cliente no Asaas (reaproveita pelo CPF)
    const ex = await asaas('GET', '/customers?cpfCnpj=' + cpf + '&limit=1');
    let customer = ex.data && ex.data[0] && ex.data[0].id;
    if (!customer) {
      const cu = await asaas('POST', '/customers', { name: nome, cpfCnpj: cpf, email, mobilePhone: fone, postalCode: cepEnt, addressNumber: String(end.numero).slice(0, 10), complement: String(end.comp || '').slice(0, 60) || undefined, externalReference: 'nota' });
      customer = cu.id;
    }

    const desc = ('Nota Perfumaria · Pedido ' + codigo + ' · ' + linhas.map(l => l.q + 'x ' + l.marca + ' ' + l.nome).join('; ') + (frete > 0 ? ' · Frete ' + freteNome : '')).slice(0, 500);
    const cob = { customer, billingType: metodo === 'CARD' ? 'CREDIT_CARD' : metodo, dueDate: hojeSP(metodo === 'BOLETO' ? 3 : 1), description: desc, externalReference: codigo };
    if (metodo === 'CARD' && c.n > 1) { cob.installmentCount = c.n; cob.totalValue = c.total; } else cob.value = c.total;
    if (metodo === 'CARD') {
      cob.creditCard = cartao;
      cob.creditCardHolderInfo = { name: nome, email, cpfCnpj: cpf, postalCode: cepEnt, addressNumber: String(end.numero).slice(0, 10), addressComplement: String(end.comp || '').slice(0, 60) || undefined, phone: fone, mobilePhone: fone };
      cob.remoteIp = A.ipOf(req);
    }
    let pay;
    try { pay = await asaas('POST', '/payments', cob); }
    catch (e) {
      if (metodo === 'CARD') return res.status(402).json({ error: 'Pagamento recusado: ' + e.message.replace(/\s+/g, ' ').slice(0, 200), codigo });
      throw e;
    }
    await db.rpc('pedido_ref', { p_codigo: codigo, p_ref: pay.id }).catch(() => {});
    const out = { codigo, total: c.total, metodo, parcelas: c.n, paymentId: pay.id, status: pay.status };

    if (metodo === 'PIX') {
      const qr = await asaas('GET', '/payments/' + pay.id + '/pixQrCode');
      out.qr = qr.encodedImage; out.copia = qr.payload; out.expira = qr.expirationDate;
    } else if (metodo === 'BOLETO') {
      const idf = await asaas('GET', '/payments/' + pay.id + '/identificationField').catch(() => ({}));
      out.linha = idf.identificationField || null; out.boletoUrl = pay.bankSlipUrl || null; out.vencimento = pay.dueDate;
      const qr = await asaas('GET', '/payments/' + pay.id + '/pixQrCode').catch(() => null); // boleto também aceita PIX
      if (qr && qr.payload) { out.qr = qr.encodedImage; out.copia = qr.payload; }
    } else {
      out.aprovado = ['CONFIRMED', 'RECEIVED'].includes(pay.status);
    }
    return res.status(200).json(out);
  } catch (e) {
    console.error('pagar', e.asaas ? 'asaas: ' + e.message : e.message);
    return res.status(502).json({ error: e.asaas ? 'Não foi possível gerar o pagamento: ' + e.message.slice(0, 200) : 'Não foi possível gerar o pagamento agora. Tente de novo ou fale no WhatsApp.' });
  }
};
