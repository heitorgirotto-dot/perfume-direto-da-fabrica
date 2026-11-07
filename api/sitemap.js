const C = require('./_catalogo');
module.exports = async (req, res) => {
  const items = await C.produtos();
  const marcas = [...new Set(items.map(i => i.b))].sort();
  const urls = ['/', ...Object.keys(C.CATS).map(k => '/c/' + k), ...marcas.map(b => '/c/' + C.slug(b)), ...items.map(i => '/p/' + i.slug)];
  const hoje = new Date().toISOString().slice(0, 10);
  res.setHeader('Content-Type', 'application/xml; charset=utf-8');
  res.setHeader('Cache-Control', 's-maxage=3600, stale-while-revalidate=86400');
  res.end('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' +
    urls.map(u => `<url><loc>${C.BASE}${u}</loc><lastmod>${hoje}</lastmod><changefreq>${u === '/' ? 'daily' : 'weekly'}</changefreq><priority>${u === '/' ? '1.0' : u.startsWith('/c/') ? '0.8' : '0.6'}</priority></url>`).join('\n') + '\n</urlset>');
};
