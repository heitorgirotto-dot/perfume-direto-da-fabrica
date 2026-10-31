// Captura de lead antes de abrir o WhatsApp (ou newsletter).
// Body JSON: { nome, whatsapp, email, produto_id, produto_nome, origem, utm, visitante }
const db = require('./_db');

function body(req) {
  if (req.body && typeof req.body === 'object') return req.body;
  try { return JSON.parse(req.body || '{}'); } catch (e) { return {}; }
}
function fone(v) {
  let d = String(v || '').replace(/\D/g, '');
  if (d.startsWith('0')) d = d.replace(/^0+/, '');
  if (d.length === 10 || d.length === 11) d = '55' + d;
  return d.length >= 12 && d.length <= 13 ? d : null;
}

module.exports = async (req, res) => {
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');
  if (req.method === 'OPTIONS') return res.status(204).end();
  if (req.method !== 'POST') return res.status(405).end();
  const b = body(req);
  const whatsapp = fone(b.whatsapp);
  const email = b.email && /^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(b.email) ? String(b.email).toLowerCase().slice(0, 120) : null;
  if (!whatsapp && !email) return res.status(400).json({ error: 'Informe um WhatsApp válido (DDD + número).' });
  const row = {
    nome: b.nome ? String(b.nome).trim().slice(0, 80) : null,
    whatsapp, email,
    produto_id: Number.isFinite(+b.produto_id) ? +b.produto_id : null,
    produto_nome: b.produto_nome ? String(b.produto_nome).slice(0, 120) : null,
    origem: b.origem ? String(b.origem).slice(0, 40) : 'site',
    utm: b.utm && typeof b.utm === 'object' ? b.utm : null,
    visitante: b.visitante ? String(b.visitante).slice(0, 40) : null
  };
  try {
    // upsert pelo WhatsApp (ou e-mail): atualiza nome/último produto se já existir
    const col = whatsapp ? 'whatsapp' : 'email';
    const r = await db.insert('leads', row, true).catch(async (e) => {
      if (!/duplicate|unique|23505/i.test(e.message)) throw e;
      const patch = { produto_id: row.produto_id, produto_nome: row.produto_nome, origem: row.origem };
      if (row.nome) patch.nome = row.nome;
      return db.update('leads', col + '=eq.' + encodeURIComponent(row[col]), patch);
    });
    db.insert('eventos', { tipo: 'lead', produto_id: row.produto_id, produto_nome: row.produto_nome, pagina: row.origem, utm: row.utm, visitante: row.visitante }, false).catch(() => {});
    res.status(200).json({ ok: true, id: r && r[0] && r[0].id });
  } catch (e) { res.status(503).json({ error: e.message }); }
};
