// Registra eventos de navegação (visita, produto, comprar, whatsapp, busca...).
const db = require('./_db');
const A = require('./_auth');

module.exports = async (req, res) => {
  if (req.method !== 'POST') return res.status(405).end();
  const b = A.body(req);
  const ua = String(req.headers['user-agent'] || '');
  b.dispositivo = /Mobi|Android|iPhone/i.test(ua) ? 'mobile' : 'desktop';
  try { await db.rpc('evento_registrar', { p: b }); res.status(204).end(); }
  catch (e) { A.fail(res, e); }
};
