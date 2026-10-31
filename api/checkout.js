// Cria o pedido e abre o pagamento no Asaas (PIX/cartão via Checkout; boleto via link de pagamento).
// Aceita um produto (?id=&q=) ou o carrinho (?cart=[{"id":1,"q":2},...]). Preços SEMPRE vêm do banco.
// Variáveis na Vercel: ASAAS_API_KEY (obrigatória), ASAAS_ENV ("sandbox"/"production"), PIX_OFF (padrão 0.10)
const { calcular } = require('./_taxas');
const db = require('./_db');
const A = require('./_auth');
const brl = v => 'R$ ' + Number(v).toFixed(2).replace('.', ',');
const r2 = v => Math.round(v * 100) / 100;

module.exports = async (req, res) => {
  const key = process.env.ASAAS_API_KEY;
  const apiBase = (process.env.ASAAS_ENV || 'production') === 'sandbox' ? 'https://api-sandbox.asaas.com/v3' : 'https://api.asaas.com/v3';
  const q = req.query || {};
  const frete = Math.max(0, r2(Number(q.f || 0)));
  const freteNome = String(q.fn || 'Frete').slice(0, 40);
  const end = String(q.e || '').slice(0, 200);
  const metodo = ['PIX', 'BOLETO', 'CARD'].includes(String(q.m || '').toUpperCase()) ? String(q.m).toUpperCase() : 'PIX';
  const nParc = parseInt(q.parc || '1', 10) || 1;
  const pixOff = Number(process.env.PIX_OFF || 0.10);
  const site = 'https://' + (req.headers['x-forwarded-host'] || req.headers.host || 'notaperfumaria.com');
  if (!key) return res.status(500).send('Checkout não configurado: defina ASAAS_API_KEY na Vercel.');

  // ---- monta as linhas do pedido com preços do banco
  let pedidoLinhas;
  try { pedidoLinhas = q.cart ? JSON.parse(q.cart) : [{ id: q.id, q: q.q }]; } catch (e) { return res.status(400).send('Carrinho inválido.'); }
  pedidoLinhas = (Array.isArray(pedidoLinhas) ? pedidoLinhas : []).map(l => ({ id: parseInt(l.id, 10), q: Math.min(10, Math.max(1, parseInt(l.q, 10) || 1)) })).filter(l => Number.isFinite(l.id)).slice(0, 30);
  if (!pedidoLinhas.length) return res.status(400).send('Nenhum produto informado.');
  let prods;
  try { prods = await db.select('produtos', 'select=id,marca,nome,preco,ativo&id=in.(' + pedidoLinhas.map(l => l.id).join(',') + ')'); }
  catch (e) { console.error('produtos', e.message); return res.status(503).send('Catálogo indisponível no momento. Tente de novo em instantes.'); }
  const linhas = [];
  for (const l of pedidoLinhas) {
    const p = prods.find(x => x.id === l.id);
    if (!p || !p.ativo || p.preco == null) return res.status(400).send('Um dos produtos não está disponível para compra online. Fale com a gente no WhatsApp.');
    const preco = Number(p.preco);
    linhas.push({ id: p.id, marca: p.marca, nome: p.nome, q: l.q, preco, unit: metodo === 'PIX' ? r2(preco * (1 - pixOff)) : r2(preco) });
  }
  const subtotal = r2(linhas.reduce((s, l) => s + l.unit * l.q, 0));
  const qtdTotal = linhas.reduce((s, l) => s + l.q, 0);
  const c = calcular(r2(subtotal + frete), metodo, nParc);
  const resumo = linhas.length === 1 ? (linhas[0].marca + ' ' + linhas[0].nome) : (qtdTotal + ' itens: ' + linhas.map(l => (l.q > 1 ? l.q + 'x ' : '') + l.nome).join(', '));

  try {
    // ---- registra o pedido
    const pedido = { produto_id: linhas.length === 1 ? linhas[0].id : null, produto_nome: resumo.slice(0, 160), quantidade: qtdTotal, valor_unit: linhas.length === 1 ? linhas[0].unit : subtotal,
      frete, frete_nome: frete > 0 ? freteNome : null, taxa: c.taxa || 0, total: c.total, metodo, parcelas: c.n || 1, endereco: end || null,
      itens: linhas.map(l => ({ id: l.id, marca: l.marca, nome: l.nome, quantidade: l.q, valor_unit: l.unit })) };
    let codigo = null;
    try { codigo = await db.rpc('pedido_criar', { p: pedido, p_tok: A.getCookie(req, 'nota_cli') || '' }); } catch (e) { console.error('pedido', e.message); }
    const setRef = (ref) => codigo && ref ? db.rpc('pedido_ref', { p_codigo: codigo, p_ref: String(ref) }).catch(() => {}) : null;
    db.rpc('evento_registrar', { p: { tipo: 'checkout', produto_id: pedido.produto_id, produto_nome: resumo.slice(0, 120), pagina: metodo + (nParc > 1 ? ' ' + nParc + 'x' : ''), referencia: String(c.total) } }).catch(() => {});

    const H = { 'Content-Type': 'application/json', access_token: key, 'User-Agent': 'NotaPerfumaria' };
    if (metodo === 'BOLETO') {
      const desc = ((codigo ? 'Pedido ' + codigo + ' · ' : '') + linhas.map(l => l.q + 'x ' + l.marca + ' ' + l.nome).join('; ') + (frete > 0 ? ' + Frete ' + freteNome + ' ' + brl(frete) : '') + (c.taxa > 0 ? ' + Taxa boleto ' + brl(c.taxa) : '') + (end ? ' · Entrega: ' + end : '')).slice(0, 500);
      const rb = await fetch(apiBase + '/paymentLinks', { method: 'POST', headers: H, body: JSON.stringify({ name: ('Nota Perfumaria ' + (codigo || '')).trim().slice(0, 60), description: desc,
        billingType: 'BOLETO', chargeType: 'DETACHED', value: c.total, dueDateLimitDays: 3, maxInstallmentCount: 1, notificationEnabled: true, externalReference: codigo || undefined }) });
      const d = await rb.json();
      if (!rb.ok || !d.url) { console.error('asaas boleto', rb.status, JSON.stringify(d)); return res.status(502).send('Não foi possível gerar o boleto agora. Fale com a gente no WhatsApp.'); }
      await setRef(d.id); res.setHeader('Cache-Control', 'no-store'); res.writeHead(302, { Location: d.url }); return res.end();
    }

    const items = linhas.map(l => ({ name: l.nome.slice(0, 30), description: (l.marca + ' ' + l.nome + (metodo === 'PIX' ? ' · preço PIX' : '')).slice(0, 150), quantity: l.q, value: l.unit }))
      .concat(frete > 0 ? [{ name: ('Frete ' + freteNome).slice(0, 30), description: (end || 'Entrega').slice(0, 150), quantity: 1, value: frete }] : [])
      .concat(c.taxa > 0 ? [{ name: metodo === 'CARD' ? (c.n > 1 ? 'Taxa cartão ' + c.n + 'x' : 'Taxa cartão à vista') : 'Taxa', description: 'Taxa de processamento do pagamento', quantity: 1, value: c.taxa }] : []);
    const payload = {
      billingTypes: metodo === 'CARD' ? ['CREDIT_CARD'] : ['PIX'],
      chargeTypes: metodo === 'CARD' && c.n > 1 ? ['DETACHED', 'INSTALLMENT'] : ['DETACHED'],
      minutesToExpire: 60,
      installment: metodo === 'CARD' && c.n > 1 ? { maxInstallmentCount: c.n, minInstallmentCount: c.n } : undefined,
      callback: { successUrl: site + '/?pago=' + (codigo || '1'), cancelUrl: site + '/', expiredUrl: site + '/' },
      externalReference: codigo || undefined,
      items
    };
    const r = await fetch(apiBase + '/checkouts', { method: 'POST', headers: H, body: JSON.stringify(payload) });
    const data = await r.json();
    if (!r.ok && JSON.stringify(data).includes('chave Pix')) return res.status(503).send('PIX indisponível no momento. Escolha cartão ou boleto, ou fale com a gente no WhatsApp.');
    const link = data.link || (data.id ? 'https://asaas.com/checkoutSession/show?id=' + data.id : null);
    if (!r.ok || !link) { console.error('asaas', r.status, JSON.stringify(data)); return res.status(502).send('Não foi possível abrir o checkout agora. Fale com a gente no WhatsApp.'); }
    await setRef(data.id);
    res.setHeader('Cache-Control', 'no-store'); res.writeHead(302, { Location: link }); res.end();
  } catch (e) {
    console.error(e);
    res.status(500).send('Erro ao criar o checkout.');
  }
};
