"""Patch do index.html: promo bar, menu, famílias/ocasiões/FAQ, cards de/por, rotas /p e /c."""
import os, sys, re
REPO = sys.argv[1]
P = os.path.join(REPO, 'index.html')
html = open(P, encoding='utf-8').read()

def rep(old, new, count=1):
    global html
    assert html.count(old) >= 1, 'não achei: ' + old[:80]
    html = html.replace(old, new, count)

# ---------------------------------------------------------------- CSS
CSS = r"""
/* ===== loja v2: promo, menu, famílias, ocasiões, faq, de/por ===== */
.promo{display:block}
.promo .track span{display:inline-flex;gap:48px;align-items:center}
.promo .track i{font-style:normal;opacity:.55}
.nav{position:relative;display:flex;gap:2px;overflow:visible;border-top:1px solid var(--line);font-size:.78rem;font-weight:600;letter-spacing:.1em;text-transform:uppercase}
.nav-scroll{overflow-x:auto;scrollbar-width:none;-webkit-overflow-scrolling:touch}.nav-scroll::-webkit-scrollbar{display:none}
.nav>a,.nav>.dd>button{white-space:nowrap;padding:12px 13px;color:var(--fg);text-decoration:none;background:transparent;border:0;border-bottom:2px solid transparent;letter-spacing:inherit;text-transform:inherit;font-weight:inherit;font-size:inherit;display:inline-flex;align-items:center;gap:6px}
.nav>a:hover,.nav>.dd>button:hover,.nav>a.on,.nav>.dd.on>button{color:var(--gold2);border-bottom-color:var(--gold)}
.nav .hl{color:var(--gold2)}
.nav .dd{position:static}
.nav .dd>button svg{width:12px;height:12px;transition:transform .2s}.nav .dd.open>button svg{transform:rotate(180deg)}
.dd-box{display:none;position:absolute;left:0;right:0;top:100%;background:#0b0a08;border:1px solid var(--line);border-top:1px solid var(--gold3);box-shadow:0 30px 60px rgba(0,0,0,.6);padding:22px 26px;z-index:20;text-transform:none;letter-spacing:0;font-weight:400;font-size:.92rem}
.dd.open .dd-box{display:block}
.dd-box .cols{display:grid;grid-template-columns:repeat(auto-fill,minmax(170px,1fr));gap:4px 24px}
.dd-box a{display:block;padding:6px 0;color:var(--fg);text-decoration:none;border-bottom:1px solid transparent}
.dd-box a:hover{color:var(--gold2)}
.dd-box h5{margin:0 0 8px;font-family:var(--display);font-size:1.25rem;color:var(--gold2);font-weight:600}
.dd-box .grp{break-inside:avoid}
.dd-box .tiles{display:grid;grid-template-columns:repeat(auto-fill,minmax(190px,1fr));gap:12px}
.dd-box .tiles a{border:1px solid var(--line);border-radius:12px;padding:14px 16px;background:var(--card)}
.dd-box .tiles a b{display:block;font-family:var(--display);font-size:1.2rem;color:var(--gold2)}
.dd-box .tiles a small{color:var(--muted)}
@media(max-width:900px){.dd-box{padding:16px}.dd-box .cols{grid-template-columns:1fr 1fr}}
@media(max-width:560px){.dd-box .cols{grid-template-columns:1fr}.nav>a,.nav>.dd>button{padding:11px 10px}}
/* tiles famílias / ocasiões */
.tiles-sec .tl{display:grid;grid-template-columns:repeat(5,1fr);gap:14px}
.tiles-sec .tl.four{grid-template-columns:repeat(4,1fr)}
.tile{position:relative;display:block;border-radius:16px;overflow:hidden;border:1px solid var(--line);background:var(--card);aspect-ratio:4/5;text-decoration:none;color:var(--fg);isolation:isolate}
.tile img{position:absolute;inset:0;width:100%;height:100%;object-fit:cover;opacity:.55;transition:transform .5s,opacity .3s;z-index:-1}
.tile:hover img{transform:scale(1.06);opacity:.7}
.tile::after{content:"";position:absolute;inset:0;background:linear-gradient(180deg,rgba(5,5,5,.05) 30%,rgba(5,5,5,.92));z-index:-1}
.tile .tx{position:absolute;left:0;right:0;bottom:0;padding:18px}
.tile .tx b{display:block;font-family:var(--display);font-size:1.55rem;line-height:1.05;color:var(--gold2)}
.tile .tx span{display:block;color:#cfc6b2;font-size:.86rem;margin-top:4px}
.tile .tx em{display:inline-block;margin-top:10px;font-style:normal;font-size:.72rem;letter-spacing:.14em;text-transform:uppercase;color:var(--gold)}
@media(max-width:1000px){.tiles-sec .tl{grid-template-columns:repeat(3,1fr)}.tiles-sec .tl.four{grid-template-columns:repeat(2,1fr)}}
@media(max-width:600px){.tiles-sec .tl{grid-template-columns:repeat(2,1fr)}.tile{aspect-ratio:4/4.4}.tile .tx{padding:14px}.tile .tx b{font-size:1.25rem}}
/* cards: de/por, badges */
.card .ph .off{position:absolute;left:10px;top:10px;background:var(--sale);color:#fff;font-size:.72rem;font-weight:800;padding:4px 8px;border-radius:6px;letter-spacing:.04em}
.card .ph .fg{position:absolute;left:10px;top:38px;background:#1b3d22;color:#9be3a6;font-size:.68rem;font-weight:700;padding:3px 7px;border-radius:6px;letter-spacing:.04em;text-transform:uppercase}
.card .old{color:var(--muted);font-size:.82rem;text-decoration:line-through;margin-top:6px}
.card .parc{color:#cfc6b2;font-size:.8rem;margin-top:2px}
.pv-info .old{color:var(--muted);text-decoration:line-through;font-size:.95rem;margin-top:8px}
/* cabeçalho de categoria */
.cat-crumb{font-size:.78rem;color:var(--muted);letter-spacing:.08em;text-transform:uppercase;margin-bottom:8px}.cat-crumb a{color:var(--gold);text-decoration:none}
/* página de produto (SSR) */
.ssr-p{border-bottom:1px solid var(--line);padding:26px 0 34px;background:var(--bg2)}
.ssr-g{display:grid;grid-template-columns:minmax(240px,400px) 1fr;gap:34px;align-items:start;margin-top:14px}
.ssr-m{background:#fbf8f2;border-radius:16px;padding:18px}.ssr-m img{width:100%;height:auto;display:block}
.ssr-i h1{font-size:clamp(1.8rem,3vw,2.6rem);margin:6px 0 10px}.ssr-i .brand{color:var(--gold);letter-spacing:.14em;text-transform:uppercase;font-size:.78rem;font-weight:600}
.ssr-i .notes,.ssr-i .like{color:var(--muted);margin-top:10px}.ssr-i .pix{margin-top:16px}
@media(max-width:760px){.ssr-g{grid-template-columns:1fr;gap:18px}}
/* FAQ */
.faq{max-width:900px;margin:0 auto}
.faq details{border-bottom:1px solid var(--line);padding:4px 0}
.faq summary{cursor:pointer;list-style:none;display:flex;justify-content:space-between;align-items:center;gap:16px;padding:16px 0;font-family:var(--display);font-size:1.25rem;font-weight:600;color:#f0e8d6}
.faq summary::-webkit-details-marker{display:none}
.faq summary::after{content:"+";color:var(--gold);font-size:1.5rem;font-weight:300;flex:none;transition:transform .2s}
.faq details[open] summary::after{transform:rotate(45deg)}
.faq details p{color:var(--muted);padding:0 0 18px;max-width:75ch;line-height:1.6}
/* instagram cta */
.insta{border:1px solid var(--line);border-radius:18px;padding:34px;text-align:center;background:radial-gradient(600px 240px at 50% 0,rgba(217,178,90,.12),transparent 70%),var(--card)}
.insta h3{font-size:1.8rem}.insta p{color:var(--muted);margin:8px 0 18px}
"""
rep('</style>\n<style>.pv-desc', CSS + '</style>\n<style>.pv-desc')

