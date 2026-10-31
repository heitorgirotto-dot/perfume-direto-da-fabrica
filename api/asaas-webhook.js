// Webhook do Asaas: atualiza o status do pedido quando o pagamento é confirmado, estornado etc.
// Configure no Asaas: Integrações → Webhooks → URL https://notaperfumaria.com/api/asaas-webhook
// e o mesmo "Token de autenticação" na variável ASAAS_WEBHOOK_TOKEN da Vercel.
const db = require('./_db');
const A = require('./_auth');

const MAPA = {
  PAYMENT_CONFIRMED: 'pago', PAYMENT_RECEIVED: 'pago', CHECKOUT_PAID: 'pago',
  PAYMENT_REFUNDED: 'cancelado', PAYMENT_DELETED: 'cancelado', PAYMENT_CHARGEBACK_REQUESTED: 'cancelado',
  CHECKOUT_CANCELED: 'cancelado', CHECKOUT_EXPIRED: 'cancelado'
};

async function acharPedido(pay, chk) {
  const tenta = async (q) => (await db.select('pedidos', 'select=*&' + q + '&limit=1'))[0];
  const ext = (pay && pay.externalReference) || (chk && chk.externalReference);
  if (ext && /^NP[A-Z0-9]+$/.test(ext)) { const p = await tenta('codigo=eq.' + ext); if (p) return p; }
  for (const ref of [pay && pay.checkoutSession, pay && pay.paymentLink, chk && chk.id].filter(Boolean)) {
    const p = await tenta('asaas_ref=eq.' + encodeURIComponent(ref)); if (p) return p;
  }
  return null;
}

module.exports = async (req, res) => {
  const token = process.env.ASAAS_WEBHOOK_TOKEN;
  if (!token || req.headers['asaas-access-token'] !== token) return res.status(401).json({ error: 'token' });
  const b = A.body(req);
  const ev = String(b.event || '');
  const novo = MAPA[ev];
  if (!novo) return res.status(200).json({ ignorado: ev });
  try {
    const pay = b.payment || null, chk = b.checkout || null;
    const p = await acharPedido(pay, chk);
    if (!p) return res.status(200).json({ ok: true, pedido: null });
    // não regride pedido já enviado/entregue para "pago"
    const ordem = ['aguardando_pagamento', 'pago', 'em_separacao', 'enviado', 'entregue'];
    if (novo === 'pago' && ordem.indexOf(p.status) >= 1) return res.status(200).json({ ok: true, mantido: p.status });
    if (novo === 'cancelado' && ['enviado', 'entregue'].includes(p.status)) return res.status(200).json({ ok: true, mantido: p.status });
    const patch = { status: novo, atualizado_em: new Date().toISOString(), historico: (p.historico || []).concat([{ status: novo, em: new Date().toISOString(), por: 'asaas:' + ev }]) };
    if (pay && pay.id) patch.asaas_payment = pay.id;
    // dados do pagador para vincular à conta pelo CPF
    const key = process.env.ASAAS_API_KEY;
    if (key && pay && pay.customer) {
      const base = (process.env.ASAAS_ENV || 'production') === 'sandbox' ? 'https://api-sandbox.asaas.com/v3' : 'https://api.asaas.com/v3';
      try {
        const cu = await fetch(base + '/customers/' + pay.customer, { headers: { access_token: key, 'User-Agent': 'NotaPerfumaria' } }).then(r => r.json());
        if (cu && cu.cpfCnpj) {
          patch.pagador_cpf = String(cu.cpfCnpj).replace(/\D/g, ''); patch.pagador_nome = cu.name || null;
          if (!p.cliente_id) { const c = (await db.select('clientes', 'select=id&cpf=eq.' + patch.pagador_cpf))[0]; if (c) patch.cliente_id = c.id; }
        }
      } catch (e) { /* segue sem dados do pagador */ }
    }
    await db.update('pedidos', 'id=eq.' + p.id, patch);
    return res.status(200).json({ ok: true, pedido: p.codigo, status: novo });
  } catch (e) {
    console.error('webhook', e.message);
    return res.status(500).json({ error: e.message });
  }
};
