// Painel administrativo — API única (?a=acao). Sessão validada no banco.
const db = require('./_db');
const A = require('./_auth');
const COOKIE = 'nota_adm';

const ASAAS_BASE = () => (process.env.ASAAS_ENV || 'production') === 'sandbox' ? 'https://api-sandbox.asaas.com/v3' : 'https://api.asaas.com/v3';

// Registra (uma vez) o webhook de pagamentos no Asaas usando a ASAAS_API_KEY já configurada.
async function garantirWebhook(tok, req) {
  const key = process.env.ASAAS_API_KEY;
  if (!key) return { ok: false, motivo: 'ASAAS_API_KEY ausente' };
  const w = await db.rpc('adm_webhook_token', { p_tok: tok });
  if (w.registrado) return { ok: true, ja: true };
  const host = req.headers['x-forwarded-host'] || req.headers.host;
  const url = 'https://' + (/vercel\.app$/.test(host) ? 'notaperfumaria.com' : host) + '/api/asaas-webhook';
  const me = await db.rpc('adm_me', { p_tok: tok });
  const base = { name: 'Nota Perfumaria - pedidos', url, email: me && me.email, enabled: true, interrupted: false, apiVersion: 3, authToken: w.token, sendType: 'SEQUENTIALLY' };
  const H = { 'Content-Type': 'application/json', access_token: key, 'User-Agent': 'NotaPerfumaria' };
  const tentativas = [
    ['PAYMENT_CONFIRMED', 'PAYMENT_RECEIVED', 'PAYMENT_REFUNDED', 'PAYMENT_DELETED', 'PAYMENT_CHARGEBACK_REQUESTED', 'CHECKOUT_PAID', 'CHECKOUT_CANCELED', 'CHECKOUT_EXPIRED'],
    ['PAYMENT_CONFIRMED', 'PAYMENT_RECEIVED', 'PAYMENT_REFUNDED', 'PAYMENT_DELETED', 'PAYMENT_CHARGEBACK_REQUESTED']
  ];
  let ultimo;
  for (const events of tentativas) {
    const r = await fetch(ASAAS_BASE() + '/webhooks', { method: 'POST', headers: H, body: JSON.stringify(Object.assign({}, base, { events })) });
    const d = await r.json().catch(() => ({}));
    if (r.ok && d.id) { await db.rpc('adm_webhook_marcar', { p_tok: tok, p_info: d.id + ' ' + events.length + 'ev' }); return { ok: true, id: d.id }; }
    ultimo = (d.errors && d.errors.map(x => x.description).join('; ')) || ('HTTP ' + r.status);
  }
  return { ok: false, motivo: ultimo };
}

