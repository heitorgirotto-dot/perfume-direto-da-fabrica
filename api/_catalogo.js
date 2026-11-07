// Regras compartilhadas entre o site (index.html) e as páginas SEO (api/pagina.js).
// Mantenha em sincronia com as constantes do index.html.
const fs = require('fs');
const path = require('path');
const db = require('./_db');

const BASE = 'https://notaperfumaria.com';
const PIX_OFF = 0.10;
const IMPORT = ["Animale","Azzaro","Britney Spears","Burberry","Dolce & Gabbana","Elizabeth Arden","Escada","Hugo Boss","Issey Miyake","Giorgio Armani","Messi","Montblanc","Paco Rabanne","Victoria’s Secret"];
const FAM = {
  doce: /baunilha|caramelo|chocolate|mel\b|tonka|café|algodão|pistache|cereja|tâmara|açúcar|gourmand|frutas vermelhas|framboesa|morango/i,
  amadeirado: /madeira|cedro|sândalo|vetiver|patchouli|oud|bétula|guaiaco/i,
  fresco: /bergamota|limão|toranja|aquátic|marinh|hortelã|mandarina|yuzu|cítric|lavanda|chá|gengibre/i,
  floral: /rosa|jasmim|flor|peônia|tuberosa|orquídea|lírio|íris|violeta|camélia|néroli|ylang/i,
  oriental: /oud|açafrão|âmbar|incenso|canela|pimenta|couro|tabaco|especiaria|cardamomo/i
};
const FAM_L = { doce: ['Doce & envolvente', 'Baunilha, caramelo, frutas', 'Perfumes doces'], amadeirado: ['Amadeirado & marcante', 'Oud, sândalo, cedro', 'Perfumes amadeirados'], fresco: ['Fresco & cítrico', 'Bergamota, limão, aquático', 'Perfumes frescos e cítricos'], floral: ['Floral & delicado', 'Rosa, jasmim, peônia', 'Perfumes florais'], oriental: ['Oriental & intenso', 'Âmbar, especiarias, incenso', 'Perfumes orientais'] };
const OCC = { dia: { t: 'Para o dia', s: 'Leves, frescos e fáceis de usar', f: ['fresco', 'floral'] }, noite: { t: 'Para a noite', s: 'Intensos, marcantes e sensuais', f: ['oriental', 'doce'] }, trabalho: { t: 'Para o trabalho', s: 'Elegantes, discretos e sofisticados', f: ['amadeirado', 'fresco'] }, romantico: { t: 'Encontro romântico', s: 'Doces, quentes e envolventes', f: ['doce', 'floral'] } };
const CATS = { masculinos: { f: 'M', t: 'Perfumes masculinos', s: 'Fragrâncias para ele: amadeirados, frescos e orientais das melhores casas' }, femininos: { f: 'F', t: 'Perfumes femininos', s: 'Fragrâncias para ela: doces, florais e marcantes' }, unissex: { f: 'U', t: 'Perfumes unissex', s: 'Fragrâncias compartilhadas, para quem não se prende a rótulos' }, arabes: { f: 'arabe', t: 'Perfumes árabes', s: 'Lattafa, Armaf, Al Haramain, Rasasi, Afnan e as casas mais desejadas do Oriente Médio' }, importados: { f: 'import', t: 'Importados & grifes', s: 'Grifes internacionais 100% originais' }, kits: { f: 'kit', t: 'Kits e presentes', s: 'Conjuntos prontos para presentear' }, 'body-splash': { f: 'splash', t: 'Body splash & mists', s: 'Leves, refrescantes, para o dia a dia' }, ofertas: { f: 'sale', t: 'Ofertas', s: 'Fragrâncias originais com o melhor preço da curadoria' }, 'mais-desejados': { f: 'best', t: 'Os mais desejados', s: 'As fragrâncias que nossos clientes mais escolhem' }, aromatizadores: { f: 'carro', t: 'Aromatizadores automotivos', s: 'Linhas KING e GIRLS: fragrâncias árabes para o seu carro, R$ 59,90 cada' }, 'aromatizadores-masculinos': { f: 'carro-M', t: 'Aromatizadores KING · masculinos', s: '20 fragrâncias árabes masculinas para pendurar no retrovisor' }, 'aromatizadores-femininos': { f: 'carro-F', t: 'Aromatizadores GIRLS · femininos', s: '20 fragrâncias árabes femininas para pendurar no retrovisor' } };
Object.keys(FAM_L).forEach(k => CATS[k] = { fam: k, t: FAM_L[k][2], s: 'Fragrâncias ' + FAM_L[k][0].toLowerCase().replace(' & ', ' e ') + 's: ' + FAM_L[k][1].toLowerCase() });
Object.keys(OCC).forEach(k => { CATS[k] = { occ: k, t: OCC[k].t, s: OCC[k].s }; [['masculino', 'M', 'masculinos'], ['feminino', 'F', 'femininos']].forEach(([n, g, pl]) => CATS[k + '-' + n] = { occ: k, f: g, t: OCC[k].t + ' · perfumes ' + pl, s: OCC[k].s }); });

