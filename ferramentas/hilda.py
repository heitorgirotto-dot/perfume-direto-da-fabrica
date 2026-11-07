"""Home da Nota no padrão Hilda Atacado (plataforma Webstore). Mantém carrinho, checkout, conta, leads.
Uso: python3 hilda.py <repo>   (parte do index.html anterior ao layout LAB 8: /tmp/index.pre-lab8.html)"""
import os, re, sys
REPO = sys.argv[1]
P = os.path.join(REPO, 'index.html')
html = open(P, encoding='utf-8').read()

def grab(pat):
    m = re.search(pat, html, re.S)
    assert m, 'não achei: ' + pat[:60]
    return m.group(0)

head = html[:html.index('<body>')]
script_main = grab(r'<script src="/produtos\.js[^"]*"></script>\n<script>\n// ===== CONFIG =====.*?</script>')
pv_modal = grab(r'<div class="pv" id="pv" hidden>.*?</div></div></div>\n')
pol_block = re.search(r'<section id="politicas" class="pol"><div class="wrap">.*?<div class="faq">\n(.*?)  </div>\n</div></section>', html, re.S).group(1)
quiz_inner = re.search(r'<section id="assinatura" class="quiz"><div class="wrap">\n(.*?)</div></section>', html, re.S).group(1)

head = head.replace('family=Cormorant+Garamond', 'family=Poppins:wght@300;400;500;600;700&family=Cormorant+Garamond', 1)

I = {
 'user': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7"><circle cx="12" cy="12" r="9.5"/><circle cx="12" cy="10" r="3.2"/><path d="M6.2 18.4c1.4-2.2 3.4-3.3 5.8-3.3s4.4 1.1 5.8 3.3"/></svg>',
 'cart': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><path d="M3 4h2.2l2.2 11h10.4l2-8H6.3"/><circle cx="9" cy="19.5" r="1.4"/><circle cx="17" cy="19.5" r="1.4"/></svg>',
 'search': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><circle cx="10.5" cy="10.5" r="6.5"/><path d="M15.5 15.5 21 21"/></svg>',
 'down': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M6 9l6 6 6-6"/></svg>',
 'left': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4"><path d="M15 5l-7 7 7 7"/></svg>',
 'right': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4"><path d="M9 5l7 7-7 7"/></svg>',
 'menu': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><path d="M3 6h18M3 12h18M3 18h18"/></svg>',
 'wa': '<svg viewBox="0 0 24 24" fill="currentColor"><path d="M12 2a10 10 0 0 0-8.6 15.1L2 22l5-1.3A10 10 0 1 0 12 2zm0 18.2a8.2 8.2 0 0 1-4.2-1.2l-.3-.2-3 .8.8-2.9-.2-.3A8.2 8.2 0 1 1 12 20.2zm4.5-6.1c-.2-.1-1.5-.7-1.7-.8s-.4-.1-.6.1-.7.8-.8 1-.3.2-.5.1a6.7 6.7 0 0 1-3.3-2.9c-.3-.4.3-.4.8-1.4.1-.2 0-.3 0-.4l-.8-1.8c-.2-.5-.4-.4-.6-.4h-.5a1 1 0 0 0-.7.3 3 3 0 0 0-.9 2.2 5.2 5.2 0 0 0 1.1 2.7 11.8 11.8 0 0 0 4.5 4c1.7.7 2.3.8 3.2.6a2.7 2.7 0 0 0 1.8-1.3 2.2 2.2 0 0 0 .2-1.3c-.1-.1-.2-.2-.5-.3z"/></svg>',
 'money': '<svg viewBox="0 0 24 24" fill="currentColor"><rect x="2" y="5" width="20" height="14" rx="2"/><path d="M6 9h4v2H6zM6 13h2v2H6zM13 9h5v1.6h-5zM13 12h5v1.6h-5z" fill="#fff"/></svg>',
 'truck': '<svg viewBox="0 0 24 24" fill="currentColor"><path d="M1 5h13v10H1zM14 8h4.5l3.5 4v3h-8z"/><circle cx="5.5" cy="17.5" r="2.2"/><circle cx="17.5" cy="17.5" r="2.2"/><circle cx="5.5" cy="17.5" r="1" fill="#fff"/><circle cx="17.5" cy="17.5" r="1" fill="#fff"/></svg>',
 'lock': '<svg viewBox="0 0 24 24" fill="currentColor"><rect x="4" y="10" width="16" height="12" rx="2"/><path d="M7.5 10V7a4.5 4.5 0 0 1 9 0v3" fill="none" stroke="currentColor" stroke-width="2.2"/></svg>',
 'insta': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><rect x="3" y="3" width="18" height="18" rx="5"/><circle cx="12" cy="12" r="4"/><circle cx="17.5" cy="6.5" r="1" fill="currentColor"/></svg>',
 'mail': '<svg viewBox="0 0 24 24" fill="currentColor"><path d="M2 5h20v14H2z"/><path d="M2 5l10 8 10-8" fill="none" stroke="#000" stroke-width="1.6"/></svg>',
 'phone': '<svg viewBox="0 0 24 24" fill="currentColor"><path d="M6.6 10.8a15 15 0 0 0 6.6 6.6l2.2-2.2c.3-.3.7-.4 1-.2 1.1.4 2.3.6 3.6.6.6 0 1 .4 1 1V20c0 .6-.4 1-1 1A17 17 0 0 1 3 4c0-.6.4-1 1-1h3.5c.6 0 1 .4 1 1 0 1.3.2 2.5.6 3.6.1.3 0 .7-.2 1z"/></svg>',
}

