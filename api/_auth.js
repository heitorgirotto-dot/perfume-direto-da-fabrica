// Utilitários de autenticação compartilhados (cliente e admin).
const crypto = require('crypto');

const SECRET = process.env.AUTH_SECRET || process.env.ADMIN_SECRET ||
  crypto.createHash('sha256').update('nota|' + (process.env.SUPABASE_SERVICE_ROLE_KEY || '') + '|' + (process.env.ADMIN_PASS || '')).digest('hex');

function sign(s) { return crypto.createHmac('sha256', SECRET).update(s).digest('base64url'); }
function makeToken(sub, horas) { const exp = Math.floor(Date.now() / 1000) + horas * 3600; const p = sub + '|' + exp; return p + '|' + sign(p); }
function readToken(t) {
  if (!t) return null;
  const i = t.lastIndexOf('|'); if (i < 0) return null;
  const p = t.slice(0, i), s = t.slice(i + 1);
  const a = Buffer.from(sign(p)), b = Buffer.from(s);
  if (a.length !== b.length || !crypto.timingSafeEqual(a, b)) return null;
  const [sub, exp] = p.split('|');
  return +exp > Date.now() / 1000 ? sub : null;
}
function getCookie(req, nome) {
  const m = (req.headers.cookie || '').match(new RegExp('(?:^|;\\s*)' + nome + '=([^;]+)'));
  return m ? decodeURIComponent(m[1]) : null;
}
function setCookie(res, nome, v, maxAge) {
  const prev = res.getHeader('Set-Cookie');
  const c = nome + '=' + encodeURIComponent(v) + '; Path=/; HttpOnly; Secure; SameSite=Lax; Max-Age=' + maxAge;
  res.setHeader('Set-Cookie', prev ? [].concat(prev, c) : c);
}
function hashSenha(senha) {
  const salt = crypto.randomBytes(16);
  const h = crypto.scryptSync(String(senha), salt, 64);
  return 'scrypt$' + salt.toString('base64') + '$' + h.toString('base64');
}
function confereSenha(senha, hash) {
  const [alg, s, h] = String(hash || '').split('$');
  if (alg !== 'scrypt' || !s || !h) return false;
  const calc = crypto.scryptSync(String(senha), Buffer.from(s, 'base64'), 64);
  const ref = Buffer.from(h, 'base64');
  return ref.length === calc.length && crypto.timingSafeEqual(ref, calc);
}
function cpfValido(c) {
  c = String(c || '').replace(/\D/g, '');
  if (c.length !== 11 || /^(\d)\1+$/.test(c)) return false;
  for (let t = 9; t < 11; t++) {
    let s = 0; for (let i = 0; i < t; i++) s += +c[i] * (t + 1 - i);
    if (((10 * s) % 11) % 10 !== +c[t]) return false;
  }
  return true;
}
function fone(v) {
  let d = String(v || '').replace(/\D/g, '').replace(/^0+/, '');
  if (d.length === 10 || d.length === 11) d = '55' + d;
  return d.length >= 12 && d.length <= 13 ? d : null;
}
function body(req) {
  if (req.body && typeof req.body === 'object') return req.body;
  try { return JSON.parse(req.body || '{}'); } catch (e) { return {}; }
}
const tentativas = new Map();
function bloqueado(k) { const r = tentativas.get(k); return r && r.n >= 8 && Date.now() - r.t < 15 * 60e3; }
function falhou(k) { const r = tentativas.get(k) || { n: 0, t: 0 }; r.n++; r.t = Date.now(); tentativas.set(k, r); }
function limpa(k) { tentativas.delete(k); }
function ipOf(req) { return String(req.headers['x-forwarded-for'] || '').split(',')[0].trim() || 'x'; }

module.exports = { makeToken, readToken, getCookie, setCookie, hashSenha, confereSenha, cpfValido, fone, body, bloqueado, falhou, limpa, ipOf };