module.exports = async (req, res) => {
  res.setHeader('Cache-Control', 'no-store');
  const a = String(req.query.a || '');
  const ip = A.ipOf(req);
  const tok = A.getCookie(req, COOKIE);
  const b = req.method === 'POST' ? A.body(req) : {};
  try {
    if (a === 'status') return res.status(200).json(await db.rpc('adm_status'));
    if (a === 'setup' || a === 'login') {
      if (req.method !== 'POST') return res.status(405).end();
      if (A.bloqueado('adm:' + ip)) return res.status(429).json({ error: 'Muitas tentativas. Aguarde 15 minutos.' });
      try {
        const r = await db.rpc(a === 'setup' ? 'adm_setup' : 'adm_login', { p_email: String(b.user || ''), p_senha: String(b.pass || '') });
        A.limpa('adm:' + ip);
        A.setCookie(res, COOKIE, r.token, 86400, 'Strict');
        return res.status(200).json({ ok: true, user: r.email });
      } catch (e) { A.falhou('adm:' + ip); throw e; }
    }
    if (a === 'logout') { if (tok) await db.rpc('cli_logout', { p_tok: tok }).catch(() => {}); A.setCookie(res, COOKIE, '', 0, 'Strict'); return res.status(200).json({ ok: true }); }
    if (a === 'me') {
      let me = tok ? await db.rpc('adm_me', { p_tok: tok }) : null;
      const cli = A.getCookie(req, 'nota_cli');
      if (!me && cli) {
        const r = await db.rpc('adm_via_cliente', { p_tok: cli }).catch(() => null);
        if (r && r.token) { A.setCookie(res, COOKIE, r.token, 86400, 'Strict'); me = { email: r.email }; }
      }
      const st = me ? null : await db.rpc('adm_status');
      return res.status(200).json({ ok: !!me, user: me && me.email, setup: st && st.precisa_setup ? st.email_setup : null });
    }
    if (!tok) return res.status(401).json({ error: 'Não autenticado' });
    const P = (fn, args) => db.rpc(fn, Object.assign({ p_tok: tok }, args || {}));

    switch (a) {
      case 'produtos': return res.status(200).json((await P('adm_produtos')).map(db.toSite));
      case 'produto':
        if (req.method === 'DELETE') { await P('adm_produto_excluir', { p_id: +req.query.id }); return res.status(200).json({ ok: true }); }
        {
          const preco = b.preco === '' || b.preco == null ? '' : String(Math.round(Number(String(b.preco).replace(',', '.')) * 100) / 100);
          if (!String(b.marca || '').trim() || !String(b.nome || '').trim()) return res.status(400).json({ error: 'Marca e nome são obrigatórios' });
          if (preco !== '' && !(+preco >= 0)) return res.status(400).json({ error: 'Preço inválido' });
          const p = { id: b.id == null ? '' : String(b.id), marca: String(b.marca).trim().slice(0, 80), nome: String(b.nome).trim().slice(0, 160), genero: ['M', 'F', 'U'].includes(b.genero) ? b.genero : 'U', preco,
            notas: String(b.notas || '').slice(0, 400) || null, lembra: String(b.lembra || '').slice(0, 120) || null, descricao: String(b.descricao || '').slice(0, 2000) || null,
            fotos: Array.isArray(b.fotos) ? b.fotos.filter(x => typeof x === 'string' && x.length < 500).slice(0, 8) : [], ativo: b.ativo !== false, custo: b.custo === '' || b.custo == null ? '' : String(Math.round(Number(String(b.custo).replace(',', '.')) * 100) / 100), mais_vendido: !!b.mais_vendido, top5: b.top5 ? String(Math.min(5, Math.max(1, +b.top5))) : '' };
          return res.status(200).json(db.toSite(await P('adm_produto_salvar', { p })));
        }
      case 'upload': {
        const m = /^data:(image\/(jpeg|png|webp));base64,(.+)$/.exec(String(b.dados || ''));
        if (!m) return res.status(400).json({ error: 'Envie uma imagem JPG, PNG ou WebP' });
        if (m[3].length > 5.5e6) return res.status(413).json({ error: 'Imagem acima de 4 MB' });
        const id = await P('adm_foto_salvar', { p_mime: m[1], p_b64: m[3] });
        return res.status(200).json({ url: '/api/foto?id=' + id });
      }
      case 'videos': return res.status(200).json(await P('adm_videos'));
      case 'video-token': return res.status(200).json({ token: await P('adm_video_token'), url: db.URL, key: db.KEY });
      case 'video': {
        if (req.method === 'DELETE' || b.excluir) { await P('adm_video_excluir', { p_id: +(b.id || req.query.id) }); return res.status(200).json({ ok: true }); }
        return res.status(200).json(await P('adm_video_salvar', { p: { id: b.id || null, src: String(b.src || ''), poster: String(b.poster || ''), nome: String(b.nome || '').slice(0, 80), produto_id: b.produto_id === '' || b.produto_id == null ? null : +b.produto_id, ativo: b.ativo !== false, ordem: +b.ordem || 0 } }));
      }
      case 'stats': return res.status(200).json(await P('adm_stats', { p_dias: Math.min(365, Math.max(1, +req.query.dias || 30)) }));
      case 'leads': return res.status(200).json(await P('adm_leads'));
      case 'lead': await P('adm_lead_excluir', { p_id: +req.query.id }); return res.status(200).json({ ok: true });
      case 'pedidos': return res.status(200).json(await P('adm_pedidos'));
      case 'pedido': {
        const STS = ['aguardando_pagamento', 'pago', 'em_separacao', 'enviado', 'entregue', 'cancelado'];
        const r = await P('adm_pedido_atualizar', { p_id: +b.id, p_status: STS.includes(b.status) ? b.status : null, p_rastreio: b.rastreio == null ? null : String(b.rastreio).slice(0, 40), p_set_rastreio: b.rastreio !== undefined });
        return res.status(200).json(r);
      }
      case 'clientes': return res.status(200).json(await P('adm_clientes'));
      case 'cliente-senha': await P('adm_cliente_senha', { p_id: +b.id, p_nova: String(b.nova || '') }); return res.status(200).json({ ok: true });
      case 'senha': await P('adm_trocar_senha', { p_atual: String(b.atual || ''), p_nova: String(b.nova || '') }); return res.status(200).json({ ok: true });
      case 'afiliados': return res.status(200).json(await P('adm_afiliados'));
      case 'afiliado': {
        const nome = String(b.nome || '').trim().replace(/\s+/g, ' ');
        const whatsapp = A.fone(b.whatsapp);
        const pct = Number(String(b.comissao_pct || '').replace(',', '.'));
        if (nome.split(' ').length < 2) return res.status(400).json({ error: 'Informe nome e sobrenome.' });
        if (!whatsapp) return res.status(400).json({ error: 'WhatsApp inválido (DDD + número).' });
        if (!String(b.pix || '').trim()) return res.status(400).json({ error: 'Informe a chave PIX.' });
        if (!(pct >= 0 && pct <= 50)) return res.status(400).json({ error: 'Comissão deve estar entre 0% e 50%.' });
        try { return res.status(200).json(await P('adm_afiliado_salvar', { p: { id: b.id == null ? '' : String(b.id), nome, whatsapp, pix: String(b.pix).trim(), comissao_pct: String(pct), ativo: b.ativo !== false } })); }
        catch (e) { if (/duplicate|unique/i.test(e.message)) return res.status(400).json({ error: 'Já existe um afiliado com este WhatsApp.' }); throw e; }
      }
      case 'afiliado-convite': return res.status(200).json({ convite: await P('adm_afiliado_novo_convite', { p_id: +b.id }) });
      case 'comissao': await P('adm_comissao_pagar', { p_pedido: +b.pedido_id, p_paga: !!b.paga }); return res.status(200).json({ ok: true });
      case 'financeiro': {
        const iso = d => /^\d{4}-\d{2}-\d{2}$/.test(String(d || '')) ? d : null;
        const hoje = new Date(Date.now() - 3 * 3600e3).toISOString().slice(0, 10);
        return res.status(200).json(await P('adm_financeiro', { p_ini: iso(req.query.ini) || hoje.slice(0, 8) + '01', p_fim: iso(req.query.fim) || hoje }));
      }
      case 'lancamentos': return res.status(200).json(await P('adm_lancamentos'));
      case 'lancamento': {
        if (req.method === 'DELETE') { await P('adm_lancamento_excluir', { p_id: +req.query.id }); return res.status(200).json({ ok: true }); }
        const valor = Math.round(Number(String(b.valor || '').replace(/\./g, '').replace(',', '.')) * 100) / 100;
        if (!['pagar', 'receber'].includes(b.tipo)) return res.status(400).json({ error: 'Tipo inválido' });
        if (!String(b.descricao || '').trim()) return res.status(400).json({ error: 'Informe a descrição' });
        if (!(valor >= 0)) return res.status(400).json({ error: 'Valor inválido' });
        if (!/^\d{4}-\d{2}-\d{2}$/.test(String(b.vencimento || ''))) return res.status(400).json({ error: 'Informe o vencimento' });
        return res.status(200).json(await P('adm_lancamento_salvar', { p: { id: b.id == null ? '' : String(b.id), tipo: b.tipo, descricao: String(b.descricao).trim(), categoria: String(b.categoria || '').trim(), valor: String(valor), vencimento: b.vencimento, quitado_em: b.quitado_em || '', obs: String(b.obs || '') } }));
      }
      case 'socios': return res.status(200).json(await P('adm_socios'));
      case 'socio': {
        if (req.method === 'DELETE') { await P('adm_socio_excluir', { p_id: +req.query.id }); return res.status(200).json({ ok: true }); }
        const pct = Number(String(b.percentual || '').replace(',', '.'));
        if (!String(b.nome || '').trim()) return res.status(400).json({ error: 'Informe o nome' });
        if (!(pct >= 0 && pct <= 100)) return res.status(400).json({ error: 'Percentual entre 0 e 100' });
        return res.status(200).json(await P('adm_socio_salvar', { p: { id: b.id == null ? '' : String(b.id), nome: String(b.nome).trim(), tipo: b.tipo === 'empresa' ? 'empresa' : 'socio', percentual: String(pct), obs: String(b.obs || '') } }));
      }
      case 'custo': {
        const c = b.custo === '' || b.custo == null ? null : Math.round(Number(String(b.custo).replace(',', '.')) * 100) / 100;
        if (c != null && !(c >= 0)) return res.status(400).json({ error: 'Custo inválido' });
        await P('adm_custo', { p_id: +b.id, p_custo: c }); return res.status(200).json({ ok: true });
      }
      case 'webhook': return res.status(200).json(await garantirWebhook(tok, req));
    }
    return res.status(404).json({ error: 'ação desconhecida' });
  } catch (e) { return A.fail(res, e); }
};