BODY = f'''<body>
<header class="h-head" id="topo">
  <div class="h-top"><div class="h-w h-top-in">
    <button class="h-burger" type="button" id="burger" aria-label="Menu">{I['menu']}</button>
    <a class="h-logo" href="/" data-cat="all" aria-label="Nota Perfumaria"><img src="/img/logo-branco.jpg?v=1" alt="Nota Perfumaria" width="900" height="352"></a>
    <form class="h-search" id="sform" role="search"><span class="h-s-ic">{I['search']}</span><input id="q" type="search" placeholder="Busque seu perfume, marca ou nota" aria-label="Buscar"><button type="submit" aria-label="Buscar">{I['search']}</button></form>
    <div class="h-acts">
      <button class="h-acc" id="acc-btn" type="button">{I['user']}<span id="acc-lbl">Minha conta</span>{I['down']}</button>
      <a class="h-ic h-wa-top" href="https://wa.me/5511982659792" target="_blank" rel="noopener" aria-label="WhatsApp">{I['wa']}</a>
      <button class="h-ic h-cart" id="cart-btn" type="button" aria-label="Carrinho">{I['cart']}<span class="h-cq" id="cart-q">0</span><span id="cart-v" class="sr">R$ 0,00</span></button>
    </div>
  </div></div>
  <nav class="h-nav" id="nav" aria-label="Menu da loja"><ul class="h-w">
    <li><a href="/c/ofertas" data-cat="ofertas">OFERTAS</a></li>
    <li class="h-dd"><a href="/c/mais-desejados" data-cat="mais-desejados">PERFUMES</a><div class="h-dd-box"><div class="h-w h-dd-cols">
      <div><b>Gênero</b><a href="/c/masculinos" data-cat="masculinos">Masculinos</a><a href="/c/femininos" data-cat="femininos">Femininos</a><a href="/c/unissex" data-cat="unissex">Unissex</a></div>
      <div><b>Famílias olfativas</b><a href="/c/fresco" data-cat="fresco">Cítricos e frescos</a><a href="/c/amadeirado" data-cat="amadeirado">Amadeirados</a><a href="/c/doce" data-cat="doce">Doces</a><a href="/c/floral" data-cat="floral">Florais</a><a href="/c/oriental" data-cat="oriental">Orientais</a></div>
      <div><b>Ocasiões</b><a href="/c/dia" data-cat="dia">Dia</a><a href="/c/noite" data-cat="noite">Noite</a><a href="/c/trabalho" data-cat="trabalho">Trabalho</a><a href="/c/romantico" data-cat="romantico">Encontros românticos</a></div>
      <div><b>Ajuda para escolher</b><a href="#assinatura" data-modo="quiz">Descubra o seu perfume</a><a href="/c/mais-desejados" data-cat="mais-desejados">Mais desejados</a></div>
    </div></div></li>
    <li><a href="/c/arabes" data-cat="arabes">PERFUMES ÁRABES</a></li>
    <li><a href="/c/importados" data-cat="importados">IMPORTADOS</a></li>
    <li class="h-dd"><a href="#marcas" data-jump="marcas">MARCAS</a><div class="h-dd-box"><div class="h-w h-dd-marcas" id="nav-marcas"></div></div></li>
    <li><a href="/c/kits" data-cat="kits">KITS</a></li>
    <li><a href="/c/body-splash" data-cat="body-splash">BODY SPLASH</a></li>
    <li><a href="/" data-jump="colecoes">MOSTRAR TODOS</a></li>
  </ul></nav>
</header>

<main id="home">
<div class="h-home">
<section class="h-banner"><div class="h-w">
  <div class="h-slides" id="slides">
    <a class="h-slide on" href="/c/arabes" data-cat="arabes" style="background-image:url(/img/capa.jpg)">
      <div class="h-slide-tx"><p>ALTA PERFUMARIA ORIGINAL</p><h2>Fragrâncias que<br><em>marcam presença</em></h2><b>CONFIRA!</b></div></a>
    <a class="h-slide h-slide2" href="/c/ofertas" data-cat="ofertas">
      <div class="h-slide-tx"><p>OFERTAS DA SEMANA</p><h2>Perfumes árabes a partir de <em>R$ 71</em></h2><b>CONFIRA!</b></div><img src="/img/hero.jpg" alt="" loading="lazy"></a>
  </div>
  <button class="h-arr h-arr-l" type="button" data-slide="-1" aria-label="Anterior">{I['left']}</button>
  <button class="h-arr h-arr-r" type="button" data-slide="1" aria-label="Próximo">{I['right']}</button>
</div></section>

<section class="h-conds"><div class="h-w h-conds-in">
  <a href="https://wa.me/5511982659792" target="_blank" rel="noopener">{I['wa']}<b>Dúvidas ?</b><span>Chame nosso time no Whats</span></a>
  <a href="#" data-pol="pagamento">{I['money']}<b>Em até 12x no cartão</b><span>ou 10% de desconto no PIX</span></a>
  <a href="#" data-pol="prazos">{I['truck']}<b>Entrega para todo o Brasil</b><span>Veja as condições</span></a>
  <a href="#" data-pol="originalidade">{I['lock']}<b>100% originais</b><span>Compre com segurança</span></a>
</div></section>

<section class="h-list"><div class="h-w">
  <h2 class="h-title">Os mais desejados da Nota</h2>
  <div class="h-car"><button class="h-car-btn l" type="button" data-car="-1" aria-label="Anterior">{I['left']}</button>
    <div class="h-track" id="best"></div>
    <button class="h-car-btn r" type="button" data-car="1" aria-label="Próximo">{I['right']}</button></div>
</div></section>

<section class="h-full"><a href="/c/arabes" data-cat="arabes"><span>PERFUMES</span><em>Originais e lacrados, das casas mais desejadas</em></a></section>
</div>

<section class="h-list h-colecoes" id="colecoes"><div class="h-w">
  <p class="h-crumb" id="cat-crumb"><a href="/" data-cat="all">Início</a> › <span id="cat-crumb-n">Todos os perfumes</span></p>
  <h2 class="h-title"><span id="cat-title">Todos os perfumes</span></h2>
  <p class="h-sub" id="cat-sub">Mais de 350 fragrâncias originais, das casas árabes às grifes internacionais</p>
  <div class="h-bar">
    <div class="h-chips" id="tabs"><button class="tab on" data-f="all">Todos</button><button class="tab" data-f="M">Masculinos</button><button class="tab" data-f="F">Femininos</button><button class="tab" data-f="U">Unissex</button><button class="tab" data-f="arabe">Árabes</button><button class="tab" data-f="import">Importados</button><button class="tab" data-f="splash">Body splash</button><button class="tab" data-f="kit">Kits</button></div>
    <div class="h-filt"><select id="brand" aria-label="Marca"><option value="">Todas as marcas</option></select><select id="range" aria-label="Faixa de preço"><option value="">Qualquer preço</option><option value="0-100">Até R$ 99</option><option value="100-200">R$ 100 a 199</option><option value="200-9999">Acima de R$ 200</option></select><select id="sort" aria-label="Ordenar"><option value="brand">Ordenar: destaques</option><option value="asc">Menor preço</option><option value="desc">Maior preço</option><option value="az">A–Z</option></select><span class="count" id="count"></span></div>
  </div>
  <div class="h-grid" id="grid"></div>
  <div class="h-more" id="more"></div>
</div></section>

<section class="h-brands h-home" id="marcas"><div class="h-w">
  <h2 class="h-title">Filtre os produtos por fabricantes</h2>
  <p class="h-sub">Trabalhamos com as casas mais desejadas da perfumaria árabe e internacional</p>
  <div class="h-car"><button class="h-car-btn l" type="button" data-car="-1" aria-label="Anterior">{I['left']}</button>
    <div class="h-track h-brand-track" id="brands"></div>
    <button class="h-car-btn r" type="button" data-car="1" aria-label="Próximo">{I['right']}</button></div>
</div></section>
</main>

<section class="h-quiz" id="assinatura"><div class="h-w">
{quiz_inner}</div></section>

<div id="politicas" hidden>
{pol_block}</div>

<section class="h-news"><div class="h-w h-news-in">
  <div><h3>Fique por dentro de nossas novidades</h3><p>Cadastre-se agora mesmo e receba nossas promoções, lançamentos e indicações.</p></div>
  <form class="h-news-f" id="nform"><input id="nnome" type="text" placeholder="Seu nome" autocomplete="name"><input id="nemail" type="email" placeholder="Seu e-mail" autocomplete="email"><button type="submit">Cadastrar</button><p id="nmsg"></p></form>
</div></section>

<footer class="h-foot"><div class="h-w">
  <div class="h-foot-top">
    <div><h4>Sobre nós</h4><p>Nota Perfumaria: alta perfumaria árabe e importada, só frascos originais e lacrados. Perfumes Lattafa, Armaf, Al Haramain, Afnan, Rasasi, Maison Alhambra, Al Wataniah e grandes grifes internacionais, com atendimento humano do primeiro contato ao pós-venda.</p></div>
    <div><h4>Dados de contato</h4><p class="h-foot-ic">{I['wa']} <span id="f-wa">(11) 98265-9792</span></p><p class="h-foot-ic">{I['insta']} @notaperfumaria</p><a href="https://wa.me/5511982659792" target="_blank" rel="noopener">Fale conosco</a><p class="h-foot-small">Segunda a sábado, das 9h às 18h</p></div>
    <div><h4>Institucional</h4><a href="#" data-pol="originalidade">Como saber se o perfume é original</a><a href="#" data-pol="pagamento">Pagamentos e preços</a><a href="#" data-pol="prazos">Política de entrega</a><a href="#" data-pol="rastreio">Rastreie o seu pedido</a><a href="#" data-pol="trocas">Trocas ou devoluções</a><a href="#" data-pol="privacidade">Sobre LGPD</a><a href="#assinatura" data-modo="quiz">Descubra o seu perfume</a></div>
    <div><h4>Redes sociais</h4><div class="h-soc"><a href="https://instagram.com/notaperfumaria" target="_blank" rel="noopener" aria-label="Instagram">{I['insta']}</a><a href="https://wa.me/5511982659792" target="_blank" rel="noopener" aria-label="WhatsApp">{I['wa']}</a></div></div>
  </div>
  <div class="h-foot-bot">
    <div><h4>Formas de pagamento</h4><div class="h-pays"><span class="pix">PIX</span><span class="visa">VISA</span><span class="mc"><i></i><i></i></span><span class="elo">elo</span><span>AMEX</span><span>Boleto</span></div></div>
    <div><h4>Selos</h4><div class="h-seals"><span>{I['lock']} Site seguro SSL</span><span>Pagamento via Asaas</span><span>100% originais</span></div></div>
  </div>
</div>
<div class="h-copy"><div class="h-w">© 2026 Nota Perfumaria. Todos os direitos reservados. Preços sujeitos a alteração; vale o valor exibido na confirmação do pedido.</div></div>
</footer>

{pv_modal}<div class="fab"><a id="fab-wa" href="https://wa.me/5511982659792" target="_blank" rel="noopener" aria-label="WhatsApp">{I['wa']}</a></div>

{script_main}
<script>
(function(){{
  const $=s=>document.querySelector(s),$$=s=>[...document.querySelectorAll(s)];
  let si=0;const sl=$$('#slides .h-slide');function go(n){{si=(n+sl.length)%sl.length;sl.forEach((e,k)=>e.classList.toggle('on',k===si))}}
  let T=setInterval(()=>go(si+1),6000);
  $$('[data-slide]').forEach(b=>b.onclick=e=>{{e.preventDefault();go(si+ +b.dataset.slide);clearInterval(T);T=setInterval(()=>go(si+1),6000)}});
  document.addEventListener('click',e=>{{const b=e.target.closest('[data-car]');if(b){{const tr=b.parentNode.querySelector('.h-track');if(tr)tr.scrollBy({{left:(+b.dataset.car)*tr.clientWidth*.75,behavior:'smooth'}})}}}});
  $('#burger').onclick=()=>document.body.classList.toggle('nav-open');
  document.addEventListener('click',e=>{{const j=e.target.closest('[data-jump]');if(j){{e.preventDefault();e.stopPropagation();document.body.classList.remove('nav-open');if(j.dataset.jump==='colecoes'){{setCat('all',true,false)}}window.setModo('home');const t=document.getElementById(j.dataset.jump);if(t)setTimeout(()=>t.scrollIntoView({{behavior:'smooth'}}),40);return}}
    const m=e.target.closest('[data-modo]');if(m){{e.preventDefault();e.stopPropagation();document.body.classList.remove('nav-open');window.setModo(m.dataset.modo);scrollTo({{top:0,behavior:'smooth'}})}}
    if(e.target.closest('#nav a[data-cat]'))document.body.classList.remove('nav-open');}},true);
}})();
</script>
</body>
</html>
'''

