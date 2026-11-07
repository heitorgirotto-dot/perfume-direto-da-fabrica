// Markdown simples e seguro para os artigos do blog (títulos, negrito, itálico, links, imagens, listas, citações).
const esc = s => String(s == null ? '' : s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
const urlOk = u => /^(https?:\/\/|\/)[^\s"'<>]*$/i.test(u);

function inline(t) {
  t = esc(t);
  t = t.replace(/!\[([^\]]*)\]\(([^)\s]+)\)/g, (m, alt, u) => urlOk(u) ? `<img src="${u}" alt="${alt}" loading="lazy">` : m);
  t = t.replace(/\[([^\]]+)\]\(([^)\s]+)\)/g, (m, txt, u) => urlOk(u) ? `<a href="${u}"${/^https?:/.test(u) && !/notaperfumaria\.com/.test(u) ? ' target="_blank" rel="noopener"' : ''}>${txt}</a>` : m);
  t = t.replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>');
  t = t.replace(/(^|[^*])\*([^*\s][^*]*)\*/g, '$1<em>$2</em>');
  return t;
}

function md(src) {
  const linhas = String(src || '').replace(/\r/g, '').split('\n');
  const out = []; let par = [], lista = null, cit = [];
  const fechaPar = () => { if (par.length) { out.push('<p>' + inline(par.join(' ')) + '</p>'); par = []; } };
  const fechaLista = () => { if (lista) { out.push(`<${lista.tipo}>` + lista.itens.map(i => '<li>' + inline(i) + '</li>').join('') + `</${lista.tipo}>`); lista = null; } };
  const fechaCit = () => { if (cit.length) { out.push('<blockquote>' + inline(cit.join(' ')) + '</blockquote>'); cit = []; } };
  const fechaTudo = () => { fechaPar(); fechaLista(); fechaCit(); };
  for (const l of linhas) {
    const t = l.trim();
    let m;
    if (!t) { fechaTudo(); continue; }
    if ((m = /^(#{2,4})\s+(.+)$/.exec(t))) { fechaTudo(); const n = Math.min(4, m[1].length); out.push(`<h${n}>${inline(m[2])}</h${n}>`); continue; }
    if (/^#\s+/.test(t)) { fechaTudo(); out.push(`<h2>${inline(t.replace(/^#\s+/, ''))}</h2>`); continue; }
    if ((m = /^[-*]\s+(.+)$/.exec(t))) { fechaPar(); fechaCit(); if (!lista || lista.tipo !== 'ul') { fechaLista(); lista = { tipo: 'ul', itens: [] }; } lista.itens.push(m[1]); continue; }
    if ((m = /^\d+[.)]\s+(.+)$/.exec(t))) { fechaPar(); fechaCit(); if (!lista || lista.tipo !== 'ol') { fechaLista(); lista = { tipo: 'ol', itens: [] }; } lista.itens.push(m[1]); continue; }
    if ((m = /^>\s?(.*)$/.exec(t))) { fechaPar(); fechaLista(); cit.push(m[1]); continue; }
    if (/^!\[[^\]]*\]\([^)]+\)$/.test(t)) { fechaTudo(); out.push('<figure>' + inline(t) + '</figure>'); continue; }
    fechaLista(); fechaCit(); par.push(t);
  }
  fechaTudo();
  return out.join('\n');
}
const texto = src => String(src || '').replace(/!\[[^\]]*\]\([^)]*\)/g, '').replace(/\[([^\]]+)\]\([^)]*\)/g, '$1').replace(/[#>*_`-]+/g, ' ').replace(/\s+/g, ' ').trim();
module.exports = { md, esc, texto };