const norm0 = s => String(s).normalize('NFD').replace(/[̀-ͯ]/g, '').toLowerCase();
const slug = s => norm0(s).replace(/&/g, ' e ').replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '');
const proprio = it => /^aromatizador/i.test(it.n) || norm0(it.n).startsWith(norm0(it.b));
const pslug = it => slug(proprio(it) ? it.n : it.b + ' ' + it.n);
const nomeCompleto = it => proprio(it) ? it.n : it.b + ' ' + it.n;
const brl = v => 'R$ ' + Number(v).toLocaleString('pt-BR', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
const pix = p => Math.round(p * (1 - PIX_OFF) * 100) / 100;
const esc = s => String(s == null ? '' : s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
const G = { M: 'Masculino', F: 'Feminino', U: 'Unissex' };

function decorate(items) {
  items.forEach((it, i) => {
    if (it.id == null) it.id = i;
    if (it.pics) it.pics = it.pics.map(x => /^(https?:|\/|data:)/.test(x) ? x : '/' + x);
    it.img = it.pics ? it.pics[0] : null;
    it.carro = /^aromatizador/i.test(it.n);
    it.splash = !it.carro && (/body|splash|mist|desodorante|perfume oil/i.test(it.n) || it.b === 'Aroma Luxe');
    it.kit = /kit/i.test(it.n);
    it.imp = IMPORT.includes(it.b);
    it.slug = pslug(it);
    const sc = Object.keys(FAM).map(k => [k, ((it.notes || '').match(new RegExp(FAM[k].source, 'gi')) || []).length]).filter(x => x[1]).sort((a, b) => b[1] - a[1]);
    it.fam = sc.slice(0, 2).map(x => x[0]);
  });
  return items;
}

let cache = { t: 0, items: null };
async function produtos() {
  if (cache.items && Date.now() - cache.t < 60000) return cache.items;
  let items = null;
  try {
    const rows = await db.select('produtos', 'select=id,marca,nome,genero,preco,notas,lembra,descricao,fotos,ativo,mais_vendido,top5&ativo=is.true&order=id.asc&limit=2000');
    if (Array.isArray(rows) && rows.length) items = rows.map(db.toSite);
  } catch (e) { /* cai no arquivo */ }
  const estat = JSON.parse(fs.readFileSync(path.join(process.cwd(), 'produtos.json'), 'utf8'));
  if (!items) items = estat;
  else { const fotos = {}; estat.forEach(i => { if (i.pics) fotos[i.id] = i.pics; }); items.forEach(i => { if (!i.pics && fotos[i.id]) i.pics = fotos[i.id]; }); }
  decorate(items);
  cache = { t: Date.now(), items };
  return items;
}

function filtrar(items, cat) {
  const d = CATS[cat];
  if (d) {
    if (String(d.f).startsWith('carro')) return items.filter(i => i.carro && (d.f === 'carro' || i.g === d.f.slice(6)));
    return items.filter(i => {
      if (i.carro) return false;
      if (d.fam && !i.fam.includes(d.fam)) return false;
      if (d.occ && !OCC[d.occ].f.includes(i.fam[0])) return false;
      switch (d.f) {
        case 'M': case 'F': return i.g === d.f || (!!d.occ && i.g === 'U');
        case 'U': return i.g === d.f;
        case 'arabe': return !i.imp && !i.splash;
        case 'import': return i.imp;
        case 'splash': return i.splash;
        case 'kit': return i.kit;
        case 'sale': return i.p != null && (i.p <= 149 || i.po > i.p);
        case 'best': return !!i.best;
        default: return true;
      }
    });
  }
  const marca = [...new Set(items.map(i => i.b))].find(b => slug(b) === cat);
  return marca ? items.filter(i => i.b === marca) : null;
}

function tituloCat(items, cat) {
  const d = CATS[cat];
  if (d) return { t: d.t, s: d.s };
  const marca = [...new Set(items.map(i => i.b))].find(b => slug(b) === cat);
  return marca ? { t: marca, s: `Todas as fragrâncias ${marca} da nossa curadoria, 100% originais` } : null;
}

module.exports = { BASE, CATS, FAM_L, OCC, G, slug, pslug, nomeCompleto, brl, pix, esc, produtos, filtrar, tituloCat, decorate };