CSS = r"""
/* =================== padrão Hilda Atacado =================== */
:root{--hf:'Poppins',Arial,sans-serif;--h-ac:#b8923a;--h-red:#ed1d1d;--h-txt:#444}
html{scroll-behavior:smooth}
body{font-family:var(--hf)!important;background:#fff!important;color:#444!important;font-size:14px}
body::before{display:none}
h1,h2,h3,h4,h5,h6{font-family:var(--hf)!important}
section{padding-block:0}
.sr{position:absolute;width:1px;height:1px;overflow:hidden;clip:rect(0 0 0 0)}
.h-w{max-width:1200px;margin:0 auto;padding:0 16px;box-sizing:content-box}
@media(max-width:1232px){.h-w{max-width:none}}
/* header */
.h-head{position:sticky;top:0;z-index:30;background:#fff}
.h-top{background:#fff;box-shadow:0 0 10px rgba(0,0,0,.2);position:relative;z-index:2}
.h-top-in{display:flex;align-items:center;gap:24px;height:70px}
.h-logo img{height:50px;width:auto;display:block}
.h-search{position:relative;margin:0 auto;width:387px;max-width:100%}
.h-search input{width:100%;height:44px;border:0;border-radius:10px;background:#f1f1f1;padding:10px 46px 10px 40px;font:inherit;font-size:13px;color:#000;box-sizing:border-box;outline:0}
.h-search input::placeholder{color:#9a9a9a}
.h-s-ic{position:absolute;left:13px;top:12px;color:#9a9a9a}.h-s-ic svg{width:18px;height:18px}
.h-search button{position:absolute;right:6px;top:6px;width:32px;height:32px;border:0;background:transparent;color:#333;display:grid;place-items:center;cursor:pointer}.h-search button svg{width:18px;height:18px}
.h-acts{display:flex;align-items:center;gap:18px}
.h-acc{display:flex;align-items:center;gap:8px;height:44px;padding:0 14px;border:0;border-radius:10px;background:#f1f1f1;color:#000;font:inherit;font-size:13px;cursor:pointer}
.h-acc svg{width:18px;height:18px}.h-acc svg:last-child{width:14px;height:14px}
.h-ic{position:relative;display:grid;place-items:center;color:#000;background:none;border:0;padding:0;cursor:pointer}.h-ic svg{width:22px;height:22px}
.h-cq{position:absolute;top:-7px;right:-9px;min-width:17px;height:17px;border-radius:99px;background:#000;color:#fff;font-size:10px;font-weight:600;display:grid;place-items:center;padding:0 3px}
.h-burger{display:none;background:none;border:0;padding:0;color:#000}.h-burger svg{width:26px;height:26px}
.h-nav{background:#000}
.h-nav>ul{list-style:none;display:flex;justify-content:center;flex-wrap:wrap;margin:0 auto;padding-block:0}
.h-nav li{position:static}
.h-nav>ul>li>a{display:block;color:#fff;text-decoration:none;padding:15px 20px;font-size:14px;line-height:20px;white-space:nowrap}
.h-nav>ul>li>a:hover,.h-nav a.on{color:var(--h-ac)}
.h-dd-box{display:none;position:absolute;left:0;right:0;background:#fff;box-shadow:0 12px 30px rgba(0,0,0,.15);padding:26px 0;z-index:40}
.h-dd:hover .h-dd-box,.h-dd:focus-within .h-dd-box{display:block}
.h-dd-cols{display:flex;gap:60px}
.h-dd-cols b{display:block;color:#000;font-weight:600;margin-bottom:10px}
.h-dd-cols a,.h-dd-marcas a{display:block;color:#444;text-decoration:none;padding:4px 0;font-size:14px}
.h-dd-cols a:hover,.h-dd-marcas a:hover{color:var(--h-ac)}
.h-dd-marcas{display:grid;grid-template-columns:repeat(6,1fr);gap:0 24px}
@media(max-width:1000px){
  .h-burger{display:grid}.h-top-in{flex-wrap:wrap;height:auto;padding-block:10px;gap:12px}.h-logo{margin-right:auto}.h-logo img{height:40px}
  .h-search{order:5;width:100%}.h-acc span{display:none}.h-acc{padding:0 10px;height:40px}.h-acc svg:last-child{display:none}.h-wa-top{display:none}
  .h-nav{display:none;position:fixed;inset:0 18% 0 0;z-index:60;overflow:auto;box-shadow:0 0 0 100vmax rgba(0,0,0,.45)}
  body.nav-open .h-nav{display:block}
  .h-nav>ul{flex-direction:column;padding:16px 0}
  .h-nav>ul>li>a{padding:14px 20px;border-bottom:1px solid #222}
  .h-dd-box{display:block;position:static;background:#111;box-shadow:none;padding:6px 20px 14px}
  .h-dd-cols{flex-direction:column;gap:12px;padding:0}.h-dd-cols b{color:#aaa;font-size:12px}.h-dd-cols a,.h-dd-marcas a{color:#ddd}
  .h-dd-marcas{grid-template-columns:1fr 1fr;padding:0}
}
/* banner */
.h-banner{padding:20px 0}
.h-banner .h-w{position:relative}
.h-slides{position:relative;aspect-ratio:1200/366;background:#0a0a0a;overflow:hidden}
.h-slide{position:absolute;inset:0;opacity:0;transition:opacity .6s;background:#0a0a0a center/cover no-repeat;color:#fff;text-decoration:none;display:flex;align-items:center}
.h-slide.on{opacity:1;z-index:1}
.h-slide-tx{margin-left:auto;margin-right:6%;max-width:46%;display:flex;flex-direction:column;align-items:flex-start;gap:12px}
.h-slide-tx p{margin:0;font-size:12px;letter-spacing:.3em;color:#e7c66f;font-weight:500}
.h-slide-tx h2{margin:0;font-family:'Cormorant Garamond',Georgia,serif!important;font-weight:600;font-size:clamp(1.8rem,4.4vw,3.6rem);line-height:1.02;color:#fff}
.h-slide-tx h2 em{color:#e7c66f}
.h-slide-tx b{background:#fff;color:#000;font-weight:700;padding:8px 22px;font-size:14px;letter-spacing:.02em}
.h-slide2{background:radial-gradient(800px 400px at 30% 50%,#2a2114,#0a0a0a 70%)}
.h-slide2 .h-slide-tx{margin-left:6%;margin-right:auto}
.h-slide2 img{position:absolute;right:0;top:0;height:100%;width:48%;object-fit:cover;object-position:50% 20%;-webkit-mask-image:linear-gradient(90deg,transparent,#000 35%);mask-image:linear-gradient(90deg,transparent,#000 35%)}
.h-arr{position:absolute;top:50%;transform:translateY(-50%);z-index:3;width:36px;height:36px;border:0;border-radius:6px;background:var(--h-ac);color:#fff;display:grid;place-items:center;cursor:pointer}
.h-arr svg{width:16px;height:16px}.h-arr-l{left:26px}.h-arr-r{right:26px}
@media(max-width:700px){.h-slides{aspect-ratio:4/5}.h-slide{align-items:flex-end;background-position:28% center}.h-slide-tx,.h-slide2 .h-slide-tx{margin:0 14px 24px;max-width:none;padding:18px;background:rgba(0,0,0,.55);border-radius:10px}.h-slide2 img{width:100%;opacity:.5;-webkit-mask-image:none;mask-image:none}.h-arr{display:none}}
/* condições */
.h-conds{padding:30px 0 20px}
.h-conds-in{display:grid;grid-template-columns:repeat(4,1fr);gap:20px}
.h-conds-in a{display:flex;flex-direction:column;align-items:center;text-align:center;text-decoration:none;color:#000}
.h-conds-in svg{width:26px;height:26px;color:var(--h-ac);margin-bottom:8px}
.h-conds-in b{font-size:18px;font-weight:600;line-height:28px}.h-conds-in span{font-size:14px;line-height:24px;color:#000}
@media(max-width:800px){.h-conds-in{grid-template-columns:1fr 1fr;gap:22px 10px}.h-conds-in b{font-size:15px;line-height:22px}.h-conds-in span{font-size:12px;line-height:18px}}
/* títulos e listas */
.h-list{padding:30px 0}
.h-title{font-size:22px!important;font-weight:600!important;color:#000!important;text-align:center;margin:0 0 20px!important;line-height:30px}
.h-sub{text-align:center;color:#444;margin:-12px 0 20px;font-size:14px}
.h-car{position:relative;padding:0 54px}
.h-car-btn{position:absolute;top:50%;transform:translateY(-50%);width:30px;height:30px;border:0;border-radius:6px;background:var(--h-ac);color:#fff;display:grid;place-items:center;cursor:pointer;z-index:2}
.h-car-btn svg{width:14px;height:14px}.h-car-btn.l{left:0}.h-car-btn.r{right:0}
.h-track{display:grid;grid-auto-flow:column;grid-auto-columns:calc((100% - 3*20px)/4);gap:20px;overflow-x:auto;scroll-snap-type:x mandatory;scrollbar-width:none}
.h-track::-webkit-scrollbar{display:none}.h-track>*{scroll-snap-align:start}
@media(max-width:900px){.h-track{grid-auto-columns:calc((100% - 12px)/2);gap:12px}.h-car{padding:0 36px}}
@media(max-width:520px){.h-car{padding:0}.h-car-btn{display:none}.h-track{grid-auto-columns:70%}}
/* card */
.h-card{position:relative;background:#fff;border:1px solid transparent;border-radius:10px;padding:20px;display:flex;flex-direction:column;transition:border-color .2s,box-shadow .2s;min-width:0}
.h-card:hover{border-color:#e5e5e5;box-shadow:0 6px 18px rgba(0,0,0,.07)}
.h-ph{position:relative;aspect-ratio:1;cursor:pointer;display:block}
.h-ph img{width:100%;height:100%;object-fit:contain;display:block}
.h-ph .h-ph0{width:100%;height:100%;display:grid;place-items:center;background:#f6f6f6;border-radius:8px}.h-ph .h-ph0 svg{width:42%}
.h-tags{position:absolute;top:-8px;right:-8px;display:flex;flex-direction:column;align-items:flex-end;gap:4px;z-index:2}
.h-tag{display:inline-block;background:var(--h-red);color:#fff;font-size:12px;line-height:24px;padding:0 10px;border-radius:100px;white-space:nowrap}
.h-tag.dk{background:#000}
.h-n{display:-webkit-box;-webkit-line-clamp:3;-webkit-box-orient:vertical;overflow:hidden;color:#444;text-decoration:none;font-size:14px;line-height:20px;min-height:60px;margin-top:12px}
.h-n:hover{color:#000}
.h-cmp{font-size:12px;color:#999;text-decoration:line-through;margin-top:8px}
.h-pr{font-size:18px;font-weight:600;color:#000;margin-top:6px}.h-pr small{font-size:12px;font-weight:400;color:#444;margin-left:4px}
.h-ins{font-size:12px;color:#666}
.h-buy{margin-top:12px;height:38px;border:0;border-radius:8px;background:#000;color:#fff;font:inherit;font-size:13px;font-weight:600;cursor:pointer;text-decoration:none;display:grid;place-items:center}
.h-buy:hover{background:var(--h-ac)}
/* banner largo */
.h-full{margin:20px 0}
.h-full a{display:flex;flex-direction:column;align-items:center;justify-content:center;height:clamp(220px,31vw,420px);background:linear-gradient(rgba(0,0,0,.35),rgba(0,0,0,.45)),url(/img/hero.jpg) center 30%/cover no-repeat;color:#fff;text-decoration:none;text-align:center}
.h-full span{font-family:'Cormorant Garamond',Georgia,serif;font-size:clamp(3.4rem,11vw,9.5rem);line-height:.9;letter-spacing:.04em;font-weight:500}
.h-full em{font-style:normal;font-size:clamp(.9rem,1.6vw,1.3rem);opacity:.9;margin-top:10px}
/* grade */
.h-grid{display:grid;grid-template-columns:repeat(4,1fr);gap:20px}
@media(max-width:900px){.h-grid{grid-template-columns:repeat(3,1fr);gap:12px}}
@media(max-width:620px){.h-grid{grid-template-columns:1fr 1fr;gap:10px}.h-card{padding:12px}.h-tags{right:-4px;top:-6px}.h-tag{font-size:10px;line-height:20px;padding:0 8px}.h-pr{font-size:16px}}
.h-more{display:flex;justify-content:center;margin-top:26px}
.h-more button{height:44px;padding:0 34px;border:0;border-radius:8px;background:#000;color:#fff;font:inherit;font-weight:600;cursor:pointer}
.h-more button:hover{background:var(--h-ac)}
.empty{grid-column:1/-1;text-align:center;color:#777;padding:40px 0}
.h-crumb{display:none;font-size:12px;color:#888;margin:0 0 10px}.h-crumb a{color:#444}
.h-bar{display:none;flex-wrap:wrap;gap:12px;align-items:center;justify-content:space-between;margin:0 0 22px;padding-bottom:16px;border-bottom:1px solid #eee}
.h-chips{display:flex;flex-wrap:wrap;gap:6px}
.h-chips .tab{border:0;background:#f1f1f1;color:#000;border-radius:8px;padding:8px 14px;font:inherit;font-size:12px;cursor:pointer}
.h-chips .tab.on{background:#000;color:#fff}
.h-filt{display:flex;gap:8px;align-items:center;flex-wrap:wrap}
.h-filt select{border:0;background:#f1f1f1;border-radius:8px;padding:9px 12px;font:inherit;font-size:13px;color:#000}
.h-filt .count{font-size:13px;color:#777}
/* fabricantes */
.h-brands{padding:30px 0}
.h-brand-track{grid-auto-columns:calc((100% - 5*14px)/6);gap:14px}
.h-brand-track a{height:46px;display:grid;place-items:center;border:1px solid #e5e5e5;border-radius:8px;color:#000;text-decoration:none;font-weight:600;font-size:13px;letter-spacing:.02em;text-transform:uppercase;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;padding:0 10px}
.h-brand-track a:hover{border-color:var(--h-ac);color:var(--h-ac)}
@media(max-width:900px){.h-brand-track{grid-auto-columns:calc((100% - 2*12px)/3)}}
/* newsletter */
.h-news{background:#eee;padding:50px 0}
.h-news-in{display:grid;grid-template-columns:1fr 1fr;gap:30px;align-items:center}
.h-news h3{font-size:20px;font-weight:600;color:#000;margin:0 0 6px}.h-news p{margin:0;color:#444}
.h-news-f{display:grid;grid-template-columns:1fr 1fr auto;gap:10px}
.h-news-f input{height:43px;border:0;background:#fff;padding:0 14px;font:inherit;font-size:13px;color:#000}
.h-news-f button{height:43px;border:0;background:#000;color:#fff;padding:0 20px;font:inherit;cursor:pointer}
.h-news-f button:hover{background:var(--h-ac)}
.h-news-f p{grid-column:1/-1;font-size:12px;min-height:1em}
@media(max-width:800px){.h-news-in{grid-template-columns:1fr}.h-news-f{grid-template-columns:1fr}}
/* footer */
.h-foot{background:#000;color:#fff;padding-top:50px}
.h-foot h4{font-size:16px;font-weight:500;color:#fff;margin:0 0 14px}
.h-foot p{margin:0 0 10px;font-size:13px;line-height:20px;color:#fff}
.h-foot a{display:block;color:#fff;text-decoration:none;font-size:13px;line-height:20px;padding:4px 0}.h-foot a:hover{color:var(--h-ac)}
.h-foot-top{display:grid;grid-template-columns:1.6fr 1fr 1.2fr .8fr;gap:40px;padding-bottom:40px;border-bottom:1px solid #444}
.h-foot-ic{display:flex;gap:8px;align-items:center}.h-foot-ic svg{width:15px;height:15px}
.h-foot-small{color:#aaa!important;font-size:12px!important;margin-top:6px!important}
.h-soc{display:flex;gap:14px}.h-soc a{padding:0}.h-soc svg{width:20px;height:20px}
.h-foot-bot{display:grid;grid-template-columns:1fr 1fr;gap:40px;padding:30px 0 40px}
.h-pays{display:flex;flex-wrap:wrap;gap:6px}
.h-pays span{height:26px;min-width:40px;padding:0 8px;border-radius:4px;background:#fff;color:#1a1f71;font-size:11px;font-weight:800;display:grid;place-items:center;font-style:italic}
.h-pays .pix{color:#32bcad;font-style:normal}.h-pays .elo{color:#000;font-style:normal;font-weight:700}
.h-pays .mc{position:relative}.h-pays .mc i{position:absolute;width:14px;height:14px;border-radius:50%;top:6px}.h-pays .mc i:first-child{background:#eb001b;left:9px}.h-pays .mc i:last-child{background:#f79e1b;left:17px;mix-blend-mode:multiply}
.h-seals{display:flex;flex-wrap:wrap;gap:10px}
.h-seals span{height:40px;padding:0 14px;border-radius:6px;background:#fff;color:#000;font-size:12px;font-weight:600;display:flex;align-items:center;gap:6px}.h-seals svg{width:14px;height:14px}
.h-copy{background:#fff;color:#666;font-size:12px;padding:20px 0;text-align:center}
@media(max-width:900px){.h-foot-top{grid-template-columns:1fr 1fr;gap:28px}.h-foot-bot{grid-template-columns:1fr}}
/* quiz */
.h-quiz{display:none;padding:30px 0 60px;min-height:60vh}
.h-quiz .sh h2{font-size:22px!important;font-weight:600!important;color:#000!important;text-transform:none}
.h-quiz .rule{display:none}
.h-quiz .chips button{border:0!important;background:#f1f1f1!important;color:#000!important;border-radius:8px!important}
.h-quiz .chips button.on{background:#000!important;color:#fff!important}
.h-quiz #qz-res{display:grid;grid-template-columns:repeat(4,1fr);gap:20px;margin-top:24px}
@media(max-width:700px){.h-quiz #qz-res{grid-template-columns:1fr 1fr;gap:10px}}
/* modos */
body.modo-lista .h-home,body.modo-quiz .h-home,body.modo-quiz .h-colecoes{display:none}
body.modo-lista .h-crumb{display:block}body.modo-lista .h-bar{display:flex}
body.modo-lista .h-colecoes .h-title,body.modo-lista .h-sub{text-align:left}
body.modo-quiz .h-quiz{display:block}
body.pg-p .h-banner{display:none}
/* modais no padrão */
.pv-box{border-radius:10px!important;border:0!important}
.pv-info h3{font-family:var(--hf)!important;font-weight:600!important;font-size:1.5rem!important;color:#000!important}
.pv .pix{color:#000!important}
.pv-info .acts .buy{background:#000!important;color:#fff!important;border-radius:8px!important}
.pv-info .add-cart{background:var(--h-ac)!important;color:#fff!important;border:0!important;border-radius:8px!important}
.pv-info .acts .ask{border-radius:8px!important}
.mx-box{border-radius:10px!important}.mx .go{border-radius:8px!important;background:#000!important}
.fab{right:20px!important;bottom:20px!important}.fab a{background:#25d366!important}
.ssr-p{background:#fff!important;border:0!important}.ssr-i h1{font-family:var(--hf)!important;font-weight:600!important;color:#000!important}
.ssr-i .acts a.buy{background:#000!important;color:#fff!important;border-radius:8px!important}.ssr-i .pix{color:#000!important}
"""

