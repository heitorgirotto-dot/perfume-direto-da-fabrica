// Webhook do Asaas: marca o pedido como pago/cancelado. O token é conferido dentro do banco.
// O próprio painel registra este webhook no Asaas automaticamente (sem configuração manual).
const db = require('./_db');
const A = require('./_auth');

const MAPA = {
  PAYMENT_CONFIRMED: 'pago', PAYMENT_RECEIVED: 'pago', CHECKOUT_PAID: 'pago',
  PAYMENT_REFUNDED: 'cancelado', PAYMENT_DELETED: 'cancelado', PAYMENT_CHARGEBACK_REQUESTED: 'cancelado',
  CHECKOUT_CANCELED: 'cancelado', CHECKOUT_EXPIRED: 'cancelado'
};

module.exports = async (req, res) => {
  if (req.method !== 'POST') return res.status(405).end();
  const token = String(req.headers['asaas-access-token'] || '');
  const b = A.body(req);
  const ev = String(b.event || '');
  const status = MAPA[ev];
  if (!status) return res.status(200).json({ ignorado: ev });
  const pay = b.payment || {}, chk = b.checkout || {};
  const p = { status, evento: ev, codigo: pay.externalReference || chk.externalReference || null, refs: [pay.checkoutSession, pay.paymentLink, chk.id].filter(Boolean), payment: pay.id || null };
  // dados do pagador para vincular o pedido à conta pelo CPF
  const key = process.env.ASAAS_API_KEY;
  if (status === 'pago' && key && pay.customer) {
    try {
      const base = (process.env.ASAAS_ENV || 'production') === 'sandbox' ? 'https://api-sandbox.asaas.com/v3' : 'https://api.asaas.com/v3';
      const cu = await fetch(base + '/customers/' + pay.customer, { headers: { access_token: key, 'User-Agent': 'NotaPerfumaria' } }).then(r => r.json());
      if (cu && cu.cpfCnpj) { p.cpf = cu.cpfCnpj; p.nome = cu.name || null; }
    } catch (e) { /* segue */ }
  }
  try { res.status(200).json(await db.rpc('pedido_webhook', { p_token: token, p })); }
  catch (e) { res.status(e.code === 'TOKEN_INVALIDO' ? 401 : 500).json({ error: e.message }); }
};