# ---------------------------------------------------------------- HEAD: JSON-LD organização
rep('<title>Nota Perfumaria · Alta perfumaria original</title>',
    '<title>Nota Perfumaria · Alta perfumaria original</title>\n'
    '<script type="application/ld+json">{"@context":"https://schema.org","@type":"Store","name":"Nota Perfumaria","url":"https://notaperfumaria.com/","image":"https://notaperfumaria.com/img/logo.jpg","description":"Alta perfumaria árabe e importada, 100% original, com atendimento personalizado.","telephone":"+55 11 98265-9792","priceRange":"R$79 - R$600","areaServed":"BR"}</script>')

# ---------------------------------------------------------------- PROMO BAR + NAV
rep('<header class="top"><div class="wrap">',
    '<div class="promo" id="promo" aria-hidden="true"><div class="track" id="promo-track"></div></div>\n<header class="top"><div class="wrap">')

NAV = '''
  <div class="nav-scroll"><nav class="nav" id="nav" aria-label="Navegação da loja">
    <a href="/" data-cat="all">Início</a>
    <div class="dd"><button type="button" aria-haspopup="true">Perfumes <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4"><path d="M6 9l6 6 6-6"/></svg></button>
      <div class="dd-box"><div class="cols">
        <div class="grp"><h5>Por gênero</h5><a href="/c/masculinos" data-cat="masculinos">Masculinos</a><a href="/c/femininos" data-cat="femininos">Femininos</a><a href="/c/unissex" data-cat="unissex">Unissex</a></div>
        <div class="grp"><h5>Por origem</h5><a href="/c/arabes" data-cat="arabes">Perfumes árabes</a><a href="/c/importados" data-cat="importados">Importados &amp; grifes</a></div>
        <div class="grp"><h5>Formatos</h5><a href="/c/kits" data-cat="kits">Kits e presentes</a><a href="/c/body-splash" data-cat="body-splash">Body splash &amp; mists</a><a href="/c/ofertas" data-cat="ofertas">Ofertas</a></div>
        <div class="grp"><h5>Mais</h5><a href="/c/mais-desejados" data-cat="mais-desejados">Mais desejados</a><a href="#assinatura">Descubra seu perfume</a></div>
      </div></div></div>
    <div class="dd"><button type="button" aria-haspopup="true">Marcas <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4"><path d="M6 9l6 6 6-6"/></svg></button><div class="dd-box"><div class="cols" id="nav-marcas"></div></div></div>
    <a href="/c/masculinos" data-cat="masculinos">Masculinos</a>
    <a href="/c/femininos" data-cat="femininos">Femininos</a>
    <a href="/c/arabes" data-cat="arabes">Árabes</a>
    <div class="dd"><button type="button" aria-haspopup="true">Famílias olfativas <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4"><path d="M6 9l6 6 6-6"/></svg></button><div class="dd-box"><div class="tiles" id="nav-fam"></div></div></div>
    <div class="dd"><button type="button" aria-haspopup="true">Ocasiões <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4"><path d="M6 9l6 6 6-6"/></svg></button><div class="dd-box"><div class="tiles" id="nav-occ"></div></div></div>
    <a href="/c/kits" data-cat="kits">Kits</a>
    <a href="/c/ofertas" data-cat="ofertas" class="hl">Ofertas</a>
    <a href="#assinatura" class="hl">Descubra seu perfume</a>
  </nav></div>
'''
rep('''      </div>
  </div></header>''', '''      </div>
''' + NAV + '''  </div></header>''')