head = head.replace('</head>', '<style>' + CSS + '</style>\n</head>', 1)
out = head + BODY

def rep(old, new):
    global out
    assert old in out, 'JS não achei: ' + old[:80]
    out = out.replace(old, new, 1)

# faixa promo inexistente
rep("""{const items=(FRETE_GRATIS>0?[`Frete grátis acima de ${brl(FRETE_GRATIS)}`]:[]).concat(PROMO);const s='<span>'+items.map(t=>`<em>${t}</em>`).join('<i>◆</i>')+'</span>';$('#promo-track').innerHTML=s;}""", "")

# card padrão Hilda
cs = out.index('function card(it,o={}){'); ce = out.index('const byName=', cs)
out = out[:cs] + r"""function card(it,o={}){
  const off=offPct(it);const tags=[];
  if(off)tags.push(`<span class="h-tag">${off}% OFF</span>`);else if(it.p!=null)tags.push(`<span class="h-tag">10% OFF no PIX</span>`);
  if(it.best)tags.push(`<span class="h-tag dk">Mais vendido</span>`);
  const price=it.p==null?`<div class="h-pr">Consultar</div>`:`${off?`<div class="h-cmp">${brl(it.po)}</div>`:''}<div class="h-pr">${brl(pix(it.p))}<small>no PIX</small></div><div class="h-ins">ou ${brl(it.p)} em até 12x</div>`;
  return `<div class="h-card"><a class="h-ph" href="/p/${it.slug}" data-open="${it.id}">${it.img?`<img src="${it.img}" alt="${it.b} ${it.n}" loading="lazy">`:`<span class="h-ph0">${bottle}</span>`}<span class="h-tags">${tags.join('')}</span></a>
   <a class="h-n" href="/p/${it.slug}" data-open="${it.id}">${it.n} - ${it.b} - Perfume ${G[it.g]}</a>${price}
   ${it.p!=null?`<button class="h-buy" type="button" data-add="${it.id}">Comprar</button>`:`<a class="h-buy ask" href="${waLink(it)}" target="_blank" rel="noopener">Consultar</a>`}</div>`;
}
""" + out[ce:]

