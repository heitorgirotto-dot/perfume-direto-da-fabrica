// Captura de lead (antes do WhatsApp e newsletter).
const db = require('./_db');
const A = require('./_auth');

module.exports = async (req, res) => {
  if (req.method !== 'POST') return res.status(405).end();
  const b = A.body(req);
  const whatsapp = A.fone(b.whatsapp);
  const email = b.email && /^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(b.email) ? String(b.email).toLowerCase().slice(0, 120) : null;
  if (!whatsapp && !email) return res.status(400).json({ error: 'Informe um WhatsApp válido (DDD + número).' });
  try {
    await db.rpc('lead_registrar', { p: Object.assign({}, b, { whatsapp, email }) });
    res.status(200).json({ ok: true });
  } catch (e) { A.fail(res, e); }
};