# ---------------------------------------------------------------- SEÇÕES NOVAS
FAM_SEC = '''
<section class="tiles-sec" id="familias"><div class="wrap">
  <div class="sh"><p class="kick" style="text-align:center">Encontre pelo estilo</p><h2 class="gold-text">Conheça as famílias olfativas</h2><p>Cada fragrância pertence a uma família. Descubra a sua e navegue só pelo que combina com você.</p><div class="rule"></div></div>
  <div class="tl" id="fam-tiles"></div>
</div></section>
'''
rep('<section class="bn right" id="bn-autoridade">', FAM_SEC + '<section class="bn right" id="bn-autoridade">')

OCC_SEC = '''
<section class="tiles-sec" id="ocasioes"><div class="wrap">
  <div class="sh"><p class="kick" style="text-align:center">Para cada momento</p><h2 class="gold-text">Explore por ocasião</h2><p>O perfume certo para o dia, a noite, o trabalho ou um encontro especial.</p><div class="rule"></div></div>
  <div class="tl four" id="occ-tiles"></div>
</div></section>
'''
rep('<section class="bn left" id="bn-atendimento">', OCC_SEC + '<section class="bn left" id="bn-atendimento">')
rep('<section><div class="wrap">\n  <div class="sh"><h2 class="gold-text">Ícones da semana</h2>', '<section id="top5-sec"><div class="wrap">\n  <div class="sh"><h2 class="gold-text">Ícones da semana</h2>')