rs = out.index('function renderFixos(){'); re_ = out.index('renderFixos();', rs)
out = out[:rs] + r"""function renderFixos(){
  const best=ITEMS.some(i=>i.best)?ITEMS.filter(i=>i.best):BEST.map(byName).filter(Boolean);
  const extra=ITEMS.filter(i=>i.img&&i.p!=null&&!best.includes(i)&&!i.splash&&!i.kit).slice(0,6);
  $('#best').innerHTML=[...best,...extra].slice(0,14).map(i=>card(i)).join('');
  const marcas=[...new Set(ITEMS.map(i=>i.b))].sort((a,b)=>a.localeCompare(b));
  const sel=$('#brand'),cur=sel.value;sel.innerHTML='<option value="">Todas as marcas</option>'+marcas.map(b=>`<option>${b}</option>`).join('');sel.value=cur;
  $('#nav-marcas').innerHTML=marcas.map(b=>`<a href="/c/${slug(b)}" data-cat="${slug(b)}">${b}</a>`).join('');
  const porQtd=[...marcas].sort((a,b)=>ITEMS.filter(i=>i.b===b).length-ITEMS.filter(i=>i.b===a).length);
  $('#brands').innerHTML=porQtd.map(b=>`<a href="/c/${slug(b)}" data-cat="${slug(b)}">${b}</a>`).join('');
}
""" + out[re_:]

