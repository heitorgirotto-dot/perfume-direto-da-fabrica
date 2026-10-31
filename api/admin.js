// Painel administrativo — API única (?a=acao).
// Variáveis na Vercel: ADMIN_USER, ADMIN_PASS (obrigatórias), ADMIN_SECRET (opcional), SUPABASE_SERVICE_ROLE_KEY.
const crypto = require('crypto');
const db = require('./_db');

const USER = process.env.ADMIN_USER || '';
const PASS = process.env.ADMIN_PASS || '';
const SECRET = process.env.ADMIN_SECRET || crypto.createHash('sha256').update('nota|' + PASS + '|' + USER).digest('hex');
const COOKIE = 'nota_adm';
const DURACAO = 12 * 3600; // 12h

function body(req) {
  if (req.body && typeof req.body === 'object') return req.body;
  try { return JSON.parse(req.body || '{}'); } catch (e) { return {}; }
}
function sign(s) { return crypto.createHmac('sha256', SECRET).update(s).digest('base64url'); }
function token() { const exp = Math.floor(Date.now() / 1000) + DURACAO; const p = USER + '|' + exp; return p + '|' + sign(p); }
function valid(t) {
  if (!t) return false;
  const i = t.lastIndexOf('|'); if (i < 0) return false;
  const p = t.slice(0, i), s = t.slice(i + 1);
  if (sign(p) !== s) return false;
  const exp = +p.split('|')[1];
  return exp > Date.now() / 1000;
}
function cookieOf(req) {
  const c = req.headers.cookie || '';
  const m = c.match(new RegExp('(?:^|;\\s*)' + COOKIE + '=([^;]+)'));
  return m ? decodeURIComponent(m[1]) : null;
}
function setCookie(res, v, maxAge) {
  res.setHeader('Set-Cookie', COOKIE + '=' + encodeURIComponent(v) + '; Path=/; HttpOnly; Secure; SameSite=Strict; Max-Age=' + maxAge);
}
function safeEq(a, b) {
  const A = Buffer.from(String(a)), B = Buffer.from(String(b));
  return A.length === B.length && crypto.timingSafeEqual(A, B);
}
const tentativas = new Map(); // IP -> {n, t}
function bloqueado(ip) { const r = tentativas.get(ip); return r && r.n >= 8 && Date.now() - r.t < 15 * 60e3; }
function falhou(ip) { const r = tentativas.get(ip) || { n: 0, t: 0 }; r.n++; r.t = Date.now(); tentativas.set(ip, r); }

function limparProduto(b) {
  const p = {
    marca: String(b.marca || '').trim().slice(0, 80),
    nome: String(b.nome || '').trim().slice(0, 160),
    genero: ['M', 'F', 'U'].includes(b.genero) ? b.genero : 'U',
    preco: b.preco === '' || b.preco == null ? null : Math.round(Number(String(b.preco).replace(',', '.')) * 100) / 100,
    notas: b.notas ? String(b.notas).trim().slice(0, 400) : null,
    lembra: b.lembra ? String(b.lembra).trim().slice(0, 120) : null,
    descricao: b.descricao ? String(b.descricao).trim().slice(0, 2000) : null,
    fotos: Array.isArray(b.fotos) ? b.fotos.filter(x => typeof x === 'string' && x.length < 500).slice(0, 8) : [],
    ativo: b.ativo !== false,
    mais_vendido: !!b.mais_vendido,
    top5: b.top5 ? Math.min(5, Math.max(1, +b.top5)) : null,
    atualizado_em: new Date().toISOString()
  };
  if (!p.marca || !p.nome) throw new Error('Marca e nome são obrigatórios');
  if (p.preco != null && !(p.preco >= 0)) throw new Error('Preço inválido');
  return p;
}