FAQ_SEC = '''
<section id="faq"><div class="wrap">
  <div class="sh"><h2 class="gold-text">Perguntas frequentes</h2><p>O que todo mundo quer saber antes de comprar</p><div class="rule"></div></div>
  <div class="faq">
    <details><summary>Os perfumes são originais?</summary><p>Sim. Trabalhamos somente com frascos originais e lacrados, com selo do importador. Você recebe exatamente o produto que escolheu, sem decants, sem contratipos.</p></details>
    <details><summary>Perfume árabe fixa mesmo?</summary><p>As casas árabes (Lattafa, Armaf, Al Haramain, Rasasi, Afnan e outras) são conhecidas pela alta concentração de essência. A maioria dos EDPs da nossa curadoria entrega de 8 a 12 horas de fixação na pele, com projeção forte nas primeiras horas.</p></details>
    <details><summary>Como escolher o perfume certo sem sentir o cheiro?</summary><p>Use o nosso <a href="#assinatura" style="color:var(--gold)">Descubra sua assinatura olfativa</a> ou fale com um especialista no WhatsApp. Indicamos por notas, estilo, ocasião e clima, e comparamos com perfumes que você já conhece.</p></details>
    <details><summary>Quais são as formas de pagamento?</summary><p>PIX à vista com desconto, boleto à vista ou cartão de crédito em até 12x. O pagamento é feito dentro do site, processado pelo Asaas, com criptografia e antifraude. A loja não armazena os dados do seu cartão.</p></details>
    <details><summary>Qual o prazo de entrega?</summary><p>Postamos em até 2 dias úteis após a confirmação do pagamento, pelos Correios, com código de rastreio enviado pelo WhatsApp. O prazo de entrega é calculado pelo CEP na hora da compra.</p></details>
    <details><summary>Posso trocar ou devolver?</summary><p>Sim. Trocas e devoluções em até 7 dias após o recebimento, para produtos lacrados, conforme o Código de Defesa do Consumidor. É só chamar no WhatsApp.</p></details>
  </div>
</div></section>
<section id="instagram"><div class="wrap">
  <div class="insta"><p class="kick">@notaperfumaria</p><h3 class="gold-text">Lançamentos e bastidores no Instagram</h3><p>Novidades, comparações e indicações toda semana.</p><a class="btn btn-ghost" href="https://instagram.com/notaperfumaria" target="_blank" rel="noopener">Seguir no Instagram</a></div>
</div></section>
'''
rep('<footer><div class="wrap">', FAQ_SEC + '<footer><div class="wrap">')

# cabeçalho de categoria dentro de #colecoes
rep('<div class="sh"><h2 class="gold-text">A coleção Nota</h2><p>Mais de 350 fragrâncias originais, das casas árabes às grifes internacionais</p><div class="rule"></div></div>',
    '<div class="sh"><p class="cat-crumb" id="cat-crumb" hidden><a href="/" data-cat="all">Início</a> › <span id="cat-crumb-n"></span></p><h2 class="gold-text" id="cat-title">A coleção Nota</h2><p id="cat-sub">Mais de 350 fragrâncias originais, das casas árabes às grifes internacionais</p><div class="rule"></div></div>')

# rodapé institucional: links reais
rep('<div><h4>Institucional</h4><ul><li><a href="#colecoes">Catálogo completo</a></li></ul></div>',
    '<div><h4>Institucional</h4><ul><li><a href="/c/masculinos">Perfumes masculinos</a></li><li><a href="/c/femininos">Perfumes femininos</a></li><li><a href="/c/arabes">Perfumes árabes</a></li><li><a href="/c/importados">Importados</a></li><li><a href="/c/kits">Kits e presentes</a></li><li><a href="/c/ofertas">Ofertas</a></li><li><a href="#faq">Perguntas frequentes</a></li></ul></div>')

# ---------------------------------------------------------------- JS: config + catálogo
rep('''const IMPORT= [''', '''const FRETE_GRATIS = 0;   // valor mínimo do pedido para frete grátis (0 = desligado). Ao ativar, ajuste também api/pagar.js.
const IMPORT= [''')