rep("Object.keys(OCC).forEach(k=>CATS[k]={occ:k,t:OCC[k].t,s:OCC[k].s});",
    "Object.keys(OCC).forEach(k=>{CATS[k]={occ:k,t:OCC[k].t,s:OCC[k].s};[['masculino','M','masculinos'],['feminino','F','femininos']].forEach(([n,g,pl])=>CATS[k+'-'+n]={occ:k,f:g,t:OCC[k].t+' · perfumes '+pl,s:OCC[k].s})});")
rep("function passF(i){switch(f){case'M':case'F':case'U':return i.g===f;",
    "function passF(i){switch(f){case'M':case'F':return i.g===f||(!!OCCF&&i.g==='U');case'U':return i.g===f;")
rep("function setF(v,scroll){", """window.setModo=function(m){document.body.classList.toggle('modo-lista',m==='lista');document.body.classList.toggle('modo-quiz',m==='quiz');if(m==='quiz'){document.title='Descubra o seu perfume · Nota Perfumaria';(function(){try{history.pushState(null,'','/#descubra')}catch(e){}})()}};
function setF(v,scroll){""")
rep("""  if(push)history.pushState(null,'',c==='all'?'/':'/c/'+c);catHead();render(true);
  if(scroll!==false)$('#colecoes').scrollIntoView({behavior:'smooth'});""",
    """  if(push)history.pushState(null,'',c==='all'?'/':'/c/'+c);catHead();render(true);setModo(c==='all'?'home':'lista');
  if(scroll!==false)scrollTo({top:0,behavior:'smooth'});""")
