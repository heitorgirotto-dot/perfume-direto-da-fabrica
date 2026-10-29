// Cria uma sessão de Checkout no Asaas e redireciona o cliente para pagar.
// Variáveis de ambiente na Vercel: ASAAS_API_KEY (obrigatória), ASAAS_ENV ("sandbox" ou "production", padrão production)
module.exports = async (req, res) => {
  const key = process.env.ASAAS_API_KEY;
  const base = (process.env.ASAAS_ENV || 'production') === 'sandbox' ? 'https://api-sandbox.asaas.com/v3' : 'https://api.asaas.com/v3';
  const q = req.query || {};
  const name = String(q.n || '').slice(0, 120);
  const brand = String(q.b || '').slice(0, 60);
  const value = Number(q.p);
  const site = 'https://' + (req.headers['x-forwarded-host'] || req.headers.host || 'notaperfumaria.vercel.app');
  if (!key) return res.status(500).send('Checkout não configurado: defina ASAAS_API_KEY na Vercel.');
  if (!name || !(value > 0)) return res.status(400).send('Produto ou valor inválido.');
  try {
    const r = await fetch(base + '/checkouts', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', 'access_token': key, 'User-Agent': 'NotaPerfumaria' },
      body: JSON.stringify({
        billingTypes: ['PIX', 'CREDIT_CARD'],
        chargeTypes: ['DETACHED', 'INSTALLMENT'],
        minutesToExpire: 60,
        installment: { maxInstallmentCount: 6 },
        callback: { successUrl: site + '/?pago=1', cancelUrl: site + '/', expiredUrl: site + '/' },
        items: [{ name: name, description: brand ? 'Marca: ' + brand : undefined, quantity: 1, value: Math.round(value * 100) / 100 }]
      })
    });
    const data = await r.json();
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
