// Páginas indexáveis: /p/<produto> e /c/<categoria>. Serve o index.html com título, meta,
// JSON-LD e conteúdo do produto/categoria já renderizado (o JS da página assume depois).
const fs = require('fs');
const path = require('path');
const C = require('./_catalogo');
const { taxas } = require('./_taxas');
const MD = require('./_md');
const DB = require('./_db');
async function posts(q) { try { const r = await DB.select('posts', q); return Array.isArray(r) ? r : []; } catch (e) { return []; } }
const dataBR = d => new Date(d).toLocaleDateString('pt-BR', { day: '2-digit', month: 'long', year: 'numeric', timeZone: 'America/Sao_Paulo' });

let TPL = null;
function template() {
  if (TPL) return TPL;
  for (const p of [path.join(process.cwd(), 'index.html'), path.join(__dirname, '..', 'index.html')]) {
    try { TPL = fs.readFileSync(p, 'utf8'); return TPL; } catch (e) { /* tenta o próximo */ }
  }
  throw new Error('index.html não encontrado');
}

function head(html, { title, desc, url, image, extra }) {
  html = html.replace(/<title>[^<]*<\/title>/, `<title>${C.esc(title)}</title>`);
  html = html.replace(/<meta name="description" content="[^"]*">/, `<meta name="description" content="${C.esc(desc)}">`);
  html = html.replace(/<link rel="canonical" href="[^"]*">/, `<link rel="canonical" href="${url}">`);
  html = html.replace(/<meta property="og:url" content="[^"]*">/, `<meta property="og:url" content="${url}">`);
  html = html.replace(/<meta property="og:title" content="[^"]*">/, `<meta property="og:title" content="${C.esc(title)}">`);
  html = html.replace(/<meta property="og:description" content="[^"]*">/, `<meta property="og:description" content="${C.esc(desc)}">`);
  const og = `<style>body.pg-p .cover-wide,body.pg-p .hero-split,body.pg-p .exp,body.pg-c .cover-wide,body.pg-c .hero-split,body.pg-c .exp,body.pg-c #vendidos,body.pg-c #familias,body.pg-c #bn-autoridade,body.pg-c #top5,body.pg-c #top5-sec,body.pg-c #ocasioes,body.pg-c #bn-atendimento,body.pg-c #assinatura{display:none!important}</style><meta property="og:type" content="${image ? 'product' : 'website'}"><meta property="og:image" content="${image || C.BASE + '/img/logo.jpg'}"><meta name="twitter:card" content="summary_large_image">`;
  return html.replace('</title>', '</title>\n' + og + (extra || ''));
}

const cardHTML = it => {
  const off = it.p != null && it.po > it.p ? Math.round((1 - it.p / it.po) * 100) : 0;
  const tag = off ? `${off}% OFF` : (it.p != null ? '10% OFF no PIX' : '');
  const price = it.p == null ? '<div class="h-pr">Consultar</div>' : `${off ? `<div class="h-cmp">${C.brl(it.po)}</div>` : ''}<div class="h-pr">${C.brl(C.pix(it.p))}<small>no PIX</small></div><div class="h-ins">ou ${C.brl(it.p)} em até 12x</div>`;
  return `<div class="h-card"><a class="h-ph" href="/p/${it.slug}" data-open="${it.id}">${it.img ? `<img src="${it.img}" alt="${C.esc(it.b + ' ' + it.n)}" loading="lazy">` : ''}${tag ? `<span class="h-tags"><span class="h-tag">${tag}</span></span>` : ''}</a>
  <a class="h-n" href="/p/${it.slug}" data-open="${it.id}">${it.carro ? C.esc(it.n) : `${C.esc(it.n)} - ${C.esc(it.b)} - Perfume ${C.G[it.g]}`}</a>${price}${it.p != null ? `<button class="h-buy" type="button" data-add="${it.id}">Comprar</button>` : ''}</div>`;
};