rep('''// ==================
const BYID={};''', '''// ==================
const slug=s=>String(s).normalize('NFD').replace(/[̀-ͯ]/g,'').toLowerCase().replace(/&/g,' e ').replace(/[^a-z0-9]+/g,'-').replace(/^-|-$/g,'');
const pslug=it=>slug(norm0(it.n).startsWith(norm0(it.b))?it.n:it.b+' '+it.n);const norm0=s=>String(s).normalize('NFD').replace(/[̀-ͯ]/g,'').toLowerCase();
const FAM={doce:/baunilha|caramelo|chocolate|mel\\b|tonka|café|algodão|pistache|cereja|tâmara|açúcar|gourmand|frutas vermelhas|framboesa|morango/i,
  amadeirado:/madeira|cedro|sândalo|vetiver|patchouli|oud|bétula|guaiaco/i,
  fresco:/bergamota|limão|toranja|aquátic|marinh|hortelã|mandarina|yuzu|cítric|lavanda|chá|gengibre/i,
  floral:/rosa|jasmim|flor|peônia|tuberosa|orquídea|lírio|íris|violeta|camélia|néroli|ylang/i,
  oriental:/oud|açafrão|âmbar|incenso|canela|pimenta|couro|tabaco|especiaria|cardamomo/i};
const FAM_L={doce:['Doce & envolvente','Baunilha, caramelo, frutas','Perfumes doces'],amadeirado:['Amadeirado & marcante','Oud, sândalo, cedro','Perfumes amadeirados'],fresco:['Fresco & cítrico','Bergamota, limão, aquático','Perfumes frescos e cítricos'],floral:['Floral & delicado','Rosa, jasmim, peônia','Perfumes florais'],oriental:['Oriental & intenso','Âmbar, especiarias, incenso','Perfumes orientais']};
const OCC={dia:{t:'Para o dia',s:'Leves, frescos e fáceis de usar',f:['fresco','floral']},noite:{t:'Para a noite',s:'Intensos, marcantes e sensuais',f:['oriental','doce']},trabalho:{t:'Para o trabalho',s:'Elegantes, discretos e sofisticados',f:['amadeirado','fresco']},romantico:{t:'Encontro romântico',s:'Doces, quentes e envolventes',f:['doce','floral']}};
const CATS={all:{f:'all',t:'A coleção Nota'},masculinos:{f:'M',t:'Perfumes masculinos',s:'Fragrâncias para ele: amadeirados, frescos e orientais das melhores casas'},femininos:{f:'F',t:'Perfumes femininos',s:'Fragrâncias para ela: doces, florais e marcantes'},unissex:{f:'U',t:'Perfumes unissex',s:'Fragrâncias compartilhadas, para quem não se prende a rótulos'},arabes:{f:'arabe',t:'Perfumes árabes',s:'Lattafa, Armaf, Al Haramain, Rasasi, Afnan e as casas mais desejadas do Oriente Médio'},importados:{f:'import',t:'Importados & grifes',s:'Grifes internacionais 100% originais'},kits:{f:'kit',t:'Kits e presentes',s:'Conjuntos prontos para presentear'},'body-splash':{f:'splash',t:'Body splash & mists',s:'Leves, refrescantes, para o dia a dia'},ofertas:{f:'sale',t:'Ofertas',s:'Fragrâncias originais com o melhor preço da curadoria'},'mais-desejados':{f:'best',t:'Os mais desejados',s:'As fragrâncias que nossos clientes mais escolhem'}};
Object.keys(FAM_L).forEach(k=>CATS[k]={fam:k,t:FAM_L[k][2],s:'Fragrâncias '+FAM_L[k][0].toLowerCase().replace(' & ',' e ')+'s: '+FAM_L[k][1].toLowerCase()});
Object.keys(OCC).forEach(k=>CATS[k]={occ:k,t:OCC[k].t,s:OCC[k].s});
const famOf=it=>{const sc=Object.keys(FAM).map(k=>[k,((it.notes||'').match(new RegExp(FAM[k].source,'gi'))||[]).length]).filter(x=>x[1]).sort((a,b)=>b[1]-a[1]);return sc.slice(0,2).map(x=>x[0])};
const BYID={};''')

rep('''it.kit=/kit/i.test(it.n);it.imp=IMPORT.includes(it.b);});}''',
    '''it.kit=/kit/i.test(it.n);it.imp=IMPORT.includes(it.b);it.slug=pslug(it);it.fam=famOf(it);if(it.pics)it.pics=it.pics.map(x=>/^(https?:|\/|data:)/.test(x)?x:'/'+x);it.img=it.pics?it.pics[0]:null;});}''')