module.exports = async (req, res) => {
  res.setHeader('Cache-Control', 'no-store');
  const a = String(req.query.a || '');
  const ip = String(req.headers['x-forwarded-for'] || '').split(',')[0].trim() || 'x';

  try {
    if (a === 'login') {
      if (req.method !== 'POST') return res.status(405).end();
      if (!USER || !PASS) return res.status(503).json({ error: 'Defina ADMIN_USER e ADMIN_PASS nas variáveis da Vercel.' });
      if (bloqueado(ip)) return res.status(429).json({ error: 'Muitas tentativas. Aguarde 15 minutos.' });
      const b = body(req);
      if (!safeEq(b.user || '', USER) || !safeEq(b.pass || '', PASS)) { falhou(ip); return res.status(401).json({ error: 'Usuário ou senha inválidos' }); }
      tentativas.delete(ip);
      setCookie(res, token(), DURACAO);
      return res.status(200).json({ ok: true, user: USER });
    }
    if (a === 'logout') { setCookie(res, '', 0); return res.status(200).json({ ok: true }); }

    const logado = valid(cookieOf(req));
    if (a === 'me') return res.status(200).json({ ok: logado, user: logado ? USER : null, config: { admin: !!(USER && PASS), supabase: !!db.KEY } });
    if (!logado) return res.status(401).json({ error: 'Não autenticado' });

    if (a === 'produtos') {
      const rows = await db.select('produtos', 'select=*&order=id.asc&limit=5000');
      return res.status(200).json(rows.map(db.toSite));
    }
    if (a === 'produto') {
      if (req.method === 'DELETE') {
        const id = +req.query.id; if (!Number.isFinite(id)) return res.status(400).json({ error: 'id' });
        const r = await db.remove('produtos', 'id=eq.' + id);
        return res.status(200).json({ ok: true, removidos: r.length });
      }
      if (req.method !== 'POST') return res.status(405).end();
      const b = body(req);
      const p = limparProduto(b);
      let r;
      if (b.id != null && b.id !== '') r = await db.update('produtos', 'id=eq.' + (+b.id), p);
      else r = await db.insert('produtos', p, true);
      if (p.top5) { // garante posição única no Top 5
        await db.update('produtos', 'top5=eq.' + p.top5 + '&id=neq.' + r[0].id, { top5: null }).catch(() => {});
      }
      return res.status(200).json(db.toSite(r[0]));
    }
    if (a === 'upload') {
      if (req.method !== 'POST') return res.status(405).end();
      const b = body(req);
      const m = /^data:(image\/(jpeg|png|webp));base64,(.+)$/.exec(String(b.dados || ''));
      if (!m) return res.status(400).json({ error: 'Envie uma imagem JPG, PNG ou WebP' });
      const buf = Buffer.from(m[3], 'base64');
      if (buf.length > 4 * 1024 * 1024) return res.status(413).json({ error: 'Imagem acima de 4 MB' });
      const ext = m[2] === 'jpeg' ? 'jpg' : m[2];
      const slug = String(b.nome || 'foto').toLowerCase().normalize('NFD').replace(/[̀-ͯ]/g, '').replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '').slice(0, 60);
      const nome = slug + '-' + Date.now().toString(36) + '.' + ext;
      const url = await db.upload(nome, buf, m[1]);
      return res.status(200).json({ url });
    }
    if (a === 'stats') {
      const dias = Math.min(365, Math.max(1, +req.query.dias || 30));
      const r = await db.rpc('stats_resumo', { dias });
      return res.status(200).json(r);
    }
    if (a === 'leads') {
      const rows = await db.select('leads', 'select=*&order=criado_em.desc&limit=5000');
      return res.status(200).json(rows);
    }
    if (a === 'lead' && req.method === 'DELETE') {
      const id = +req.query.id; if (!Number.isFinite(id)) return res.status(400).json({ error: 'id' });
      await db.remove('leads', 'id=eq.' + id);
      return res.status(200).json({ ok: true });
    }
    return res.status(404).json({ error: 'ação desconhecida' });
  } catch (e) {
    return res.status(500).json({ error: e.message });
  }
};
