// Acesso ao Supabase via REST (PostgREST) com a chave de serviço.
// Variáveis na Vercel: SUPABASE_URL (opcional, já tem padrão) e SUPABASE_SERVICE_ROLE_KEY (obrigatória).
const URL = (process.env.SUPABASE_URL || 'https://vsgqhzvlmocmsclduljw.supabase.co').replace(/\/$/, '');
const KEY = process.env.SUPABASE_SERVICE_ROLE_KEY || '';

function headers(extra) {
  return Object.assign({ apikey: KEY, Authorization: 'Bearer ' + KEY, 'Content-Type': 'application/json' }, extra || {});
}

async function rest(method, path, body, extra) {
  if (!KEY) throw new Error('SUPABASE_SERVICE_ROLE_KEY não configurada na Vercel');
  const r = await fetch(URL + '/rest/v1/' + path, { method, headers: headers(extra), body: body === undefined ? undefined : JSON.stringify(body) });
  const txt = await r.text();
  let data = null; try { data = txt ? JSON.parse(txt) : null; } catch (e) { data = txt; }
  if (!r.ok) throw new Error((data && (data.message || data.hint)) || ('Supabase ' + r.status));
  return data;
}

module.exports = {
  URL, KEY,
  select: (table, query) => rest('GET', table + '?' + query),
  insert: (table, rows, ret) => rest('POST', table, rows, { Prefer: ret === false ? 'return=minimal' : 'return=representation' }),
  update: (table, query, patch) => rest('PATCH', table + '?' + query, patch, { Prefer: 'return=representation' }),
  remove: (table, query) => rest('DELETE', table + '?' + query, undefined, { Prefer: 'return=representation' }),
  rpc: (fn, args) => rest('POST', 'rpc/' + fn, args || {}),
  // Upload binário para o Storage (bucket público "fotos"). Retorna a URL pública.
  async upload(nome, buffer, contentType) {
    if (!KEY) throw new Error('SUPABASE_SERVICE_ROLE_KEY não configurada na Vercel');
    const r = await fetch(URL + '/storage/v1/object/fotos/' + nome, {
      method: 'POST',
      headers: { apikey: KEY, Authorization: 'Bearer ' + KEY, 'Content-Type': contentType || 'application/octet-stream', 'x-upsert': 'true' },
      body: buffer
    });
    if (!r.ok) throw new Error('Storage ' + r.status + ': ' + (await r.text()).slice(0, 200));
    return URL + '/storage/v1/object/public/fotos/' + nome;
  },
  // Formato usado pelo site
  toSite(p) {
    return { id: p.id, b: p.marca, n: p.nome, g: p.genero, p: p.preco == null ? null : Number(p.preco), notes: p.notas || '', like: p.lembra || null, desc: p.descricao || null, pics: Array.isArray(p.fotos) && p.fotos.length ? p.fotos : null, best: !!p.mais_vendido, top5: p.top5 || null, ativo: p.ativo };
  }
};
