// Busca fotos para os produtos sem imagem em produtos.json, procurando pelo nome no site de referência
// (thekingofparfums.com.br, loja Nuvemshop) e baixando até 3 imagens por produto para fotos-king/.
// Roda no GitHub Actions (.github/workflows/fotos.yml). Uso local: node ferramentas/buscar-fotos.js
const fs = require('fs');
const path = require('path');
const ROOT = path.join(__dirname, '..');
const LOJA = 'https://www.thekingofparfums.com.br';
const UA = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/124 Safari/537.36';
const norm = s => String(s).normalize('NFD').replace(/[̀-ͯ]/g, '').toLowerCase().replace(/[^a-z0-9]+/g, ' ').trim();
const toks = s => norm(s).split(' ').filter(t => t.length > 1 && !['edp', 'edt', 'ml', 'de', 'da', 'do', 'e', 'for', 'the', 'parfum', 'extrait', 'eau'].includes(t));
const sleep = ms => new Promise(r => setTimeout(r, ms));

async function get(url) {
  const r = await fetch(url, { headers: { 'User-Agent': UA, Accept: 'text/html' }, redirect: 'follow' });
  if (!r.ok) throw new Error(r.status + ' ' + url);
  return r.text();
}
function score(a, b) {
  const A = new Set(toks(a)), B = new Set(toks(b));
  if (!A.size) return 0;
  let hit = 0; A.forEach(t => { if (B.has(t)) hit++; });
  return hit / A.size;
}
async function buscar(it) {
  const q = encodeURIComponent((it.b + ' ' + it.n).replace(/\b\d+\s?ml\b/i, '').trim());
  const html = await get(`${LOJA}/search/?q=${q}`);
  if (process.env.DEBUG) { console.log('DEBUG url:', `${LOJA}/search/?q=${q}`, 'tamanho:', html.length, 'links /produtos/:', (html.match(/\/produtos\//g) || []).length); console.log(html.replace(/\s+/g, ' ').slice(0, 4000)); const i = html.indexOf('/produtos/'); if (i > 0) console.log('TRECHO:', html.slice(Math.max(0, i - 600), i + 400)); }
  // links de produto do resultado + o texto do link para conferir o nome
  const cand = [];
  const re = /<a[^>]+href="([^"]*\/produtos\/[^"]+)"[^>]*>([\s\S]*?)<\/a>/gi;
  let m; while ((m = re.exec(html))) {
    const href = m[1].startsWith('http') ? m[1] : LOJA + m[1];
    const txt = m[2].replace(/<[^>]+>/g, ' ').replace(/\s+/g, ' ').trim();
    const sc = Math.max(score(it.n, txt), score(it.n, decodeURIComponent(href.split('/produtos/')[1] || '').replace(/-/g, ' ')));
    if (sc > 0) cand.push({ href, txt, sc });
  }
  cand.sort((a, b) => b.sc - a.sc);
  const best = cand[0];
  if (!best || best.sc < 0.6) return null;
  const pg = await get(best.href);
  const imgs = [...new Set((pg.match(/https:\/\/acdn[^"' ]*mitiendanube\.com\/stores\/[^"' ]+?-1024-1024\.(?:webp|jpg|jpeg|png)/g) || []))];
  return { url: best.href, nome: best.txt, imgs: imgs.slice(0, 3) };
}
async function baixar(url, dest) {
  const r = await fetch(url, { headers: { 'User-Agent': UA } });
  if (!r.ok) throw new Error('img ' + r.status);
  fs.writeFileSync(dest, Buffer.from(await r.arrayBuffer()));
}
(async () => {
  const PJ = path.join(ROOT, 'produtos.json');
  const items = JSON.parse(fs.readFileSync(PJ, 'utf8'));
  const sem = items.filter(i => !i.pics || !i.pics.length);
  console.log(sem.length, 'produtos sem foto');
  let ok = 0, lista = [];
  fs.mkdirSync(path.join(ROOT, 'fotos-king'), { recursive: true });
  for (const it of (process.env.DEBUG ? sem.slice(0, 1) : sem)) {
    try {
      const r = await buscar(it);
      if (!r || !r.imgs.length) { console.log('  sem resultado:', it.b, it.n); continue; }
      const pics = [];
      for (let k = 0; k < r.imgs.length; k++) {
        const ext = r.imgs[k].split('.').pop().split('?')[0];
        const rel = `fotos-king/${it.id}-${k}.${ext}`;
        await baixar(r.imgs[k], path.join(ROOT, rel));
        pics.push(rel); lista.push(`${rel} ${r.imgs[k]}`);
      }
      it.pics = pics; ok++;
      console.log('  ok:', it.b, it.n, '<-', r.nome, pics.length, 'fotos');
    } catch (e) { console.log('  erro:', it.b, it.n, e.message); }
    await sleep(400);
  }
  if (ok) {
    fs.writeFileSync(PJ, JSON.stringify(items));
    fs.writeFileSync(path.join(ROOT, 'produtos.js'), 'const ITEMS=' + JSON.stringify(items) + ';\n');
    fs.appendFileSync(path.join(ROOT, 'fotos-king-lista.txt'), lista.join('\n') + '\n');
  }
  console.log('concluído:', ok, 'produtos com foto nova');
})();