module.exports = async (req, res) => {
  const q = req.query || {};
  const tipo = q.tipo, s = String(q.slug || '').toLowerCase().replace(/[^a-z0-9-]/g, '');
  if (tipo === 'videos') {
    let v = [];
    try { v = await require('./_db').select('videos', 'select=id,src,poster,nome,produto_id&ativo=is.true&order=ordem.asc,id.desc&limit=6'); } catch (e) { v = []; }
    res.setHeader('Cache-Control', 's-maxage=60, stale-while-revalidate=300');
    return res.json(Array.isArray(v) ? v : []);
  }
  if (tipo === 'taxas') { res.setHeader('Cache-Control', 'public, max-age=300'); return res.json(taxas()); }

  if (tipo === 'blog' || tipo === 'post') {
    let html; try { html = template(); } catch (e) { res.statusCode = 302; res.setHeader('Location', '/'); return res.end(); }
    res.setHeader('Content-Type', 'text/html; charset=utf-8');
    const casca = (corpo, cls) => html.replace('<body>', `<body class="pg-blog ${cls}">`).replace('<main id="home">', corpo + '\n<main id="home">');
    const crumb = (itens) => `<nav class="b-crumb" aria-label="Você está em">${itens.map((x, k) => k < itens.length - 1 ? `<a href="${x[1]}">${MD.esc(x[0])}</a><span>›</span>` : `<span>${MD.esc(x[0])}</span>`).join('')}</nav>`;
    if (tipo === 'blog') {
      const lista = await posts('select=slug,titulo,resumo,capa,publicado_em,conteudo&order=publicado_em.desc&limit=60');
      const url = C.BASE + '/blog';
      const desc = 'Blog da Nota Perfumaria: dicas de perfumaria árabe e importada, famílias olfativas, como escolher e fazer seu perfume durar mais.';
      const ld = { '@context': 'https://schema.org', '@type': 'Blog', name: 'Blog Nota Perfumaria', url, blogPost: lista.slice(0, 20).map(p => ({ '@type': 'BlogPosting', headline: p.titulo, url: `${C.BASE}/blog/${p.slug}`, datePublished: p.publicado_em, image: p.capa ? (p.capa.startsWith('http') ? p.capa : C.BASE + p.capa) : undefined })) };
      const cards = lista.length ? lista.map(p => `<article class="b-card"><a class="b-img" href="/blog/${p.slug}">${p.capa ? `<img src="${MD.esc(p.capa)}" alt="${MD.esc(p.titulo)}" loading="lazy">` : ''}</a>
        <div class="b-tx"><h2><a href="/blog/${p.slug}">${MD.esc(p.titulo)}</a></h2><p>${MD.esc(p.resumo || MD.texto(p.conteudo).slice(0, 180))}</p><a class="b-mais" href="/blog/${p.slug}">Leia mais</a></div></article>`).join('')
        : '<p class="b-vazio">Em breve, nossos primeiros artigos.</p>';
      const corpo = `<section class="b-head"><div class="h-w b-head-in"><h1>Blog</h1>${crumb([['Início', '/'], ['Blog', '/blog']])}</div></section>
<section class="b-lista"><div class="h-w"><div class="b-grid">${cards}</div></div></section>`;
      let out = head(casca(corpo, 'pg-blog-lista'), { title: 'Blog · Nota Perfumaria', desc, url, extra: `<script type="application/ld+json">${JSON.stringify(ld)}</script>` });
      res.setHeader('Cache-Control', 's-maxage=120, stale-while-revalidate=600');
      return res.end(out);
    }
    const r = (await posts(`select=*&slug=eq.${encodeURIComponent(s)}&limit=1`))[0];
    if (!r) { res.statusCode = 302; res.setHeader('Location', '/blog'); return res.end(); }
    const url = `${C.BASE}/blog/${r.slug}`;
    const capaAbs = r.capa ? (r.capa.startsWith('http') ? r.capa : C.BASE + r.capa) : null;
    const desc = (r.seo_descricao || r.resumo || MD.texto(r.conteudo)).slice(0, 160);
    const outros = (await posts(`select=slug,titulo,capa,publicado_em&slug=neq.${encodeURIComponent(r.slug)}&order=publicado_em.desc&limit=3`));
    const ld = { '@context': 'https://schema.org', '@type': 'BlogPosting', headline: r.titulo, description: desc, image: capaAbs || undefined, datePublished: r.publicado_em, dateModified: r.atualizado_em,
      author: { '@type': 'Organization', name: r.autor || 'Nota Perfumaria' }, publisher: { '@type': 'Organization', name: 'Nota Perfumaria', logo: { '@type': 'ImageObject', url: C.BASE + '/img/logo-branco.jpg' } }, mainEntityOfPage: url };
    const bc = { '@context': 'https://schema.org', '@type': 'BreadcrumbList', itemListElement: [{ '@type': 'ListItem', position: 1, name: 'Início', item: C.BASE + '/' }, { '@type': 'ListItem', position: 2, name: 'Blog', item: C.BASE + '/blog' }, { '@type': 'ListItem', position: 3, name: r.titulo, item: url }] };
    const wa = `https://wa.me/5511982659792?text=${encodeURIComponent('Olá! Li o artigo "' + r.titulo + '" no blog da Nota e quero uma indicação de perfume.')}`;
    const share = `https://wa.me/?text=${encodeURIComponent(r.titulo + ' ' + url)}`;
    const corpo = `<section class="b-head"><div class="h-w b-head-in"><p class="b-kick">Blog</p>${crumb([['Início', '/'], ['Blog', '/blog'], [r.titulo, '']])}</div></section>
<article class="b-post"><div class="b-w">
  <h1>${MD.esc(r.titulo)}</h1>
  <p class="b-meta">${MD.esc(r.autor || 'Nota Perfumaria')} · <time datetime="${r.publicado_em}">${dataBR(r.publicado_em)}</time></p>
  ${r.capa ? `<img class="b-capa" src="${MD.esc(r.capa)}" alt="${MD.esc(r.titulo)}">` : ''}
  <div class="b-conteudo">${MD.md(r.conteudo)}</div>
  <div class="b-cta"><div><b>Quer ajuda para escolher?</b><span>Um especialista da Nota indica o perfume ideal para você pelo WhatsApp.</span></div><a href="${wa}" target="_blank" rel="noopener">Falar com especialista</a></div>
  <p class="b-share"><a href="${share}" target="_blank" rel="noopener">Compartilhar no WhatsApp</a> · <a href="/blog">Ver todos os artigos</a></p>
</div></article>
${outros.length ? `<section class="b-lista b-rel"><div class="h-w"><h2 class="h-title">Leia também</h2><div class="b-grid">${outros.map(p => `<article class="b-card"><a class="b-img" href="/blog/${p.slug}">${p.capa ? `<img src="${MD.esc(p.capa)}" alt="${MD.esc(p.titulo)}" loading="lazy">` : ''}</a><div class="b-tx"><h2><a href="/blog/${p.slug}">${MD.esc(p.titulo)}</a></h2><a class="b-mais" href="/blog/${p.slug}">Leia mais</a></div></article>`).join('')}</div></div></section>` : ''}`;
    let out = head(casca(corpo, 'pg-blog-post'), { title: (r.seo_titulo || r.titulo) + ' · Nota Perfumaria', desc, url, image: capaAbs, extra: `<script type="application/ld+json">${JSON.stringify(ld)}</script><script type="application/ld+json">${JSON.stringify(bc)}</script>` });
    out = out.replace(/<meta property="og:type" content="[^"]*">/, '<meta property="og:type" content="article">');
    res.setHeader('Cache-Control', 's-maxage=120, stale-while-revalidate=600');
    return res.end(out);
  }
  if (tipo === 'sitemap') {
    const items = await C.produtos();
    const marcas = [...new Set(items.map(i => i.b))].sort();
    const ps = await posts('select=slug&order=publicado_em.desc&limit=500');
    const urls = ['/', '/blog', ...ps.map(p => '/blog/' + p.slug), ...Object.keys(C.CATS).map(k => '/c/' + k), ...marcas.map(b => '/c/' + C.slug(b)), ...items.map(i => '/p/' + i.slug)];
    const hoje = new Date().toISOString().slice(0, 10);
    res.setHeader('Content-Type', 'application/xml; charset=utf-8');
    res.setHeader('Cache-Control', 's-maxage=3600, stale-while-revalidate=86400');
    return res.end('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' +
      urls.map(u => `<url><loc>${C.BASE}${u}</loc><lastmod>${hoje}</lastmod><changefreq>${u === '/' ? 'daily' : 'weekly'}</changefreq><priority>${u === '/' ? '1.0' : u.startsWith('/c/') || u.startsWith('/blog') ? '0.8' : '0.6'}</priority></url>`).join('\n') + '\n</urlset>');
  }
  let html;
  try { html = template(); } catch (e) { res.statusCode = 302; res.setHeader('Location', '/'); return res.end(); }
  const items = await C.produtos();
  res.setHeader('Content-Type', 'text/html; charset=utf-8');

  if (tipo === 'p') {
    const it = items.find(i => i.slug === s);
    if (!it) { res.statusCode = 302; res.setHeader('Location', '/'); return res.end(); }
    const nome = C.nomeCompleto(it);
    const url = `${C.BASE}/p/${it.slug}`;
    const image = it.img ? `${C.BASE}${it.img}` : null;
    const desc = it.carro ? `${nome}: aromatizador automotivo ${C.G[it.g].toLowerCase()} da Nota Perfumaria por ${C.brl(C.pix(it.p))} no PIX ou em até 12x no cartão. Notas: ${it.notes || ''}.${it.like ? ' Perfil olfativo próximo a ' + it.like + '.' : ''} Envio para todo o Brasil.`.slice(0, 300) : `${nome} ${C.G[it.g].toLowerCase()} 100% original${it.p != null ? ` por ${C.brl(C.pix(it.p))} no PIX ou em até 12x no cartão` : ''}. Notas: ${it.notes || ''}.${it.like ? ' Lembra ' + it.like + '.' : ''} Envio para todo o Brasil.`.slice(0, 300);
    const ld = {
      '@context': 'https://schema.org', '@type': 'Product', name: nome, brand: { '@type': 'Brand', name: it.b }, image: it.pics ? it.pics.map(p => `${C.BASE}${p}`) : undefined,
      description: desc, sku: String(it.id), url,
      offers: it.p == null ? undefined : { '@type': 'Offer', url, priceCurrency: 'BRL', price: C.pix(it.p).toFixed(2), availability: 'https://schema.org/InStock', itemCondition: 'https://schema.org/NewCondition', seller: { '@type': 'Organization', name: 'Nota Perfumaria' } }
    };
    const crumb = { '@context': 'https://schema.org', '@type': 'BreadcrumbList', itemListElement: [
      { '@type': 'ListItem', position: 1, name: 'Início', item: C.BASE + '/' },
      { '@type': 'ListItem', position: 2, name: it.b, item: `${C.BASE}/c/${C.slug(it.b)}` },
      { '@type': 'ListItem', position: 3, name: it.n, item: url }] };
    html = head(html, { title: `${nome} · Nota Perfumaria`, desc, url, image, extra: `<script type="application/ld+json">${JSON.stringify(ld)}</script><script type="application/ld+json">${JSON.stringify(crumb)}</script>` });
    const off = it.p != null && it.po > it.p ? Math.round((1 - it.p / it.po) * 100) : 0;
    const bloco = `
<section id="ssr-produto" class="ssr-p"><div class="wrap">
  <p class="cat-crumb"><a href="/">Início</a> › <a href="/c/${C.slug(it.b)}">${C.esc(it.b)}</a> › ${C.esc(it.n)}</p>
  <div class="ssr-g">
    <div class="ssr-m">${it.img ? `<img src="${it.img}" alt="${C.esc(nome)}">` : ''}</div>
    <div class="ssr-i">
      <div class="brand">${C.esc(it.b)}</div><h1>${C.esc(nome)}</h1><span class="pill ${it.g}" style="position:static;display:inline-block">${C.G[it.g]}</span>
      <p class="notes"><b>Notas:</b> ${C.esc(it.notes || '')}</p>${it.like ? `<p class="like">Perfil olfativo próximo a <b>${C.esc(it.like)}</b>${it.carro ? '<br><small style="opacity:.7">Referência de estilo, sem vínculo com a marca citada.</small>' : ''}</p>` : ''}${it.desc ? `<p class="pv-desc">${C.esc(it.desc)}</p>` : ''}
      ${it.p == null ? '<div class="pix">Consultar</div>' : `${off ? `<div class="old">de ${C.brl(it.po)} · ${off}% OFF</div>` : ''}<div class="pix">${C.brl(C.pix(it.p))}<small>no PIX</small></div><div class="full">${C.brl(it.p)} no cartão (até 12x) ou boleto</div>`}
      <div class="acts" style="margin-top:18px"><a class="buy" href="/p/${it.slug}" data-open="${it.id}">Comprar</a><a class="ask" href="https://wa.me/5511982659792?text=${encodeURIComponent('Olá! Tenho uma dúvida sobre ' + nome)}" target="_blank" rel="noopener">Falar com especialista</a></div>
      <p class="msg" style="margin-top:14px">${it.carro ? 'Linha exclusiva Nota Perfumaria' : '100% original e lacrado'} · PIX, boleto ou cartão em até 12x · Envio pelos Correios com rastreio</p>
    </div>
  </div>
</div></section>`;
    html = html.replace('<main id="home">', bloco + '\n<main id="home">').replace('<body>', '<body class="pg-p">');
    res.setHeader('Cache-Control', 's-maxage=300, stale-while-revalidate=3600');
    return res.end(html);
  }

  if (tipo === 'c') {
    const t = C.tituloCat(items, s);
    const list = t ? C.filtrar(items, s) : null;
    if (!list) { res.statusCode = 302; res.setHeader('Location', '/'); return res.end(); }
    const url = `${C.BASE}/c/${s}`;
    const desc = `${t.t} 100% originais na Nota Perfumaria: ${t.s}. ${list.length} fragrâncias com PIX com desconto ou cartão em até 12x e envio para todo o Brasil.`;
    const crumb = { '@context': 'https://schema.org', '@type': 'BreadcrumbList', itemListElement: [{ '@type': 'ListItem', position: 1, name: 'Início', item: C.BASE + '/' }, { '@type': 'ListItem', position: 2, name: t.t, item: url }] };
    const lista = { '@context': 'https://schema.org', '@type': 'ItemList', name: t.t, numberOfItems: list.length, itemListElement: list.slice(0, 40).map((it, k) => ({ '@type': 'ListItem', position: k + 1, url: `${C.BASE}/p/${it.slug}`, name: C.nomeCompleto(it) })) };
    html = head(html, { title: `${t.t} · Nota Perfumaria`, desc, url, extra: `<script type="application/ld+json">${JSON.stringify(crumb)}</script><script type="application/ld+json">${JSON.stringify(lista)}</script>` });
    html = html.replace('<h2 class="h-title"><span id="cat-title">Todos os perfumes</span></h2>', `<h1 class="h-title"><span id="cat-title">${C.esc(t.t)}</span></h1>`)
      .replace('<p id="cat-sub">Mais de 350 fragrâncias originais, das casas árabes às grifes internacionais</p>', `<p id="cat-sub">${C.esc(t.s)}</p>`)
      .replace('<span id="cat-crumb-n">Todos os perfumes</span>', `<span id="cat-crumb-n">${C.esc(t.t)}</span>`)
      .replace('<span class="count" id="count"></span>', `<span class="count" id="count">${list.length} produtos</span>`)
      .replace('<div class="h-grid" id="grid"></div>', `<div class="h-grid" id="grid">${list.slice(0, 40).map(cardHTML).join('')}</div>`).replace('<body>', '<body class="pg-c modo-lista">');
    res.setHeader('Cache-Control', 's-maxage=300, stale-while-revalidate=3600');
    return res.end(html);
  }
  res.statusCode = 302; res.setHeader('Location', '/'); res.end();
};
