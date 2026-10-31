// Serve fotos enviadas pelo painel (guardadas no banco). /api/foto?id=123
const db = require('./_db');

module.exports = async (req, res) => {
  const id = parseInt(req.query.id, 10);
  if (!Number.isFinite(id)) return res.status(400).end();
  try {
    const r = await db.rpc('foto_get', { p_id: id });
    const f = Array.isArray(r) ? r[0] : r;
    if (!f || !f.b64) return res.status(404).end();
    res.setHeader('Content-Type', f.mime);
    res.setHeader('Cache-Control', 'public, max-age=31536000, immutable');
    res.status(200).send(Buffer.from(f.b64, 'base64'));
  } catch (e) { res.status(500).end(); }
};
