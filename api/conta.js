// Área do cliente: cadastro, login, logout, dados e pedidos (?a=acao).
const db = require('./_db');
const A = require('./_auth');
const COOKIE = 'nota_cli';
const DIAS = 30;
const STATUS = { aguardando_pagamento: 'Aguardando pagamento', pago: 'Pagamento aprovado', em_separacao: 'Em separação', enviado: 'Enviado', entregue: 'Entregue', cancelado: 'Cancelado' };

module.exports = async (req, res) => {
  res.setHeader('Cache-Control', 'no-store');
  const a = String(req.query.a || '');
  const ip = A.ipOf(req);
  const tok = A.getCookie(req, COOKIE);
  try {
    if (a === 'cadastro') {
      if (req.method !== 'POST') return res.status(405).end();
      const b = A.body(req);
      const nome = String(b.nome || '').trim().replace(/\s+/g, ' ').slice(0, 80);
      const cpf = String(b.cpf || '').replace(/\D/g, '');
      const email = String(b.email || '').trim().toLowerCase().slice(0, 120);
      const whatsapp = A.fone(b.whatsapp);
      const senha = String(b.senha || '');
      if (nome.split(' ').length < 2) return res.status(400).json({ error: 'Informe nome e sobrenome.' });
      if (!A.cpfValido(cpf)) return res.status(400).json({ error: 'CPF inválido.' });
      if (!/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(email)) return res.status(400).json({ error: 'E-mail inválido.' });
      if (!whatsapp) return res.status(400).json({ error: 'WhatsApp inválido (use DDD + número).' });
      if (senha.length < 8) return res.status(400).json({ error: 'A senha precisa ter pelo menos 8 caracteres.' });
      if (!b.aceite) return res.status(400).json({ error: 'É preciso aceitar a política de privacidade.' });
      const r = await db.rpc('cli_cadastrar', { p: { nome, cpf, email, whatsapp, senha, marketing: b.marketing !== false } });
      db.rpc('lead_registrar', { p: { nome, whatsapp, email, origem: 'cadastro' } }).catch(() => {});
      A.setCookie(res, COOKIE, r.token, DIAS * 86400);
      return res.status(200).json({ ok: true, cliente: r.cliente });
    }
    if (a === 'login') {
      if (req.method !== 'POST') return res.status(405).end();
      if (A.bloqueado('cli:' + ip)) return res.status(429).json({ error: 'Muitas tentativas. Aguarde 15 minutos.' });
      const b = A.body(req);
      try {
        const r = await db.rpc('cli_login', { p_login: String(b.login || ''), p_senha: String(b.senha || '') });
        A.limpa('cli:' + ip);
        A.setCookie(res, COOKIE, r.token, DIAS * 86400);
        return res.status(200).json({ ok: true, cliente: r.cliente });
      } catch (e) { A.falhou('cli:' + ip); throw e; }
    }
    if (a === 'logout') {
      if (tok) await db.rpc('cli_logout', { p_tok: tok }).catch(() => {});
      A.setCookie(res, COOKIE, '', 0);
      return res.status(200).json({ ok: true });
    }
    if (a === 'me') {
      const c = tok ? await db.rpc('cli_me', { p_tok: tok }) : null;
      return res.status(200).json({ ok: !!c, cliente: c || null });
    }
    if (!tok) return res.status(401).json({ error: 'Faça login.' });
    if (a === 'pedidos') {
      const r = await db.rpc('cli_pedidos', { p_tok: tok });
      return res.status(200).json((r || []).map(p => Object.assign(p, { total: Number(p.total), status_txt: STATUS[p.status] || p.status })));
    }
    if (a === 'senha' && req.method === 'POST') {
      const b = A.body(req);
      await db.rpc('cli_trocar_senha', { p_tok: tok, p_atual: String(b.atual || ''), p_nova: String(b.nova || '') });
      return res.status(200).json({ ok: true });
    }
    return res.status(404).json({ error: 'ação desconhecida' });
  } catch (e) { return A.fail(res, e); }
};