# ---------------------------------------------------------------- JS: card com de/por
rep('''function card(it,o={}){
  const price=it.p==null?`<div class="pix" style="font-size:1rem">Consultar</div>`:`<div class="pix">${brl(pix(it.p))}<small>no PIX</small></div><div class="full">${brl(it.p)} no boleto · cartão em até 12x</div>`;
  return `<div class="card"><div class="ph${it.img?" has zoom":""}" data-open="${it.id}" title="${it.img?"Ver produto":""}">${it.img?`<img src="${it.img}" alt="${it.n}" loading="lazy">`:bottle}${o.rank?`<span class="rank">${o.rank}</span>`:''}<span class="pill ${it.g}">${G[it.g]}</span></div>''',
    '''const offPct=it=>it.p!=null&&it.po>it.p?Math.round((1-it.p/it.po)*100):0;
function card(it,o={}){
  const off=offPct(it),fg=FRETE_GRATIS>0&&it.p>=FRETE_GRATIS;
  const price=it.p==null?`<div class="pix" style="font-size:1rem">Consultar</div>`:`${off?`<div class="old">de ${brl(it.po)}</div>`:''}<div class="pix">${brl(pix(it.p))}<small>no PIX</small></div><div class="full">${brl(it.p)} no boleto</div><div class="parc">ou em até 12x no cartão</div>`;
  return `<div class="card"><div class="ph${it.img?" has zoom":""}" data-open="${it.id}" title="${it.img?"Ver produto":""}">${it.img?`<img src="${it.img}" alt="${it.b} ${it.n}" loading="lazy">`:bottle}${off?`<span class="off">${off}% OFF</span>`:''}${fg?`<span class="fg">Frete grátis</span>`:''}${o.rank?`<span class="rank">${o.rank}</span>`:''}<span class="pill ${it.g}">${G[it.g]}</span></div>''')
rep('''<div class="acts"><a class="buy" href="#p-${it.id}" data-open="${it.id}">Comprar</a>''',
    '''<div class="acts"><a class="buy" href="/p/${it.slug}" data-open="${it.id}">Comprar</a>''')
rep('''<div class="cb"><div class="brand">${it.b}</div><h3>${it.n}</h3>''',
    '''<div class="cb"><div class="brand">${it.b}</div><h3><a href="/p/${it.slug}" data-open="${it.id}" style="text-decoration:none">${it.n}</a></h3>''')

# modal: de/por
rep('''$('#pv-price').innerHTML=it.p==null?'<div class="pix">Consultar</div>':`<div class="pix">${brl(pix(unit))}<small>no PIX (unid.)</small></div>''',
    '''$('#pv-price').innerHTML=it.p==null?'<div class="pix">Consultar</div>':`${offPct(it)?`<div class="old">de ${brl(it.po)} · ${offPct(it)}% OFF</div>`:''}<div class="pix">${brl(pix(unit))}<small>no PIX (unid.)</small></div>''')

# ---------------------------------------------------------------- JS: renderFixos -> marcas no menu, tiles
rep('''  const sel=$('#brand'),cur=sel.value;sel.innerHTML='<option value="">Todas as marcas</option>'+[...new Set(ITEMS.map(i=>i.b))].sort().map(b=>`<option>${b}</option>`).join('');sel.value=cur;
}''', '''  const marcas=[...new Set(ITEMS.map(i=>i.b))].sort((a,b)=>a.localeCompare(b));
  const sel=$('#brand'),cur=sel.value;sel.innerHTML='<option value="">Todas as marcas</option>'+marcas.map(b=>`<option>${b}</option>`).join('');sel.value=cur;
  $('#nav-marcas').innerHTML=marcas.map(b=>`<a href="/c/${slug(b)}" data-cat="${slug(b)}">${b} <small style="color:var(--muted)">(${ITEMS.filter(i=>i.b===b).length})</small></a>`).join('');
  const TILE_PIC={doce:'Yara Tous EDP 100ml',amadeirado:'Lattafa|Asad EDP 100ml',fresco:'Hawas Ice EDP 100ml',floral:'Yara Elixir EDP 100ml',oriental:'Teriaq EDP 100ml',dia:'Hawas For Him 100ml',noite:'9 PM Elixir Black Gold Parfum 100ml',trabalho:'Club De Nuit Intense Man EDT 105ml',romantico:'Yara Tous EDP 100ml'};
  const pic=(pred,k)=>{const pref=TILE_PIC[k]&&byName(TILE_PIC[k]);if(pref&&pref.img)return pref.img;const x=ITEMS.filter(i=>i.img&&pred(i));return x.length?x[Math.floor(x.length/3)].img:''};
  $('#fam-tiles').innerHTML=Object.keys(FAM_L).map(k=>`<a class="tile" href="/c/${k}" data-cat="${k}"><img src="${pic(i=>i.fam.includes(k),k)}" alt="" loading="lazy"><div class="tx"><b>${FAM_L[k][0]}</b><span>${FAM_L[k][1]}</span><em>Ver fragrâncias ›</em></div></a>`).join('');
  $('#nav-fam').innerHTML=Object.keys(FAM_L).map(k=>`<a href="/c/${k}" data-cat="${k}"><b>${FAM_L[k][0]}</b><small>${FAM_L[k][1]}</small></a>`).join('');
  $('#occ-tiles').innerHTML=Object.keys(OCC).map(k=>`<a class="tile" href="/c/${k}" data-cat="${k}"><img src="${pic(i=>OCC[k].f.includes(i.fam[0]),k)}" alt="" loading="lazy"><div class="tx"><b>${OCC[k].t}</b><span>${OCC[k].s}</span><em>Ver seleção ›</em></div></a>`).join('');
  $('#nav-occ').innerHTML=Object.keys(OCC).map(k=>`<a href="/c/${k}" data-cat="${k}"><b>${OCC[k].t}</b><small>${OCC[k].s}</small></a>`).join('');
}''')