rep("""function setF(v,scroll){f=v;FAMF='';OCCF='';CAT=Object.keys(CATS).find(k=>CATS[k].f===v)||'all';catHead();render(true);if(scroll)$('#colecoes').scrollIntoView({behavior:'smooth'})}""",
    """function setF(v,scroll){f=v;FAMF='';OCCF='';CAT=Object.keys(CATS).find(k=>CATS[k].f===v)||'all';catHead();render(true);setModo('lista');if(CAT!=='all'){(function(){try{history.replaceState(null,'','/c/'+CAT)}catch(e){}})()}}""")
rep("""$('#cat-crumb').hidden=CAT==='all';""", "")
rep("""const title=brandCat?($('#brand').value||'Marca'):(c.t||'A coleção Nota');""", """const title=brandCat?($('#brand').value||'Marca'):(c.t||'Todos os perfumes');""")
rep("""$('#sform').addEventListener('submit',e=>{e.preventDefault();f='all';render(true);$('#colecoes').scrollIntoView({behavior:'smooth'})});""",
    """$('#sform').addEventListener('submit',e=>{e.preventDefault();f='all';FAMF='';OCCF='';CAT='all';$('#brand').value='';render(true);catHead();const v=$('#q').value.trim();$('#cat-title').textContent=v?`Busca: ${v}`:'Todos os perfumes';setModo('lista');scrollTo({top:0,behavior:'smooth'})});
$('#q').addEventListener('input',()=>{if($('#q').value.trim().length>=2&&!document.body.classList.contains('modo-lista')){setModo('lista');$('#cat-title').textContent='Busca'}});""")
rep("""  if(p.startsWith('/c/')){setCat(p.slice(3),false,false);if(!document.body.classList.contains('pg-c'))setTimeout(()=>$('#colecoes').scrollIntoView(),50);return true}""",
    """  if(p.startsWith('/c/')){setCat(p.slice(3),false,false);return true}
  if(location.hash==='#descubra'){setModo('quiz');return true}""")
