// Cria uma sessão de Checkout no Asaas e redireciona o cliente para pagar.
// Variáveis de ambiente na Vercel: ASAAS_API_KEY (obrigatória), ASAAS_ENV ("sandbox" ou "production", padrão production)
module.exports = async (req, res) => {
  const key = process.env.ASAAS_API_KEY;
  const base = (process.env.ASAAS_ENV || 'production') === 'sandbox' ? 'https://api-sandbox.asaas.com/v3' : 'https://api.asaas.com/v3';
  const q = req.query || {};
  const name = String(q.n || '').slice(0, 120);
  const brand = String(q.b || '').slice(0, 60);
  const value = Number(q.p);
  const qty = Math.min(10, Math.max(1, parseInt(q.q || '1', 10) || 1));
  const frete = Number(q.f || 0);
  const freteNome = String(q.fn || 'Frete').slice(0, 40);
  const end = String(q.e || '').slice(0, 200);
  const site = 'https://' + (req.headers['x-forwarded-host'] || req.headers.host || 'notaperfumaria.vercel.app');
  if (!key) return res.status(500).send('Checkout não configurado: defina ASAAS_API_KEY na Vercel.');
  if (!name || !(value > 0)) return res.status(400).send('Produto ou valor inválido.');
  try {
    const payload = (billing) => ({
        billingTypes: billing,
        chargeTypes: ['DETACHED', 'INSTALLMENT'],
        minutesToExpire: 60,
        installment: { maxInstallmentCount: 6 },
        callback: { successUrl: site + '/?pago=1', cancelUrl: site + '/', expiredUrl: site + '/' },
        externalReference: end ? ('Entrega: ' + end) : undefined,
        items: [{ name: name, description: (brand ? 'Marca: ' + brand : '') + (end ? ' · Entrega: ' + end : ''), quantity: qty, value: Math.round(value * 100) / 100 }]
          .concat(frete > 0 ? [{ name: 'Frete ' + freteNome, description: end || undefined, quantity: 1, value: Math.round(frete * 100) / 100 }] : [])
      });
    const call = (billing) => fetch(base + '/checkouts', { method: 'POST', headers: { 'Content-Type': 'application/json', 'access_token': key, 'User-Agent': 'NotaPerfumaria' }, body: JSON.stringify(payload(billing)) });
    let r = await call(['PIX', 'CREDIT_CARD']);
    let data = await r.json();
    if (!r.ok && JSON.stringify(data).includes('chave Pix')) {
      console.warn('asaas: sem chave Pix cadastrada, abrindo checkout só com cartão');
      r = await call(['CREDIT_CARD']);
      data = await r.json();
    }
    const link = data.link || (data.id ? 'https://asaas.com/checkoutSession/show?id=' + data.id : null);
    if (!r.ok || !link) {
      console.error('asaas', r.status, JSON.stringify(data));
      return res.status(502).send('Não foi possível abrir o checkout agora. Fale com a gente no WhatsApp.');
    }
    res.setHeader('Cache-Control', 'no-store');
    res.writeHead(302, { Location: link });
    res.end();
  } catch (e) {
    console.error(e);
    res.status(500).send('Erro ao criar o checkout.');
  }
};