# ---------------------------------------------------------------- JS: filtros com família/ocasião/categoria
rep('''let f='all',page=1;const PAGE=40;''', '''let f='all',page=1,FAMF='',OCCF='',CAT='all';const PAGE=40;''')
rep('''case'sale':return i.p!=null&&i.p<=149;default:return true}}''',
    '''case'sale':return i.p!=null&&(i.p<=149||i.po>i.p);case'best':return!!i.best||BEST.map(byName).includes(i);default:return true}}
function passFam(i){if(FAMF&&!i.fam.includes(FAMF))return false;if(OCCF&&!OCC[OCCF].f.includes(i.fam[0]))return false;return true}''')
rep('''let out=ITEMS.filter(i=>passF(i)&&(!b||i.b===b)&&(!q||norm(i.n+' '+i.b).includes(q)));''',
    '''let out=ITEMS.filter(i=>passF(i)&&passFam(i)&&(!b||i.b===b)&&(!q||norm(i.n+' '+i.b).includes(q)));''')
rep('''function setF(v,scroll){f=v;render(true);if(scroll)$('#colecoes').scrollIntoView({behavior:'smooth'})}''',
    '''function setF(v,scroll){f=v;FAMF='';OCCF='';CAT=Object.keys(CATS).find(k=>CATS[k].f===v)||'all';catHead();render(true);if(scroll)$('#colecoes').scrollIntoView({behavior:'smooth'})}
function catHead(){const c=CATS[CAT]||{};const brandCat=!c.t&&CAT!=='all';const title=brandCat?($('#brand').value||'Marca'):(c.t||'A coleção Nota');
  $('#cat-title').textContent=title;$('#cat-sub').textContent=brandCat?`Todas as fragrâncias ${$('#brand').value} da nossa curadoria, 100% originais`:(c.s||'Mais de 350 fragrâncias originais, das casas árabes às grifes internacionais');
  $('#cat-crumb').hidden=CAT==='all';$('#cat-crumb-n').textContent=title;
  document.querySelectorAll('#nav [data-cat]').forEach(a=>a.classList.toggle('on',a.dataset.cat===CAT));
  if(CAT!=='all')document.title=`${title} · Nota Perfumaria`;else document.title='Nota Perfumaria · Alta perfumaria original';}
function setCat(c,push,scroll){c=c||'all';const d=CATS[c];const marca=!d&&[...new Set(ITEMS.map(i=>i.b))].find(b=>slug(b)===c);if(!d&&!marca)c='all';
  CAT=c;f=d?(d.f||'all'):'all';FAMF=d?(d.fam||''):'';OCCF=d?(d.occ||''):'';$('#brand').value=marca||'';
  if(push)history.pushState(null,'',c==='all'?'/':'/c/'+c);catHead();render(true);
  if(scroll!==false)$('#colecoes').scrollIntoView({behavior:'smooth'});track('busca',null,{pagina:'cat:'+c})}''')

