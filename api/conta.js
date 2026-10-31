// Área do cliente: cadastro, login, logout, dados e pedidos (?a=acao).
const db = require('./_db');
const A = require('./_auth');
const COOKIE = 'nota_cli';
const HORAS = 24 * 30; // 30 dias

const STATUS = { aguardando_pagamento: 'Aguardando pagamento', pago: 'Pagamento aprovado', em_separacao: 'Em separação', enviado: 'Enviado', entregue: 'Entregue', cancelado: 'Cancelado' };

function publico(c) { return { id: c.id, nome: c.nome, email: c.email, whatsapp: c.whatsapp, cpf: c.cpf.replace(/^(\d{3})\d{6}(\d{2})$/, '$1.***.***-$2') }; }
function pedidoPublico(p) {
  return { codigo: p.codigo, produto: p.produto_nome, quantidade: p.quantidade, total: Number(p.total), metodo: p.metodo, parcelas: p.parcelas, status: p.status, status_txt: STATUS[p.status] || p.status, rastreio: p.rastreio, endereco: p.endereco, criado_em: p.criado_em, historico: p.historico || [] };
}
async function clienteLogado(req) {
  const sub = A.readToken(A.getCookie(req, COOKIE));
  if (!sub || !sub.startsWith('c:')) return null;
  const r = await db.select('clientes', 'select=*&id=eq.' + (+sub.slice(2)));
  return r[0] || null;
}

module.exports = async (req, res) => {
  res.setHeader('Cache-Control', 'no-store');
  const a = String(req.query.a || '');
  const ip = A.ipOf(req);
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
      const ja = await db.select('clientes', 'select=id,email,cpf&or=(email.eq.' + encodeURIComponent(email) + ',cpf.eq.' + cpf + ')');
      if (ja.length) return res.status(409).json({ error: ja[0].email === email ? 'Já existe uma conta com este e-mail. Faça login.' : 'Já existe uma conta com este CPF. Faça login.' });
      const r = await db.insert('clientes', { nome, cpf, email, whatsapp, senha_hash: A.hashSenha(senha), marketing: b.marketing !== false, ultimo_login: new Date().toISOString() });
      const c = r[0];
      // vincula compras feitas antes do cadastro com o mesmo CPF
      db.update('pedidos', 'cliente_id=is.null&pagador_cpf=eq.' + cpf, { cliente_id: c.id }).catch(() => {});
      db.insert('leads', { nome, whatsapp, email, origem: 'cadastro' }, false).catch(() => {});
      A.setCookie(res, COOKIE, A.makeToken('c:' + c.id, HORAS), HORAS * 3600);
      return res.status(200).json({ ok: true, cliente: publico(c) });
    }

    if (a === 'login') {
      if (req.method !== 'POST') return res.status(405).end();
      if (A.bloqueado('cli:' + ip)) return res.status(429).json({ error: 'Muitas tentativas. Aguarde 15 minutos.' });
      const b = A.body(req);
      const id = String(b.login || '').trim().toLowerCase();
      const cpf = id.replace(/\D/g, '');
      const q = id.includes('@') ? 'email=eq.' + encodeURIComponent(id) : 'cpf=eq.' + cpf;
      const r = (id && (id.includes('@') || cpf.length === 11)) ? await db.select('clientes', 'select=*&' + q) : [];
      const c = r[0];
      if (!c || !A.confereSenha(b.senha || '', c.senha_hash)) { A.falhou('cli:' + ip); return res.status(401).json({ error: 'E-mail/CPF ou senha inválidos.' }); }
      A.limpa('cli:' + ip);
      db.update('clientes', 'id=eq.' + c.id, { ultimo_login: new Date().toISOString() }).catch(() => {});
      A.setCookie(res, COOKIE, A.makeToken('c:' + c.id, HORAS), HORAS * 3600);
      return res.status(200).json({ ok: true, cliente: publico(c) });
    }

    if (a === 'logout') { A.setCookie(res, COOKIE, '', 0); return res.status(200).json({ ok: true }); }

    const c = await clienteLogado(req);
    if (a === 'me') return res.status(200).json({ ok: !!c, cliente: c ? publico(c) : null });
    if (!c) return res.status(401).json({ error: 'Faça login.' });

    if (a === 'pedidos') {
      const r = await db.select('pedidos', 'select=*&cliente_id=eq.' + c.id + '&order=criado_em.desc&limit=100');
      return res.status(200).json(r.map(pedidoPublico));
    }
    if (a === 'senha') {
      if (req.method !== 'POST') return res.status(405).end();
      const b = A.body(req);
      if (!A.confereSenha(b.atual || '', c.senha_hash)) return res.status(400).json({ error: 'Senha atual incorreta.' });
      if (String(b.nova || '').length < 8) return res.status(400).json({ error: 'A nova senha precisa ter pelo menos 8 caracteres.' });
      await db.update('clientes', 'id=eq.' + c.id, { senha_hash: A.hashSenha(b.nova) });
      return res.status(200).json({ ok: true });
    }
    return res.status(404).json({ error: 'ação desconhecida' });
  } catch (e) {
    return res.status(500).json({ error: e.message });
  }
};
module.exports.STATUS = STATUS;
module.exports.clienteLogado = clienteLogado;
