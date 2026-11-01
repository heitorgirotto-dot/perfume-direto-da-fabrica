// Área do afiliado: ativar acesso pelo convite, login (WhatsApp + senha) e painel de vendas/comissões.
const db = require('./_db');
const A = require('./_auth');
const COOKIE = 'nota_afi';

module.exports = async (req, res) => {
  res.setHeader('Cache-Control', 'no-store');
  const a = String(req.query.a || '');
  const ip = A.ipOf(req);
  const tok = A.getCookie(req, COOKIE);
  const b = req.method === 'POST' ? A.body(req) : {};
  try {
    if (a === 'convite') return res.status(200).json(await db.rpc('afi_convite', { p_convite: String(req.query.c || '') }) || null);
    if (a === 'ativar' || a === 'login') {
      if (req.method !== 'POST') return res.status(405).end();
      if (A.bloqueado('afi:' + ip)) return res.status(429).json({ error: 'Muitas tentativas. Aguarde 15 minutos.' });
      try {
        const r = a === 'ativar'
          ? await db.rpc('afi_ativar', { p_convite: String(b.convite || ''), p_senha: String(b.senha || '') })
          : await db.rpc('afi_login', { p_whatsapp: A.fone(b.whatsapp) || '', p_senha: String(b.senha || '') });
        A.limpa('afi:' + ip);
        A.setCookie(res, COOKIE, r.token, 30 * 86400);
        return res.status(200).json({ ok: true });
      } catch (e) { A.falhou('afi:' + ip); if (e.code === 'LOGIN_INVALIDO') e.message = 'WhatsApp ou senha inválidos.'; throw e; }
    }
    if (a === 'logout') { if (tok) await db.rpc('cli_logout', { p_tok: tok }).catch(() => {}); A.setCookie(res, COOKIE, '', 0); return res.status(200).json({ ok: true }); }
    if (a === 'painel') {
      if (!tok) return res.status(401).json({ error: 'Faça login.' });
      return res.status(200).json(await db.rpc('afi_painel', { p_tok: tok }));
    }
    return res.status(404).json({ error: 'ação desconhecida' });
  } catch (e) { return A.fail(res, e); }
};
