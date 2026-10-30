// Cria uma sessão de Checkout no Asaas e redireciona o cliente para pagar.
// Variáveis de ambiente na Vercel: ASAAS_API_KEY (obrigatória), ASAAS_ENV ("sandbox" ou "production", padrão production)
const { calcular } = require('./_taxas');
module.exports = async (req, res) => {
  const key = process.env.ASAAS_API_KEY;
  const apiBase = (process.env.ASAAS_ENV || 'production') === 'sandbox' ? 'https://api-sandbox.asaas.com/v3' : 'https://api.asaas.com/v3';
  const q = req.query || {};
  const name = String(q.n || '').slice(0, 120);
  const brand = String(q.b || '').slice(0, 60);
  const value = Number(q.p);
  const qty = Math.min(10, Math.max(1, parseInt(q.q || '1', 10) || 1));
  const frete = Number(q.f || 0);
  const freteNome = String(q.fn || 'Frete').slice(0, 40);
  const end = String(q.e || '').slice(0, 200);
  const metodo = ['PIX','BOLETO','CARD'].includes(String(q.m||'').toUpperCase()) ? String(q.m).toUpperCase() : 'PIX';
  const nParc = parseInt(q.n_ || q.parc || '1', 10) || 1;
  const pixOff = Number(process.env.PIX_OFF || 0.10);
  const site = 'https://' + (req.headers['x-forwarded-host'] || req.headers.host || 'notaperfumaria.vercel.app');
  if (!key) return res.status(500).send('Checkout não configurado: defina ASAAS_API_KEY na Vercel.');
  if (!name || !(value > 0)) return res.status(400).send('Produto ou valor inválido.');
  try {
    const unit = metodo === 'PIX' ? Math.round(value * (1 - pixOff) * 100) / 100 : Math.round(value * 100) / 100;
    const base = unit * qty + (frete > 0 ? Math.round(frete * 100) / 100 : 0);
    const c = calcular(base, metodo, nParc);
    const payload = (billing) => ({
        billingTypes: billing,
        chargeTypes: metodo === 'CARD' && c.n > 1 ? ['INSTALLMENT'] : ['DETACHED'],
        minutesToExpire: 60,
        installment: metodo === 'CARD' && c.n > 1 ? { maxInstallmentCount: c.n, minInstallmentCount: c.n } : undefined,
        callback: { successUrl: site + '/?pago=1', cancelUrl: site + '/', expiredUrl: site + '/' },
        externalReference: end ? ('Entrega: ' + end) : undefined,
        items: [{ name: name.slice(0, 30), description: (name.length > 30 ? name + ' · ' : '') + (brand ? 'Marca: ' + brand : '') + (metodo === 'PIX' ? ' · preço PIX' : '') + (end ? ' · Entrega: ' + end : ''), quantity: qty, value: unit }]
          .concat(frete > 0 ? [{ name: ('Frete ' + freteNome).slice(0, 30), description: end || undefined, quantity: 1, value: Math.round(frete * 100) / 100 }] : [])
          .concat(c.taxa > 0 ? [{ name: (metodo === 'CARD' ? (c.n > 1 ? 'Taxa cartão ' + c.n + 'x' : 'Taxa cartão à vista') : 'Taxa boleto'), description: 'Taxa de processamento do pagamento', quantity: 1, value: c.taxa }] : [])
      });
    const billing = metodo === 'CARD' ? ['CREDIT_CARD'] : metodo === 'BOLETO' ? ['BOLETO'] : ['PIX'];
    const call = (b) => fetch(apiBase + '/checkouts', { method: 'POST', headers: { 'Content-Type': 'application/json', 'access_token': key, 'User-Agent': 'NotaPerfumaria' }, body: JSON.stringify(payload(b)) });
    let r = await call(billing);
    let data = await r.json();
    if (!r.ok && JSON.stringify(data).includes('chave Pix')) {
      console.error('asaas: conta sem chave Pix cadastrada');
      return res.status(503).send('PIX indisponível no momento: a loja ainda não cadastrou a chave Pix. Escolha cartão ou boleto, ou fale com a gente no WhatsApp.');
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