# cliques: categorias do menu/tiles + dropdowns
rep('''document.addEventListener('click',e=>{
  const t=e.target;
  const z=t.closest('[data-open]');if(z){e.preventDefault();openPV(+z.dataset.open);return}''',
    '''document.addEventListener('click',e=>{
  const t=e.target;
  const dd=t.closest('.dd>button');if(dd){const d=dd.parentNode;const was=d.classList.contains('open');document.querySelectorAll('.dd.open').forEach(x=>x.classList.remove('open'));if(!was)d.classList.add('open');return}
  if(!t.closest('.dd'))document.querySelectorAll('.dd.open').forEach(x=>x.classList.remove('open'));
  const z=t.closest('[data-open]');if(z){e.preventDefault();openPV(+z.dataset.open);return}
  const cat=t.closest('a[data-cat]');if(cat){e.preventDefault();document.querySelectorAll('.dd.open').forEach(x=>x.classList.remove('open'));setCat(cat.dataset.cat,true);return}''')

# ---------------------------------------------------------------- JS: rotas /p/slug e /c/slug + URL do modal
rep('''  renderPV();$('#pv').hidden=false;document.body.style.overflow='hidden';location.hash='p-'+id;}
function closePV(){$('#pv').hidden=true;document.body.style.overflow='';if(location.hash.startsWith('#p-'))history.replaceState(null,'',' ');}''',
    '''  renderPV();$('#pv').hidden=false;document.body.style.overflow='hidden';
  if(!PV_ROTA){PV_ROTA=location.pathname+location.search;history.pushState({pv:1},'','/p/'+it.slug)}else history.replaceState({pv:1},'','/p/'+it.slug);
  document.title=`${norm0(it.n).startsWith(norm0(it.b))?it.n:it.b+' '+it.n} · Nota Perfumaria`;}
let PV_ROTA=null;
function closePV(){if($('#pv').hidden)return;$('#pv').hidden=true;document.body.style.overflow='';
  if(location.pathname.startsWith('/p/')&&!$('#ssr-produto')){history.replaceState(null,'',PV_ROTA&&!PV_ROTA.startsWith('/p/')?PV_ROTA:'/')}PV_ROTA=null;if(!$('#ssr-produto'))catHead();}
window.addEventListener('popstate',()=>{if(location.pathname.startsWith('/p/')){const it=ITEMS.find(i=>i.slug===location.pathname.slice(3));if(it){PV_ROTA=PV_ROTA||'/';openPV(it.id)}}else{if(!$('#pv').hidden){$('#pv').hidden=true;document.body.style.overflow='';PV_ROTA=null}if(location.pathname.startsWith('/c/'))setCat(location.pathname.slice(3),false,false);else setCat('all',false,false)}});
function rota(){const p=location.pathname;
  if(p.startsWith('/p/')){const it=ITEMS.find(i=>i.slug===p.slice(3));if(it){if($('#ssr-produto')){PV_ROTA=p;return true}PV_ROTA='/';openPV(it.id);return true}}
  if(p.startsWith('/c/')){setCat(p.slice(3),false,false);if(!document.body.classList.contains('pg-c'))setTimeout(()=>$('#colecoes').scrollIntoView(),50);return true}
  const m=location.hash.match(/^#p-(\\d+)$/);if(m){openPV(+m[1]);return true}return false}''')
rep('''window.addEventListener('hashchange',()=>{const m=location.hash.match(/^#p-(\\d+)$/);if(m)openPV(+m[1])});''', '''''')
rep('''render(true);{const m=location.hash.match(/^#p-(\\d+)$/);if(m)openPV(+m[1]);}
</script>''', '''render(true);rota();
</script>''')
# quando o catálogo do admin chega, reabre pelo slug também
rep('''  const m=location.hash.match(/^#p-(\\d+)$/);if(m&&!$('#pv').hidden)openPV(+m[1]);
}).catch(()=>{});''', '''  catHead();if(location.pathname.startsWith('/p/')&&!$('#pv').hidden){const it=ITEMS.find(i=>i.slug===location.pathname.slice(3));if(it)openPV(it.id)}
}).catch(()=>{});''')
# o quiz tinha a própria FAM: remover a duplicata
rep('''/* ---------- descubra sua assinatura olfativa ---------- */
const FAM={doce:''', '''/* ---------- descubra sua assinatura olfativa ---------- */
const _FAM_quiz={doce:''')

# promo bar
rep('''// promo marquee
''', '''// promo marquee
{const items=(FRETE_GRATIS>0?[`Frete grátis acima de ${brl(FRETE_GRATIS)}`]:[]).concat(PROMO);const s='<span>'+items.map(t=>`${t}<i>◆</i>`).join('')+'</span>';$('#promo-track').innerHTML=s+s;}
''')

html = html.replace('src="img/', 'src="/img/')
open(P, 'w', encoding='utf-8').write(html)
print('ok', len(html.encode()) // 1024, 'KB')
