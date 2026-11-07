// Páginas indexáveis: /p/<produto> e /c/<categoria>. Serve o index.html com título, meta,
// JSON-LD e conteúdo do produto/categoria já renderizado (o JS da página assume depois).
const fs = require('fs');
const path = require('path');
const C = require('./_catalogo');
const { taxas } = require('./_taxas');

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
  const price = it.p == null ? '<div class="pix" style="font-size:1rem">Consultar</div>' : `${off ? `<div class="old">de ${C.brl(it.po)}</div>` : ''}<div class="pix">${C.brl(C.pix(it.p))}<small>no PIX</small></div><div class="full">${C.brl(it.p)} no boleto</div><div class="parc">ou em até 12x no cartão</div>`;
  return `<div class="card"><div class="ph${it.img ? ' has zoom' : ''}" data-open="${it.id}">${it.img ? `<img src="${it.img}" alt="${C.esc(it.b + ' ' + it.n)}" loading="lazy">` : ''}${off ? `<span class="off">${off}% OFF</span>` : ''}<span class="pill ${it.g}">${C.G[it.g]}</span></div>
  <div class="cb"><div class="brand">${C.esc(it.b)}</div><h3><a href="/p/${it.slug}" data-open="${it.id}" style="text-decoration:none">${C.esc(it.n)}</a></h3><p class="notes"><b>Notas:</b> ${C.esc(it.notes || '')}</p>${it.like ? `<p class="like">Lembra: <b>${C.esc(it.like)}</b></p>` : ''}${price}
  <div class="acts"><a class="buy" href="/p/${it.slug}" data-open="${it.id}">Comprar</a></div></div></div>`;
};

module.exports = async (req, res) => {
  const q = req.query || {};
  const tipo = q.tipo, s = String(q.slug || '').toLowerCase().replace(/[^a-z0-9-]/g, '');
  if (tipo === 'taxas') { res.setHeader('Cache-Control', 'public, max-age=300'); return res.json(taxas()); }
  if (tipo === 'sitemap') {
    const items = await C.produtos();
    const marcas = [...new Set(items.map(i => i.b))].sort();
    const urls = ['/', ...Object.keys(C.CATS).map(k => '/c/' + k), ...marcas.map(b => '/c/' + C.slug(b)), ...items.map(i => '/p/' + i.slug)];
    const hoje = new Date().toISOString().slice(0, 10);
    res.setHeader('Content-Type', 'application/xml; charset=utf-8');
    res.setHeader('Cache-Control', 's-maxage=3600, stale-while-revalidate=86400');
    return res.end('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' +
      urls.map(u => `<url><loc>${C.BASE}${u}</loc><lastmod>${hoje}</lastmod><changefreq>${u === '/' ? 'daily' : 'weekly'}</changefreq><priority>${u === '/' ? '1.0' : u.startsWith('/c/') ? '0.8' : '0.6'}</priority></url>`).join('\n') + '\n</urlset>');
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
    const desc = `${nome} ${C.G[it.g].toLowerCase()} 100% original${it.p != null ? ` por ${C.brl(C.pix(it.p))} no PIX ou em até 12x no cartão` : ''}. Notas: ${it.notes || ''}.${it.like ? ' Lembra ' + it.like + '.' : ''} Envio para todo o Brasil.`.slice(0, 300);
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
      <p class="notes"><b>Notas:</b> ${C.esc(it.notes || '')}</p>${it.like ? `<p class="like">Lembra: <b>${C.esc(it.like)}</b></p>` : ''}${it.desc ? `<p class="pv-desc">${C.esc(it.desc)}</p>` : ''}
      ${it.p == null ? '<div class="pix">Consultar</div>' : `${off ? `<div class="old">de ${C.brl(it.po)} · ${off}% OFF</div>` : ''}<div class="pix">${C.brl(C.pix(it.p))}<small>no PIX</small></div><div class="full">${C.brl(it.p)} no boleto · cartão em até 12x</div>`}
      <div class="acts" style="margin-top:18px"><a class="buy" href="/p/${it.slug}" data-open="${it.id}">Comprar</a><a class="ask" href="https://wa.me/5511982659792?text=${encodeURIComponent('Olá! Tenho uma dúvida sobre ' + nome)}" target="_blank" rel="noopener">Falar com especialista</a></div>
      <p class="msg" style="margin-top:14px">100% original e lacrado · PIX, boleto ou cartão em até 12x · Envio pelos Correios com rastreio</p>
    </div>
  </div>
</div></section>`;
    html = html.replace('<a class="cover-wide"', bloco + '\n<a class="cover-wide"').replace('<body>', '<body class="pg-p">');
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
    html = html.replace('<h2 class="gold-text" id="cat-title">A coleção Nota</h2>', `<h1 class="gold-text" id="cat-title">${C.esc(t.t)}</h1>`)
      .replace('<p id="cat-sub">Mais de 350 fragrâncias originais, das casas árabes às grifes internacionais</p>', `<p id="cat-sub">${C.esc(t.s)}</p>`)
      .replace('<p class="cat-crumb" id="cat-crumb" hidden>', '<p class="cat-crumb" id="cat-crumb">')
      .replace('<span id="cat-crumb-n"></span>', `<span id="cat-crumb-n">${C.esc(t.t)}</span>`)
      .replace('<span class="count" id="count"></span>', `<span class="count" id="count">${list.length} produtos</span>`)
      .replace('<div class="grid" id="grid"></div>', `<div class="grid" id="grid">${list.slice(0, 40).map(cardHTML).join('')}</div>`).replace('<body>', '<body class="pg-c">');
    res.setHeader('Cache-Control', 's-maxage=300, stale-while-revalidate=3600');
    return res.end(html);
  }
  res.statusCode = 302; res.setHeader('Location', '/'); res.end();
};