rep("""if(location.pathname.startsWith('/c/'))setCat(location.pathname.slice(3),false,false);else setCat('all',false,false)}});""",
    """if(location.pathname.startsWith('/c/'))setCat(location.pathname.slice(3),false,false);else{setCat('all',false,false);setModo(location.hash==='#descubra'?'quiz':'home')}}});""")
rep("""`<button class="btn btn-ghost" id="morebtn">Carregar mais (${out.length-show.length})</button>`""", """`<button type="button" id="morebtn">Carregar mais produtos (${out.length-show.length})</button>`""")
rep("""const pol=t.closest('[data-pol]');if(pol){e.preventDefault();const d=document.getElementById('pol-'+pol.dataset.pol);if(d){d.open=true;d.scrollIntoView({behavior:'smooth',block:'start'});return}""",
    """const pol=t.closest('[data-pol]');if(pol){e.preventDefault();const d=document.getElementById('pol-'+pol.dataset.pol);if(d){const s=d.querySelector('summary').textContent;const b=[...d.querySelectorAll('p')].map(p=>`<p style="color:#444;line-height:1.6;margin:0 0 12px">${p.innerHTML}</p>`).join('');mx(`<h3>${s}</h3>${b}`,true);return}""")
rep("""body:JSON.stringify({email:v,origem:'newsletter',utm:UTM,visitante:VIS})""", """body:JSON.stringify({email:v,nome:($('#nnome')&&$('#nnome').value.trim())||null,origem:'newsletter',utm:UTM,visitante:VIS})""")
rep("""const z=a.closest('.card');""", """const z=a.closest('.h-card');""")

open(P, 'w', encoding='utf-8').write(out)
print('ok', len(out.encode()) // 1024, 'KB')
