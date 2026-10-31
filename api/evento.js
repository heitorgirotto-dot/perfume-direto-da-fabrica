// Registra eventos de navegação (visita, produto aberto, clique em comprar, WhatsApp, lead).
// Body JSON: { tipo, produto_id, produto_nome, pagina, referencia, utm, visitante }
const db = require('./_db');
const TIPOS = new Set(['visita', 'produto', 'comprar', 'checkout', 'whatsapp', 'lead', 'busca']);

function body(req) {
  if (req.body && typeof req.body === 'object') return req.body;
  try { return JSON.parse(req.body || '{}'); } catch (e) { return {}; }
}

module.exports = async (req, res) => {
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');
  if (req.method === 'OPTIONS') return res.status(204).end();
  if (req.method !== 'POST') return res.status(405).end();
  const b = body(req);
  const tipo = String(b.tipo || '').slice(0, 20);
  if (!TIPOS.has(tipo)) return res.status(400).json({ error: 'tipo inválido' });
  const ua = String(req.headers['user-agent'] || '');
  const disp = /Mobi|Android|iPhone/i.test(ua) ? 'mobile' : 'desktop';
  const row = {
    tipo,
    produto_id: Number.isFinite(+b.produto_id) ? +b.produto_id : null,
    produto_nome: b.produto_nome ? String(b.produto_nome).slice(0, 120) : null,
    pagina: b.pagina ? String(b.pagina).slice(0, 200) : null,
    referencia: b.referencia ? String(b.referencia).slice(0, 200) : null,
    utm: b.utm && typeof b.utm === 'object' ? b.utm : null,
    visitante: b.visitante ? String(b.visitante).slice(0, 40) : null,
    dispositivo: disp
  };
  try { await db.insert('eventos', row, false); res.status(204).end(); }
  catch (e) { res.status(503).json({ error: e.message }); }
};
