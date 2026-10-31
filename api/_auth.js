// Utilitários HTTP de sessão (o token é gerado e validado no banco).
function getCookie(req, nome) {
  const m = (req.headers.cookie || '').match(new RegExp('(?:^|;\\s*)' + nome + '=([^;]+)'));
  return m ? decodeURIComponent(m[1]) : null;
}
function setCookie(res, nome, v, maxAge, sameSite) {
  const prev = res.getHeader('Set-Cookie');
  const c = nome + '=' + encodeURIComponent(v) + '; Path=/; HttpOnly; Secure; SameSite=' + (sameSite || 'Lax') + '; Max-Age=' + maxAge;
  res.setHeader('Set-Cookie', prev ? [].concat(prev, c) : c);
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
function fail(res, e) { res.status(e.status || 500).json({ error: e.message }); }

module.exports = { getCookie, setCookie, cpfValido, fone, body, bloqueado, falhou, limpa, ipOf, fail };
