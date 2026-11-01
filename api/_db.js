// Acesso ao Supabase com a chave PÚBLICA (publishable). Toda operação sensível passa por
// funções no banco (RPC, security definer) que validam sessão de admin/cliente — não há segredo no servidor.
const URL = (process.env.SUPABASE_URL || 'https://vsgqhzvlmocmsclduljw.supabase.co').replace(/\/$/, '');
const KEY = process.env.SUPABASE_KEY || 'sb_publishable_UpJoFjDOrkJ3UMkpNZjZKw_1j05SzNi';

const MSG = {
  NAO_AUTENTICADO: 'Sessão expirada. Faça login novamente.',
  LOGIN_INVALIDO: 'E-mail/CPF ou senha inválidos.',
  EMAIL_EXISTE: 'Já existe uma conta com este e-mail. Faça login.',
  CPF_EXISTE: 'Já existe uma conta com este CPF. Faça login.',
  DADOS_INVALIDOS: 'Confira os dados informados.',
  SENHA_ATUAL: 'Senha atual incorreta.',
  SENHA_CURTA: 'Senha muito curta.',
  SETUP_INDISPONIVEL: 'Cadastro de administrador indisponível para este e-mail.',
  IMAGEM_INVALIDA: 'Imagem inválida ou muito grande.',
  NAO_ENCONTRADO: 'Registro não encontrado.',
  TOKEN_INVALIDO: 'Token inválido.',
  CONVITE_INVALIDO: 'Este link de ativação já foi usado ou expirou. Peça um novo à loja.'
};

class DbError extends Error { constructor(code, msg, status) { super(msg); this.code = code; this.status = status; } }

async function req(method, path, body) {
  const r = await fetch(URL + '/rest/v1/' + path, {
    method,
    headers: { apikey: KEY, Authorization: 'Bearer ' + KEY, 'Content-Type': 'application/json', Prefer: 'return=representation' },
    body: body === undefined ? undefined : JSON.stringify(body)
  });
  const txt = await r.text();
  let data = null; try { data = txt ? JSON.parse(txt) : null; } catch (e) { data = txt; }
  if (!r.ok) {
    const raw = (data && (data.message || data.hint)) || ('Supabase ' + r.status);
    const code = Object.keys(MSG).find(k => raw.includes(k));
    throw new DbError(code || 'ERRO', code ? MSG[code] : raw, code === 'NAO_AUTENTICADO' ? 401 : code ? 400 : 500);
  }
  return data;
}

module.exports = {
  URL, KEY, DbError,
  select: (table, query) => req('GET', table + '?' + query),
  rpc: (fn, args) => req('POST', 'rpc/' + fn, args || {}),
  toSite(p) {
    return { id: p.id, b: p.marca, n: p.nome, g: p.genero, p: p.preco == null ? null : Number(p.preco), notes: p.notas || '', like: p.lembra || null, desc: p.descricao || null, pics: Array.isArray(p.fotos) && p.fotos.length ? p.fotos : null, best: !!p.mais_vendido, top5: p.top5 || null, ativo: p.ativo };
  }
};
