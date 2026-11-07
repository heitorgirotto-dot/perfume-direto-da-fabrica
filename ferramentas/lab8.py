"""Reconstrói a home da Nota no esqueleto da LAB 8 (Nuvemshop 'flex'), mantendo carrinho, checkout,
conta, leads e painel. Uso: python3 lab8.py <repo>"""
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
faq_items = grab(r'(?<=<div class="faq">\n)(?:    <details>.*?</details>\n)+(?=  </div>\n</div></section>\n\n<section class="sobre")') if False else None
faq_block = re.search(r'<section id="faq"><div class="wrap">.*?<div class="faq">\n(.*?)  </div>\n</div></section>', html, re.S).group(1)
pol_block = re.search(r'<section id="politicas" class="pol"><div class="wrap">.*?<div class="faq">\n(.*?)  </div>\n</div></section>', html, re.S).group(1)
quiz_inner = re.search(r'<section id="assinatura" class="quiz"><div class="wrap">\n(.*?)</div></section>', html, re.S).group(1)

# ------------------------------------------------------------------ HEAD
head = head.replace('family=Cormorant+Garamond', 'family=Plus+Jakarta+Sans:wght@300;400;500;600;700&family=Cormorant+Garamond', 1)

ICON = {
 'user': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6"><circle cx="12" cy="12" r="9.5"/><circle cx="12" cy="10" r="3.2"/><path d="M6.2 18.4c1.4-2.2 3.4-3.3 5.8-3.3s4.4 1.1 5.8 3.3"/></svg>',
 'bag': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6"><path d="M5 8h14l-1.2 12.2a1 1 0 0 1-1 .8H7.2a1 1 0 0 1-1-.8z"/><path d="M9 8V6.5a3 3 0 0 1 6 0V8"/></svg>',
 'search': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><circle cx="10.5" cy="10.5" r="6.5"/><path d="M15.5 15.5 21 21"/></svg>',
 'eye': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><path d="M2 12s3.6-6.5 10-6.5S22 12 22 12s-3.6 6.5-10 6.5S2 12 2 12z"/><circle cx="12" cy="12" r="3"/></svg>',
 'left': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><path d="M15 5l-7 7 7 7"/></svg>',
 'right': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><path d="M9 5l7 7-7 7"/></svg>',
 'menu': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><path d="M3 6h18M3 12h18M3 18h18"/></svg>',
 'truck': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M2.5 6.5h11v9h-11zM13.5 9.5h4l3 3v3h-7z"/><circle cx="6.5" cy="17.5" r="1.8"/><circle cx="17" cy="17.5" r="1.8"/></svg>',
 'card': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><rect x="2.5" y="5.5" width="19" height="13" rx="2"/><path d="M2.5 9.5h19M6 15h4"/></svg>',
 'lock': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><rect x="5" y="10.5" width="14" height="10" rx="2"/><path d="M8 10.5V7.5a4 4 0 0 1 8 0v3"/></svg>',
 'wa': '<svg viewBox="0 0 24 24" fill="currentColor"><path d="M12 2a10 10 0 0 0-8.6 15.1L2 22l5-1.3A10 10 0 1 0 12 2zm0 18.2a8.2 8.2 0 0 1-4.2-1.2l-.3-.2-3 .8.8-2.9-.2-.3A8.2 8.2 0 1 1 12 20.2zm4.5-6.1c-.2-.1-1.5-.7-1.7-.8s-.4-.1-.6.1-.7.8-.8 1-.3.2-.5.1a6.7 6.7 0 0 1-3.3-2.9c-.3-.4.3-.4.8-1.4.1-.2 0-.3 0-.4l-.8-1.8c-.2-.5-.4-.4-.6-.4h-.5a1 1 0 0 0-.7.3 3 3 0 0 0-.9 2.2 5.2 5.2 0 0 0 1.1 2.7 11.8 11.8 0 0 0 4.5 4c1.7.7 2.3.8 3.2.6a2.7 2.7 0 0 0 1.8-1.3 2.2 2.2 0 0 0 .2-1.3c-.1-.1-.2-.2-.5-.3z"/></svg>',
 'insta': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6"><rect x="3" y="3" width="18" height="18" rx="5"/><circle cx="12" cy="12" r="4"/><circle cx="17.5" cy="6.5" r="1" fill="currentColor"/></svg>',
 'swap': '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M4 9h14l-3-3M20 15H6l3 3"/></svg>',
}

def stamp(lines, label, sub, icon):
    t = ' • '.join(lines) + ' • '
    return f'''<div class="l8-stamp"><svg viewBox="0 0 120 120" aria-hidden="true"><defs><path id="c-{label[:4]}" d="M60 60m-46 0a46 46 0 1 1 92 0a46 46 0 1 1-92 0"/></defs><circle cx="60" cy="60" r="56" fill="none" stroke="#111" stroke-width="1.2"/><circle cx="60" cy="60" r="34" fill="none" stroke="#111" stroke-width="1"/><text font-size="8.6" letter-spacing="1.6" font-weight="600" fill="#111"><textPath href="#c-{label[:4]}">{t.upper()}</textPath></text><g transform="translate(42 42) scale(1.5)" fill="none" stroke="#111" stroke-width="1.4">{icon}</g></svg><b>{label}</b><span>{sub}</span></div>'''

ST_ICONS = [
 '<path d="M12 3l7 3v5c0 5-3.5 8-7 10-3.5-2-7-5-7-10V6z"/><path d="M9 12l2 2 4-4"/>',
 '<rect x="5" y="10" width="14" height="10" rx="2"/><path d="M8 10V7a4 4 0 0 1 8 0v3"/>',
 '<path d="M3 7h11v9H3zM14 10h4l3 3v3h-7z"/><circle cx="7" cy="18" r="2"/><circle cx="17" cy="18" r="2"/>',
 '<path d="M4 5h16v11H8l-4 4z"/><path d="M8 9h8M8 12h5"/>',
]

FAM_SVG = {
 'doce': '<g fill="#5a3418"><path d="M30 150c40-70 90-110 140-120-35 30-75 75-120 135z" opacity=".95"/><path d="M60 170c40-70 85-105 125-112-30 28-70 70-110 128z" opacity=".8"/></g><g fill="#f7efe2"><circle cx="150" cy="150" r="20"/><circle cx="150" cy="150" r="8" fill="#e8c873"/></g><g fill="#fff8ec" opacity=".9"><path d="M150 118c6 10 6 18 0 24-6-6-6-14 0-24zM182 150c-10 6-18 6-24 0 6-6 14-6 24 0zM150 182c-6-10-6-18 0-24 6 6 6 14 0 24zM118 150c10-6 18-6 24 0-6 6-14 6-24 0z"/></g>',
 'amadeirado': '<g fill="none" stroke="#5b3a1e" stroke-width="3" opacity=".75">' + ''.join(f'<ellipse cx="100" cy="110" rx="{12+i*13}" ry="{18+i*16}"/>' for i in range(7)) + '</g><path d="M100 0v40M70 0c8 20 8 35 0 50M130 0c-8 20-8 35 0 50" stroke="#4a2e17" stroke-width="2" fill="none" opacity=".5"/>',
 'fresco': '<circle cx="100" cy="100" r="78" fill="#f7b733"/><circle cx="100" cy="100" r="70" fill="#fde7a5"/><g fill="#f9c74f">' + ''.join(f'<path d="M100 100 L{100+64*__import__("math").cos(__import__("math").radians(a)):.1f} {100+64*__import__("math").sin(__import__("math").radians(a)):.1f} A64 64 0 0 1 {100+64*__import__("math").cos(__import__("math").radians(a+40)):.1f} {100+64*__import__("math").sin(__import__("math").radians(a+40)):.1f}z" transform="rotate(4 100 100)"/>' for a in range(0, 360, 45)) + '</g><circle cx="100" cy="100" r="8" fill="#fff6d6"/>',
 'floral': '<g transform="translate(100 100)">' + ''.join(f'<ellipse rx="26" ry="62" fill="#f7c6d5" stroke="#e79ab3" stroke-width="2" transform="rotate({a}) translate(0 -46)"/>' for a in range(0, 360, 60)) + '<circle r="22" fill="#f4d35e"/><g fill="#c9772c">' + ''.join(f'<circle r="2.6" cx="{10*__import__("math").cos(__import__("math").radians(a)):.1f}" cy="{10*__import__("math").sin(__import__("math").radians(a)):.1f}"/>' for a in range(0, 360, 40)) + '</g></g>',
 'oriental': '<g transform="translate(100 100)">' + ''.join(f'<path d="M0 0 L-14 -60 Q0 -78 14 -60z" fill="#7a3b17" stroke="#4d220b" stroke-width="2" transform="rotate({a})"/>' for a in range(0, 360, 45)) + '<circle r="14" fill="#5a2a0f"/>' + ''.join(f'<ellipse rx="5" ry="8" fill="#e2a24a" transform="rotate({a}) translate(0 -40)"/>' for a in range(0, 360, 45)) + '</g>',
}
FAM_BG = {'doce': '#f3e3cf', 'amadeirado': '#c99c6e', 'fresco': '#fff4cf', 'floral': '#fbe4ec', 'oriental': '#e6b375'}
FAM_LBL = {'doce': 'Doce', 'amadeirado': 'Amadeirado', 'fresco': 'Cítrico & fresco', 'floral': 'Floral', 'oriental': 'Oriental'}

fam_tiles = ''.join(f'''<a class="l8-fam-it" href="/c/{k}" data-cat="{k}"><span>{FAM_LBL[k]}</span><div class="l8-fam-media" style="background:{FAM_BG[k]}"><svg viewBox="0 0 200 220" preserveAspectRatio="xMidYMid slice" aria-hidden="true">{FAM_SVG[k]}</svg></div></a>''' for k in ['fresco', 'amadeirado', 'doce', 'floral', 'oriental'])

BODY = f'''<body>
<div class="l8-adbar"><div class="l8w l8-adbar-in">
  <button class="l8-ad-arr" type="button" data-ad="-1" aria-label="Anterior">{ICON['left']}</button>
  <div class="l8-ad-msgs" id="ad-msgs"><span class="on">{ICON['truck']} Entrega para todo o Brasil com rastreio</span><span>{ICON['card']} PIX com 10% de desconto ou até 12x no cartão</span><span>{ICON['swap']} 7 dias para troca ou devolução</span></div>
  <button class="l8-ad-arr" type="button" data-ad="1" aria-label="Próxima">{ICON['right']}</button>
  <div class="l8-ad-links"><a href="#" data-pol="contato">CONTATO</a><span>|</span><a href="#" data-pol="trocas">TROCAS E DEVOLUÇÕES</a></div>
</div></div>
<header class="l8-head" id="topo"><div class="l8w l8-head-in">
  <button class="l8-burger" type="button" id="burger" aria-label="Menu">{ICON['menu']}</button>
  <a class="l8-logo" href="/" data-cat="all" aria-label="Nota Perfumaria"><img src="/img/logo-t.png?v=1" alt="Nota Perfumaria" width="640" height="237"></a>
  <nav class="l8-nav" id="nav" aria-label="Navegação da loja">
    <a href="/" data-cat="all">INÍCIO</a>
    <div class="l8-dd"><a href="/c/mais-desejados" data-cat="mais-desejados">PERFUMES</a><div class="l8-dd-box"><div class="l8-dd-cols">
      <div><h5>Gênero</h5><a href="/c/masculinos" data-cat="masculinos">Perfumes masculinos</a><a href="/c/femininos" data-cat="femininos">Perfumes femininos</a><a href="/c/unissex" data-cat="unissex">Perfumes unissex</a></div>
      <div><h5>Origem</h5><a href="/c/arabes" data-cat="arabes">Perfumes árabes</a><a href="/c/importados" data-cat="importados">Importados & grifes</a></div>
      <div><h5>Formatos</h5><a href="/c/kits" data-cat="kits">Kits e presentes</a><a href="/c/body-splash" data-cat="body-splash">Body splash & mists</a><a href="/c/ofertas" data-cat="ofertas">Ofertas</a></div>
    </div></div></div>
    <div class="l8-dd"><a href="/c/arabes" data-cat="arabes">MARCAS</a><div class="l8-dd-box"><div class="l8-dd-cols l8-dd-marcas" id="nav-marcas"></div></div></div>
    <div class="l8-dd"><a href="#ocasioes" data-jump="ocasioes">OCASIÕES</a><div class="l8-dd-box"><div class="l8-dd-cols">
      <div><h5>Masculinos</h5><a href="/c/romantico-masculino" data-cat="romantico-masculino">Encontros românticos</a><a href="/c/dia-masculino" data-cat="dia-masculino">Dia</a><a href="/c/noite-masculino" data-cat="noite-masculino">Noite</a><a href="/c/trabalho-masculino" data-cat="trabalho-masculino">Trabalho</a></div>
      <div><h5>Femininos</h5><a href="/c/romantico-feminino" data-cat="romantico-feminino">Encontros românticos</a><a href="/c/dia-feminino" data-cat="dia-feminino">Dia</a><a href="/c/noite-feminino" data-cat="noite-feminino">Noite</a><a href="/c/trabalho-feminino" data-cat="trabalho-feminino">Trabalho</a></div>
    </div></div></div>
    <div class="l8-dd"><a href="#familias" data-jump="familias">FAMÍLIAS OLFATIVAS</a><div class="l8-dd-box"><div class="l8-dd-cols">
      <div><h5>Famílias</h5><a href="/c/fresco" data-cat="fresco">Cítricos & frescos</a><a href="/c/amadeirado" data-cat="amadeirado">Amadeirados</a><a href="/c/doce" data-cat="doce">Doces</a><a href="/c/floral" data-cat="floral">Florais</a><a href="/c/oriental" data-cat="oriental">Orientais</a></div>
    </div></div></div>
    <a href="#assinatura" data-modo="quiz">DESCUBRA O SEU PERFUME IDEAL</a>
  </nav>
  <form class="l8-search" id="sform" role="search"><input id="q" type="search" placeholder="Buscar" aria-label="Buscar"><button type="submit" aria-label="Buscar">{ICON['search']}</button></form>
  <button class="l8-ic" id="acc-btn" type="button" aria-label="Minha conta">{ICON['user']}<span id="acc-lbl" class="sr">Entrar</span></button>
  <button class="l8-ic l8-cart" id="cart-btn" type="button" aria-label="Sacola">{ICON['bag']}<span class="l8-cq" id="cart-q">0</span><span id="cart-v" class="sr">R$ 0,00</span></button>
</div></header>

<main id="home" class="l8-home">
<section class="l8-hero" id="hero" aria-label="Destaques">
  <div class="l8-slides" id="slides">
    <a class="l8-slide on" href="/c/arabes" data-cat="arabes" style="--img:url(/img/capa.jpg)">
      <div class="l8-slide-tx right"><p>ALTA PERFUMARIA ORIGINAL</p><h2>Fragrâncias que <em>marcam presença</em></h2><span>Árabes e importados 100% originais, lacrados e escolhidos com você.</span><b>EXPLORAR A COLEÇÃO</b></div>
    </a>
    <a class="l8-slide l8-slide-split" href="/c/ofertas" data-cat="ofertas">
      <div class="l8-slide-tx left"><p>CURADORIA NOTA</p><h2>Perfumes árabes a partir de <em>R$ 71</em></h2><span>No PIX, com 10% de desconto. Ou em até 12x no cartão.</span><b>VER OFERTAS</b></div>
      <img src="/img/hero.jpg" alt="" loading="lazy">
    </a>
  </div>
  <button class="l8-hero-arr prev" type="button" data-slide="-1" aria-label="Anterior">{ICON['left']}</button>
  <button class="l8-hero-arr next" type="button" data-slide="1" aria-label="Próximo">{ICON['right']}</button>
  <div class="l8-dots" id="dots"><i class="on"></i><i></i></div>
</section>

<section class="l8-ticker" aria-hidden="true"><div class="l8-ticker-track" id="promo-track"></div></section>

<section class="l8-info"><div class="l8w l8-info-in">
  <div>{ICON['truck']}<p><b>Entrega para todo o Brasil</b><span>Correios com código de rastreio</span></p></div>
  <div>{ICON['card']}<p><b>PIX com 10% de desconto</b><span>ou em até 12x no cartão</span></p></div>
  <div>{ICON['lock']}<p><b>Site 100% seguro</b><span>Pagamento processado pelo Asaas</span></p></div>
</div></section>

<section class="l8-show" id="vendidos"><div class="l8w">
  <div class="l8-show-h"><h2>MAIS VENDIDOS</h2>
    <div class="l8-tabs" id="st-tabs"><button type="button" class="on" data-st="best">DESTAQUES</button><button type="button" data-st="arabe">ÁRABE</button><button type="button" data-st="M">MASCULINO</button><button type="button" data-st="F">FEMININO</button></div>
    <div class="l8-arrs"><button type="button" data-car="-1" aria-label="Anterior">{ICON['left']}</button><button type="button" data-car="1" aria-label="Próximo">{ICON['right']}</button></div>
  </div>
  <div class="l8-track" id="best"></div>
</div></section>

<section class="l8-oc" id="ocasioes"><div class="l8w l8-oc-in">
  <div class="l8-oc-side"><h2>EXPLORE DIFERENTES OCASIÕES</h2>
    <button type="button" class="l8-pill on" data-occg="masculino">PERFUMES MASCULINOS</button>
    <button type="button" class="l8-pill" data-occg="feminino">PERFUMES FEMININOS</button></div>
  <div class="l8-oc-wrap"><div class="l8-track l8-oc-track" id="occ-tiles"></div>
    <button class="l8-oc-arr prev" type="button" data-car="-1" aria-label="Anterior">{ICON['left']}</button><button class="l8-oc-arr next" type="button" data-car="1" aria-label="Próximo">{ICON['right']}</button></div>
</div></section>

<section class="l8-fam" id="familias"><div class="l8w">
  <h2>CONHEÇA AS FAMÍLIAS OLFATIVAS</h2>
  <div class="l8-fam-row" id="fam-tiles">{fam_tiles}</div>
</div></section>

<section class="l8-show" id="ofertas"><div class="l8w">
  <div class="l8-show-h"><h2>MELHORES OFERTAS DE HOJE!</h2><a class="l8-all" href="/c/ofertas" data-cat="ofertas">Ver todas</a>
    <div class="l8-arrs"><button type="button" data-car="-1" aria-label="Anterior">{ICON['left']}</button><button type="button" data-car="1" aria-label="Próximo">{ICON['right']}</button></div></div>
  <div class="l8-track" id="sale"></div>
</div></section>

<section class="l8-marca" id="marca"><div class="l8-marca-in">
  <div class="l8-marca-img"><img src="/img/hero.jpg" alt="" loading="lazy"></div>
  <div class="l8-marca-r">
    <div class="l8-show-h dark"><h2>LATTAFA</h2><a class="l8-all" href="/c/lattafa" data-cat="lattafa">Descubra a marca</a>
      <div class="l8-arrs"><button type="button" data-car="-1" aria-label="Anterior">{ICON['left']}</button><button type="button" data-car="1" aria-label="Próximo">{ICON['right']}</button></div></div>
    <div class="l8-track" id="marca-track"></div>
  </div>
</div></section>

<section class="l8-show" id="importados"><div class="l8w">
  <div class="l8-show-h"><h2>IMPORTADOS & GRIFES</h2><a class="l8-all" href="/c/importados" data-cat="importados">Ver todos</a>
    <div class="l8-arrs"><button type="button" data-car="-1" aria-label="Anterior">{ICON['left']}</button><button type="button" data-car="1" aria-label="Próximo">{ICON['right']}</button></div></div>
  <div class="l8-track" id="imp-track"></div>
</div></section>

<section class="l8-bcat" id="bcat"></section>

<section class="l8-sobre" id="sobre"><div class="l8w">
  <div class="l8-sobre-g">
    <div class="l8-sobre-img"><img src="/img/colagem-1.jpg" alt="" loading="lazy"><img src="/img/colagem-2.jpg" alt="" loading="lazy"><img src="/img/colagem-3.jpg" alt="" loading="lazy"><img src="/img/colagem-4.jpg" alt="" loading="lazy"></div>
    <div class="l8-sobre-tx"><h2>ALTA PERFUMARIA ORIGINAL</h2>
      <p>A Nota Perfumaria nasceu para vender alta perfumaria árabe e importada do jeito que a gente gostaria de comprar: sem mistério sobre o produto, sem pressão e com alguém do outro lado que conhece cada fragrância da coleção.</p>
      <p>Trabalhamos só com frascos originais e lacrados, das casas mais respeitadas do Oriente Médio e da perfumaria internacional, e acompanhamos o seu pedido do pagamento até a entrega.</p>
      <a href="#" data-pol="originalidade">Conheça nossa garantia de originalidade</a></div>
  </div>
  <div class="l8-stamps">
    {stamp(['100% originais', 'lacrados'], '100% originais', 'Lacrados, com selo do importador', ST_ICONS[0])}
    {stamp(['pagamento seguro', 'asaas'], 'Pagamento seguro', 'Processado pelo Asaas', ST_ICONS[1])}
    {stamp(['entrega rastreada', 'correios'], 'Entrega rastreada', 'Para todo o Brasil', ST_ICONS[2])}
    {stamp(['atendimento humano', 'whatsapp'], 'Atendimento humano', 'Especialista no WhatsApp', ST_ICONS[3])}
  </div>
</div></section>

<section class="l8-faq" id="faq"><div class="l8-faq-in">
  <h2>PERGUNTAS FREQUENTES</h2>
{faq_block}</div></section>

<section class="l8-insta"><a href="https://instagram.com/notaperfumaria" target="_blank" rel="noopener">{ICON['insta']}<span>Siga-nos no Instagram</span><b>@notaperfumaria</b></a></section>

<section class="l8-news"><div class="l8-news-in">
  <div class="l8-news-img"><img src="/img/capa.jpg" alt="" loading="lazy"></div>
  <div class="l8-news-tx"><h2>PERFUMES QUE ASSINAM CADA MOMENTO</h2><p>Receba lançamentos, ofertas e indicações exclusivas.</p></div>
  <form class="l8-news-f" id="nform"><label>Nome completo*<input id="nnome" type="text" placeholder="Digite seu nome" autocomplete="name"></label><label>E-mail*<input id="nemail" type="email" placeholder="Ex: exemplo@email.com" autocomplete="email"></label><button type="submit">CADASTRAR</button><p id="nmsg"></p></form>
</div></section>
</main>

<section class="l8-lista" id="colecoes"><div class="l8w">
  <p class="l8-crumb" id="cat-crumb"><a href="/" data-cat="all">Início</a> › <span id="cat-crumb-n">Todos os perfumes</span></p>
  <div class="l8-lista-h"><h1 id="cat-title">Todos os perfumes</h1><p id="cat-sub">Mais de 350 fragrâncias originais, das casas árabes às grifes internacionais</p></div>
  <div class="l8-lista-bar">
    <div class="l8-chips" id="tabs"><button class="tab on" data-f="all">Todos</button><button class="tab" data-f="M">Masculinos</button><button class="tab" data-f="F">Femininos</button><button class="tab" data-f="U">Unissex</button><button class="tab" data-f="arabe">Árabes</button><button class="tab" data-f="import">Importados</button><button class="tab" data-f="splash">Body splash</button><button class="tab" data-f="kit">Kits</button></div>
    <div class="l8-filt"><select id="brand" aria-label="Marca"><option value="">Todas as marcas</option></select><select id="range" aria-label="Faixa de preço"><option value="">Qualquer preço</option><option value="0-100">Até R$ 99</option><option value="100-200">R$ 100 a 199</option><option value="200-9999">Acima de R$ 200</option></select><select id="sort" aria-label="Ordenar"><option value="brand">Ordenar: destaques</option><option value="asc">Menor preço</option><option value="desc">Maior preço</option><option value="az">A–Z</option></select><span class="count" id="count"></span></div>
  </div>
  <div class="l8-grid" id="grid"></div>
  <div class="l8-more" id="more"></div>
</div></section>

<section class="l8-quiz" id="assinatura"><div class="l8w">
{quiz_inner}</div></section>

<div id="politicas" hidden>
{pol_block}</div>

<footer class="l8-foot"><div class="l8w">
  <div class="l8-foot-top">
    <div class="l8-foot-brand"><img src="/img/logo.jpg?v=2" alt="Nota Perfumaria" loading="lazy"><p>Somos a Nota Perfumaria, curadoria de alta perfumaria árabe e importada. Só frascos originais e lacrados, com atendimento humano do primeiro contato ao pós-venda.</p>
      <h6>ACOMPANHE A NOTA</h6><div class="l8-soc"><a href="https://instagram.com/notaperfumaria" target="_blank" rel="noopener" aria-label="Instagram">{ICON['insta']}</a><a href="https://wa.me/5511982659792" target="_blank" rel="noopener" aria-label="WhatsApp">{ICON['wa']}</a></div></div>
    <div><h6>INSTITUCIONAL</h6><a href="/" data-cat="all">Início</a><a href="#" data-pol="originalidade">Sobre a Nota</a><a href="#assinatura" data-modo="quiz">Descubra o seu perfume ideal</a><a href="#faq" data-jump="faq">Perguntas frequentes</a></div>
    <div><h6>SUPORTE</h6><a href="#" data-pol="pagamento">Pagamentos e aprovações</a><a href="#" data-pol="prazos">Prazos e entregas</a><a href="#" data-pol="rastreio">Rastreie o seu pedido</a><a href="#" data-pol="trocas">Trocas e devoluções</a><a href="#" data-pol="privacidade">Privacidade (LGPD)</a><a href="#" data-pol="contato">Contato</a></div>
    <div><h6>ATENDIMENTO PELO WHATSAPP</h6><p class="l8-foot-note">{ICON['wa']} <span id="f-wa">(11) 98265-9792</span></p><p class="l8-foot-note">Segunda a sábado, das 9h às 18h.</p><p class="l8-foot-note">Loja 100% online, envio para todo o Brasil.</p>
      <h6 style="margin-top:22px">SEGURANÇA</h6><div class="l8-seals"><span>{ICON['lock']} SSL</span><span>Asaas</span><span>PIX</span><span>12x</span></div></div>
  </div>
  <div class="l8-foot-cats"><p class="l8-foot-sep"><span>TODAS AS CATEGORIAS</span></p>
    <div class="l8-foot-cols">
      <div><h6>PRODUTOS</h6><a href="/c/masculinos" data-cat="masculinos">Perfumes masculinos</a><a href="/c/femininos" data-cat="femininos">Perfumes femininos</a><a href="/c/unissex" data-cat="unissex">Perfumes unissex</a><a href="/c/kits" data-cat="kits">Para presente</a><a href="/c/arabes" data-cat="arabes">Perfumes árabes</a></div>
      <div><h6>LINHAS</h6><a href="/c/importados" data-cat="importados">Importados & grifes</a><a href="/c/body-splash" data-cat="body-splash">Body splash</a><a href="/c/ofertas" data-cat="ofertas">Ofertas</a><a href="/c/mais-desejados" data-cat="mais-desejados">Mais desejados</a></div>
      <div><h6>OCASIÕES</h6><a href="/c/romantico-masculino" data-cat="romantico-masculino">Ocasiões perfumes masculinos</a><a href="/c/romantico-feminino" data-cat="romantico-feminino">Ocasiões perfumes femininos</a></div>
      <div><h6>FAMÍLIAS OLFATIVAS</h6><a href="/c/fresco" data-cat="fresco">Perfume cítrico</a><a href="/c/amadeirado" data-cat="amadeirado">Perfume amadeirado</a><a href="/c/doce" data-cat="doce">Perfume doce</a><a href="/c/floral" data-cat="floral">Perfume floral</a><a href="/c/oriental" data-cat="oriental">Perfume oriental</a></div>
    </div></div>
  <div class="l8-copy"><span>© 2026 Nota Perfumaria. Todos os direitos reservados. Preços sujeitos a alteração; vale o valor exibido na confirmação do pedido.</span><span>Pagamentos: Asaas · Envios: Correios</span></div>
</div></footer>

{pv_modal}<div class="fab"><a id="fab-wa" href="https://wa.me/5511982659792" target="_blank" rel="noopener" aria-label="WhatsApp">{ICON['wa']}</a></div>

{script_main}
<script>
/* ===== layout LAB 8: modos, carrosséis, slider, ticker ===== */
(function(){{
  const $=s=>document.querySelector(s), $$=s=>[...document.querySelectorAll(s)];
  // slider
  let si=0;const sl=$$('#slides .l8-slide'),dots=$$('#dots i');
  function go(n){{si=(n+sl.length)%sl.length;sl.forEach((e,k)=>e.classList.toggle('on',k===si));dots.forEach((e,k)=>e.classList.toggle('on',k===si))}}
  $$('[data-slide]').forEach(b=>b.onclick=e=>{{e.preventDefault();go(si+ +b.dataset.slide);clearInterval(T);T=setInterval(()=>go(si+1),6000)}});
  dots.forEach((d,k)=>d.onclick=()=>go(k));let T=setInterval(()=>go(si+1),6000);
  // adbar
  let ai=0;const am=$$('#ad-msgs span');function ad(n){{ai=(n+am.length)%am.length;am.forEach((e,k)=>e.classList.toggle('on',k===ai))}}
  $$('[data-ad]').forEach(b=>b.onclick=()=>ad(ai+ +b.dataset.ad));setInterval(()=>ad(ai+1),5000);
  // carrosséis
  document.addEventListener('click',e=>{{const b=e.target.closest('[data-car]');if(!b)return;const sec=b.closest('section');const tr=sec&&sec.querySelector('.l8-track');if(tr)tr.scrollBy({{left:(+b.dataset.car)*tr.clientWidth*.8,behavior:'smooth'}})}});
  // menu mobile
  $('#burger').onclick=()=>document.body.classList.toggle('nav-open');
  document.addEventListener('click',e=>{{const j=e.target.closest('[data-jump]');if(j){{e.preventDefault();window.setModo('home');document.body.classList.remove('nav-open');const t=document.getElementById(j.dataset.jump);if(t)setTimeout(()=>t.scrollIntoView({{behavior:'smooth'}}),30);return}}
    const m=e.target.closest('[data-modo]');if(m){{e.preventDefault();document.body.classList.remove('nav-open');window.setModo(m.dataset.modo);scrollTo({{top:0,behavior:'smooth'}})}}
    if(e.target.closest('#nav a[data-cat]'))document.body.classList.remove('nav-open');}});
}})();
</script>
</body>
</html>
'''

CSS = r"""
/* =================== LAB 8 layout =================== */
section.l8-hero,section.l8-ticker,section.l8-bcat,section.l8-marca,section.l8-news,section.l8-info{padding-block:0}
section.l8-info{padding:20px 0}
:root{--l8:'Plus Jakarta Sans',system-ui,-apple-system,'Segoe UI',sans-serif;--l8-ink:#111;--l8-mut:#424242;--l8-g:#f2f2f2;--l8-badge:#d9d6f2;--l8-pad:64px}
html{scroll-behavior:smooth}
body{font-family:var(--l8)!important;background:#fff!important;color:#111!important;font-size:14px}
body::before{display:none}
h1,h2,h3,h4,h5,h6{font-family:var(--l8)!important}
.sr{position:absolute;width:1px;height:1px;overflow:hidden;clip:rect(0 0 0 0)}
.l8w{max-width:1366px;margin:0 auto;padding:0 var(--l8-pad)}
@media(max-width:900px){:root{--l8-pad:16px}}
/* adbar */
.l8-adbar{background:#000;color:#fff;font-size:12px;height:40px}
.l8-adbar-in{display:grid;grid-template-columns:24px 1fr 24px;align-items:center;height:40px;position:relative;max-width:1366px}
.l8-ad-arr{background:none;border:0;color:#fff;padding:0;display:grid;place-items:center}.l8-ad-arr svg{width:14px;height:14px}
.l8-ad-msgs{position:relative;height:20px;text-align:center}
.l8-ad-msgs span{position:absolute;inset:0;display:flex;align-items:center;justify-content:center;gap:6px;opacity:0;transition:opacity .4s}
.l8-ad-msgs span.on{opacity:1}.l8-ad-msgs svg{width:15px;height:15px}
.l8-ad-links{position:absolute;right:var(--l8-pad);top:0;height:40px;display:flex;align-items:center;gap:6px;letter-spacing:.04em}
.l8-ad-links a{color:#fff;text-decoration:none}.l8-ad-links a:hover{text-decoration:underline}
@media(min-width:901px){.l8-adbar-in{grid-template-columns:24px 360px 24px;justify-content:start;padding-left:calc(50% - 204px)}}
@media(max-width:900px){.l8-ad-links{display:none}}
/* header */
.l8-head{position:sticky;top:0;z-index:30;background:#fff;border-bottom:1px solid #ececec}
.l8-head-in{display:flex;align-items:center;gap:26px;height:72px}
.l8-logo img{height:46px;width:auto;display:block}
.l8-nav{display:flex;align-items:center;gap:26px;font-size:12.5px;font-weight:500;letter-spacing:.02em;flex:1;height:100%}
.l8-nav>a,.l8-dd>a{color:#111;text-decoration:none;white-space:nowrap;display:flex;align-items:center;height:72px;border-bottom:2px solid transparent}
.l8-nav>a:hover,.l8-dd:hover>a,.l8-nav a.on{border-bottom-color:#111}
.l8-dd{position:static;height:100%}
.l8-dd-box{display:none;position:absolute;left:0;right:0;top:72px;background:#fff;border-top:1px solid #ececec;box-shadow:0 18px 40px rgba(0,0,0,.08);padding:28px 0 32px;z-index:40}
.l8-dd:hover .l8-dd-box,.l8-dd:focus-within .l8-dd-box{display:block}
.l8-dd-cols{max-width:1366px;margin:0 auto;padding:0 var(--l8-pad);display:flex;gap:64px}
.l8-dd-cols h5{font-size:12px;font-weight:700;letter-spacing:.08em;text-transform:uppercase;margin:0 0 12px;color:#111}
.l8-dd-cols a{display:block;color:#424242;text-decoration:none;padding:5px 0;font-size:14px;font-weight:400;letter-spacing:0}
.l8-dd-cols a:hover{color:#000;text-decoration:underline}
.l8-dd-marcas{display:grid;grid-template-columns:repeat(5,1fr);gap:0 32px}
.l8-search{display:flex;align-items:center;border-bottom:1px solid #111;width:230px;margin-left:auto}
.l8-search input{flex:1;border:0;background:transparent;font:inherit;font-size:13px;padding:6px 0;min-width:0;color:#111}
.l8-search input::placeholder{color:#777}
.l8-search button{background:none;border:0;padding:0 0 0 8px;color:#111;display:grid}.l8-search svg{width:20px;height:20px}
.l8-ic{background:none;border:0;padding:0;color:#111;position:relative;display:grid;place-items:center}.l8-ic svg{width:24px;height:24px}
.l8-cq{position:absolute;top:-6px;right:-7px;background:#111;color:#fff;font-size:10px;min-width:16px;height:16px;border-radius:99px;display:grid;place-items:center;padding:0 3px;font-weight:600}
.l8-burger{display:none;background:none;border:0;padding:0;color:#111}.l8-burger svg{width:24px;height:24px}
@media(max-width:1180px){.l8-nav{gap:16px;font-size:11.5px}.l8-search{width:160px}}
@media(max-width:1000px){
  .l8-burger{display:grid}.l8-head-in{gap:14px;height:64px}.l8-logo{margin-right:auto}.l8-logo img{height:38px}
  .l8-search{order:5;width:100%;margin:0 0 10px}.l8-head-in{flex-wrap:wrap;height:auto;padding-top:10px}
  .l8-nav{display:none;position:fixed;inset:0 20% 0 0;background:#fff;z-index:60;flex-direction:column;align-items:stretch;gap:0;padding:70px 24px 24px;overflow:auto;height:auto;box-shadow:0 0 0 100vmax rgba(0,0,0,.4)}
  body.nav-open .l8-nav{display:flex}
  .l8-nav>a,.l8-dd>a{height:auto;padding:14px 0;border-bottom:1px solid #eee;font-size:14px}
  .l8-dd-box{display:block;position:static;box-shadow:none;border:0;padding:4px 0 10px}
  .l8-dd-cols{padding:0;flex-direction:column;gap:10px}.l8-dd-marcas{grid-template-columns:1fr 1fr}
}
/* hero */
.l8-hero{position:relative;background:#0a0a0a;overflow:hidden}
.l8-slides{position:relative;height:clamp(420px,46vw,629px)}
.l8-slide{position:absolute;inset:0;opacity:0;transition:opacity .7s;background:var(--img) center/cover no-repeat #0a0a0a;color:#fff;text-decoration:none;display:flex;align-items:center}
.l8-slide.on{opacity:1;z-index:1}
.l8-slide-tx{width:min(44%,520px);display:flex;flex-direction:column;gap:14px}
.l8-slide-tx.right{margin-left:auto;margin-right:6%;text-align:left}
.l8-slide-tx.left{margin-left:var(--l8-pad)}
.l8-slide-tx p{font-size:12px;letter-spacing:.3em;color:#d9b25a;font-weight:600;margin:0}
.l8-slide-tx h2{font-size:clamp(2rem,4vw,3.6rem);line-height:1.04;font-weight:700;margin:0;color:#fff;text-transform:uppercase}
.l8-slide-tx h2 em{font-style:normal;color:#e7c66f}
.l8-slide-tx span{font-size:1.05rem;color:#ddd;max-width:40ch}
.l8-slide-tx b{align-self:flex-start;margin-top:8px;background:#fff;color:#111;border-radius:999px;padding:12px 26px;font-size:12px;letter-spacing:.08em;font-weight:600}
.l8-slide-split{background:radial-gradient(900px 500px at 25% 50%,#2a2114,#0a0a0a 70%)}
.l8-slide-split img{position:absolute;right:0;top:0;height:100%;width:46%;object-fit:cover;object-position:50% 20%;-webkit-mask-image:linear-gradient(90deg,transparent,#000 30%);mask-image:linear-gradient(90deg,transparent,#000 30%)}
.l8-hero-arr{position:absolute;top:50%;transform:translateY(-50%);z-index:3;width:40px;height:40px;border-radius:50%;border:0;background:rgba(255,255,255,.85);color:#111;display:grid;place-items:center}
.l8-hero-arr svg{width:18px;height:18px}.l8-hero-arr.prev{left:20px}.l8-hero-arr.next{right:20px}
.l8-dots{position:absolute;bottom:16px;left:0;right:0;display:flex;justify-content:center;gap:8px;z-index:3}
.l8-dots i{width:8px;height:8px;border-radius:50%;background:rgba(255,255,255,.45);cursor:pointer}.l8-dots i.on{background:#fff}
@media(max-width:760px){.l8-slides{height:560px}.l8-slide{align-items:flex-end;background-position:30% center}.l8-slide-tx,.l8-slide-tx.right,.l8-slide-tx.left{width:auto;margin:0 16px 56px;padding:22px;background:rgba(0,0,0,.55);border-radius:14px;backdrop-filter:blur(4px)}.l8-slide-split img{width:100%;-webkit-mask-image:none;mask-image:none;opacity:.55}.l8-hero-arr{display:none}}
/* ticker */
.l8-ticker{background:#000;color:#fff;height:50px;overflow:hidden;display:flex;align-items:center;white-space:nowrap}
.l8-ticker-track{display:inline-flex;animation:l8mq 38s linear infinite}
.l8-ticker-track span{display:inline-flex;align-items:center;gap:0;padding-right:0}
.l8-ticker-track em{font-style:normal;font-size:14px;padding:0 22px}.l8-ticker-track em b{font-weight:700}
.l8-ticker-track i{font-style:normal;font-size:16px}
@keyframes l8mq{to{transform:translateX(-50%)}}
@media(prefers-reduced-motion:reduce){.l8-ticker-track{animation:none}}
/* info */
.l8-info{background:#fff;padding:20px 0}
.l8-info-in{display:flex;justify-content:center;gap:64px;flex-wrap:wrap}
.l8-info-in>div{display:flex;align-items:center;gap:12px}
.l8-info-in svg{width:30px;height:30px;color:#111;flex:none}
.l8-info-in b{display:block;font-size:14px;font-weight:600}.l8-info-in span{font-size:13px;color:#424242}
@media(max-width:760px){.l8-info-in{gap:14px;justify-content:flex-start;flex-direction:column}}
/* showcase */
.l8-show{padding:56px 0}
.l8-show-h{display:flex;align-items:flex-end;gap:28px;margin-bottom:22px;flex-wrap:wrap}
.l8-show-h h2{font-size:32px;font-weight:400;text-transform:uppercase;margin:0;line-height:1.15;color:#000;letter-spacing:-.01em}
.l8-all{font-size:13px;color:#111;text-decoration:underline;text-underline-offset:3px;margin-bottom:6px}
.l8-tabs{display:flex;border-bottom:1px solid #111}
.l8-tabs button{background:transparent;border:0;padding:12px 24px;font:inherit;font-size:14px;letter-spacing:.02em;color:#000;cursor:pointer}
.l8-tabs button.on{background:#000;color:#fff}
.l8-arrs{margin-left:auto;display:flex;gap:10px}
.l8-arrs button{width:34px;height:34px;border-radius:50%;border:1px solid #bdbdbd;background:#fff;color:#111;display:grid;place-items:center;cursor:pointer}
.l8-arrs button:last-child{border-color:#111}.l8-arrs svg{width:15px;height:15px}
.l8-track{display:grid;grid-auto-flow:column;grid-auto-columns:calc((100% - 4*24px)/4.6);gap:24px;overflow-x:auto;scroll-snap-type:x mandatory;scrollbar-width:none;padding-bottom:4px}
.l8-track::-webkit-scrollbar{display:none}
.l8-track>*{scroll-snap-align:start}
@media(max-width:1000px){.l8-track{grid-auto-columns:calc((100% - 16px)/2.3);gap:16px}.l8-show-h h2{font-size:24px}.l8-tabs{order:5;width:100%;overflow-x:auto}.l8-tabs button{padding:10px 16px;font-size:13px;white-space:nowrap}}
@media(max-width:560px){.l8-track{grid-auto-columns:calc((100% - 12px)/1.7);gap:12px}.l8-show{padding:40px 0}}
/* card */
.l8-card{min-width:0;display:flex;flex-direction:column;color:#111}
.l8-card-ph{position:relative;aspect-ratio:3/4;border-radius:12px;overflow:hidden;background:#f2f2f2;cursor:pointer}
.l8-card-ph img{width:100%;height:100%;object-fit:contain;padding:9% 6% 16%;mix-blend-mode:multiply;filter:brightness(1.07) contrast(1.03);transition:transform .5s}
.l8-card:hover .l8-card-ph img{transform:scale(1.04)}
.l8-card-ph .l8-ph0{position:absolute;inset:0;display:grid;place-items:center}.l8-card-ph .l8-ph0 svg{width:46%;opacity:.85}
.l8-card-btns{position:absolute;left:10px;right:10px;bottom:10px;display:flex;justify-content:space-between;z-index:2}
.l8-card-btns button,.l8-card-btns a{height:28px;min-width:44px;border-radius:999px;display:grid;place-items:center;border:1.5px solid #000;cursor:pointer;padding:0 12px}
.l8-card-btns .v{background:#fff;color:#111;border-color:#fff}.l8-card-btns .a{background:#000;color:#fff}
.l8-card-btns svg{width:17px;height:17px}
.l8-card-g{position:absolute;top:10px;left:10px;font-size:10px;letter-spacing:.08em;text-transform:uppercase;background:rgba(255,255,255,.9);border-radius:99px;padding:4px 9px;color:#424242}
.l8-card-b{padding:14px 10px 0;display:flex;flex-direction:column;gap:4px}
.l8-card-top{display:flex;gap:10px;align-items:flex-start;justify-content:space-between}
.l8-card-n{font-size:15px;line-height:1.35;color:#11131d;text-decoration:none;display:-webkit-box;-webkit-line-clamp:3;-webkit-box-orient:vertical;overflow:hidden}
.l8-card-n:hover{text-decoration:underline}
.l8-badge{flex:none;background:var(--l8-badge);color:#2a2560;font-size:11px;font-weight:700;border-radius:6px;padding:5px 7px;text-transform:uppercase;white-space:nowrap}
.l8-card-brand{font-size:12px;color:#777;letter-spacing:.02em}
.l8-cmp{font-size:14px;font-weight:500;color:#424242;text-decoration:line-through;margin-top:8px}
.l8-pr{font-size:20px;font-weight:700;color:#000;margin-top:2px}.l8-pr small{font-size:12px;font-weight:500;color:#424242;margin-left:4px}
.l8-ins{font-size:13px;color:#424242}
/* ocasiões */
.l8-oc{padding:56px 0}
.l8-oc-in{display:grid;grid-template-columns:240px 1fr;gap:40px;align-items:center}
.l8-oc-side h2{font-size:32px;font-weight:400;line-height:1.1;margin:0 0 24px;color:#000;text-transform:uppercase}
.l8-pill{display:block;width:240px;height:38px;border-radius:999px;border:1px solid #000;background:transparent;color:#000;font:inherit;font-size:11px;font-weight:500;letter-spacing:.08em;margin-bottom:12px;cursor:pointer}
.l8-pill.on{background:#000;color:#fff}
.l8-oc-wrap{position:relative;min-width:0}
.l8-oc-track{grid-auto-columns:calc((100% - 2*16px)/3);gap:16px}
.l8-oc-card{position:relative;display:block;height:348px;border-radius:12px;overflow:hidden;background:#f2f2f2;color:#fff;text-decoration:none;isolation:isolate}
.l8-oc-card .bg{position:absolute;inset:0;z-index:-2}
.l8-oc-card img{position:absolute;left:50%;top:44%;transform:translate(-50%,-50%);height:66%;width:auto;mix-blend-mode:multiply;filter:brightness(1.07) contrast(1.03);z-index:-1;transition:transform .5s}
.l8-oc-card:hover img{transform:translate(-50%,-52%) scale(1.04)}
.l8-oc-card::after{content:"";position:absolute;inset:auto 0 0 0;height:55%;background:linear-gradient(180deg,transparent,rgba(0,0,0,.78));z-index:-1}
.l8-oc-card .tx{position:absolute;left:0;right:0;bottom:22px;text-align:center}
.l8-oc-card b{display:block;font-size:20px;font-weight:400;margin-bottom:14px}
.l8-oc-card em{font-style:normal;display:inline-block;border:1px solid #fff;border-radius:99px;padding:9px 22px;font-size:11px;letter-spacing:.08em}
.l8-oc-arr{position:absolute;top:50%;transform:translateY(-50%);width:36px;height:36px;border-radius:50%;border:0;background:#fff;color:#111;box-shadow:0 2px 10px rgba(0,0,0,.15);display:grid;place-items:center;z-index:2}
.l8-oc-arr svg{width:15px;height:15px}.l8-oc-arr.prev{left:-12px}.l8-oc-arr.next{right:-12px}
@media(max-width:900px){.l8-oc-in{grid-template-columns:1fr;gap:18px}.l8-oc-side h2{font-size:24px}.l8-oc-side{display:flex;flex-wrap:wrap;gap:8px}.l8-oc-side h2{width:100%;margin-bottom:6px}.l8-pill{width:auto;padding:0 16px;margin:0}.l8-oc-track{grid-auto-columns:72%}.l8-oc-arr{display:none}}
/* famílias */
.l8-fam{padding:24px 0 56px}
.l8-fam h2{font-size:32px;font-weight:400;margin:0 0 22px;color:#000}
.l8-fam-row{display:flex;gap:10px;overflow-x:auto;scrollbar-width:none}
.l8-fam-it{flex:0 0 158px;text-decoration:none;color:#111;text-align:center}
.l8-fam-it span{display:block;font-size:13px;margin-bottom:8px}
.l8-fam-media{height:222px;border-radius:12px;overflow:hidden;-webkit-mask:radial-gradient(circle 14px at 0 50%,transparent 98%,#000) left/51% 100% no-repeat,radial-gradient(circle 14px at 100% 50%,transparent 98%,#000) right/51% 100% no-repeat;mask:radial-gradient(circle 14px at 0 50%,transparent 98%,#000) left/51% 100% no-repeat,radial-gradient(circle 14px at 100% 50%,transparent 98%,#000) right/51% 100% no-repeat;transition:transform .3s}
.l8-fam-media svg{width:100%;height:100%;display:block}
.l8-fam-it:hover .l8-fam-media{transform:translateY(-4px)}
@media(max-width:760px){.l8-fam h2{font-size:24px}.l8-fam-it{flex-basis:130px}.l8-fam-media{height:182px}}
/* marca destaque */
.l8-marca{background:#0b1013;color:#fff}
.l8-marca-in{display:grid;grid-template-columns:50% 50%;max-width:1366px;margin:0 auto;padding:24px 0 72px}
.l8-marca-img{height:620px;overflow:hidden}.l8-marca-img img{width:100%;height:100%;object-fit:cover;object-position:50% 25%}
.l8-marca-r{padding:22px var(--l8-pad) 0 40px;min-width:0}
.l8-show-h.dark h2{color:#fff}.l8-show-h.dark .l8-all{color:#fff}
.l8-show-h.dark .l8-arrs button{background:transparent;color:#fff;border-color:#555}.l8-show-h.dark .l8-arrs button:last-child{border-color:#fff}
.l8-marca .l8-track{grid-auto-columns:calc((100% - 32px)/2.15);gap:32px}
.l8-marca .l8-card{background:#fff;border-radius:6px;overflow:hidden;padding-bottom:14px}
.l8-marca .l8-card-ph{border-radius:0;aspect-ratio:1/1}
@media(max-width:900px){.l8-marca-in{grid-template-columns:1fr;padding:0 0 40px}.l8-marca-img{height:300px}.l8-marca-r{padding:24px 16px 0}.l8-marca .l8-track{grid-auto-columns:62%;gap:14px}}
/* banners categoria */
.l8-bcat{display:grid;grid-template-columns:repeat(3,1fr)}
.l8-bcat a{position:relative;height:455px;display:flex;flex-direction:column;align-items:center;justify-content:flex-end;padding-bottom:42px;color:#fff;text-decoration:none;overflow:hidden;isolation:isolate}
.l8-bcat a img{position:absolute;left:50%;top:42%;height:64%;transform:translate(-50%,-50%);mix-blend-mode:multiply;filter:brightness(1.07) contrast(1.03);z-index:-1;transition:transform .6s}
.l8-bcat a:hover img{transform:translate(-50%,-50%) scale(1.05)}
.l8-bcat a::after{content:"";position:absolute;inset:0;background:linear-gradient(180deg,transparent 45%,rgba(0,0,0,.72));z-index:-1}
.l8-bcat b{font-size:36px;font-weight:400;letter-spacing:.02em}.l8-bcat span{font-size:14px;font-weight:600;text-decoration:underline;margin-top:4px}
@media(max-width:760px){.l8-bcat{grid-template-columns:1fr}.l8-bcat a{height:300px}.l8-bcat b{font-size:28px}}
/* sobre */
.l8-sobre{padding:72px 0 40px}
.l8-sobre-g{display:grid;grid-template-columns:1fr 1.1fr;gap:72px;align-items:center;max-width:1100px;margin:0 auto}
.l8-sobre-img{display:grid;grid-template-columns:1fr 1fr;gap:10px;border-radius:28px;overflow:hidden}
.l8-sobre-img img{width:100%;aspect-ratio:1;object-fit:cover;display:block}
.l8-sobre-tx h2{font-size:clamp(2rem,3.4vw,3rem);font-weight:400;line-height:1.08;margin:0 0 22px;color:#000}
.l8-sobre-tx p{font-size:15px;line-height:1.6;color:#111;margin:0 0 16px;max-width:52ch}
.l8-sobre-tx a{font-weight:700;color:#111;text-decoration:underline;text-underline-offset:3px}
.l8-stamps{display:grid;grid-template-columns:repeat(4,1fr);gap:24px;max-width:1100px;margin:64px auto 0;text-align:center}
.l8-stamp svg{width:96px;height:96px;display:block;margin:0 auto 12px}
.l8-stamp b{display:block;font-size:14px;font-weight:700}.l8-stamp span{font-size:13px;color:#424242}
@media(max-width:860px){.l8-sobre-g{grid-template-columns:1fr;gap:28px}.l8-stamps{grid-template-columns:1fr 1fr;gap:28px 12px;margin-top:40px}}
/* faq */
.l8-faq{background:#f2f2f2;padding:64px 20px}
.l8-faq-in{max-width:740px;margin:0 auto}
.l8-faq h2{text-align:center;font-size:28px;font-weight:400;margin:0 0 28px;color:#000}
.l8-faq details{border-bottom:1px solid #cfcfcf}
.l8-faq summary{list-style:none;cursor:pointer;display:flex;justify-content:space-between;align-items:center;gap:16px;padding:18px 0;font-size:14px;font-weight:600;color:#111;font-family:var(--l8)}
.l8-faq summary::-webkit-details-marker{display:none}
.l8-faq summary::after{content:"+";font-size:24px;font-weight:300;color:#111;transition:transform .2s;line-height:1}
.l8-faq details[open] summary::after{transform:rotate(45deg)}
.l8-faq details p{padding:0 0 18px;margin:0;color:#424242;line-height:1.6;font-size:14px}
.l8-faq details a{color:#111}
/* insta */
.l8-insta{background:#000;color:#fff;padding:52px var(--l8-pad)}
.l8-insta a{color:#fff;text-decoration:none;display:inline-flex;flex-direction:column;align-items:center;gap:4px;margin-left:calc((100% - min(100%,1238px))/2)}
.l8-insta svg{width:30px;height:30px}.l8-insta span{font-size:11px}.l8-insta b{font-size:18px}
/* newsletter */
.l8-news{background:linear-gradient(90deg,#000,#1a1a1a 50%,#000);color:#fff;overflow:hidden}
.l8-news-in{display:grid;grid-template-columns:28% 1fr 300px;gap:40px;align-items:center;max-width:1366px;margin:0 auto;padding-right:var(--l8-pad);min-height:300px}
.l8-news-img{height:300px}.l8-news-img img{width:100%;height:100%;object-fit:cover;object-position:18% 50%;-webkit-mask-image:linear-gradient(90deg,#000 55%,transparent);mask-image:linear-gradient(90deg,#000 55%,transparent)}
.l8-news-tx h2{font-size:26px;font-weight:400;line-height:1.2;margin:0 0 10px;color:#fff}.l8-news-tx p{font-size:14px;color:#ddd;margin:0}
.l8-news-f{display:flex;flex-direction:column;gap:12px}
.l8-news-f label{display:block;border:1px solid #888;border-radius:99px;padding:6px 18px;font-size:10px;color:#ddd}
.l8-news-f input{display:block;width:100%;background:transparent;border:0;color:#fff;font:inherit;font-size:13px;padding:2px 0;outline:0}
.l8-news-f input::placeholder{color:#888}
.l8-news-f button{height:44px;border-radius:99px;border:0;background:#fff;color:#111;font:inherit;font-weight:700;font-size:13px;letter-spacing:.04em;cursor:pointer}
.l8-news-f p{font-size:12px;color:#ccc;margin:0;min-height:1em}
@media(max-width:900px){.l8-news-in{grid-template-columns:1fr;padding:0 16px 36px;gap:20px}.l8-news-img{height:180px;margin:0 -16px}}
/* footer */
.l8-foot{background:#000;color:#fff;padding:56px 0 32px;font-size:14px}
.l8-foot h6{font-size:12px;font-weight:500;letter-spacing:.08em;margin:0 0 16px;color:#fff}
.l8-foot a{display:block;color:#fff;text-decoration:none;font-size:14px;padding:5px 0}.l8-foot a:hover{text-decoration:underline}
.l8-foot-top{display:grid;grid-template-columns:1.3fr .9fr .9fr 1fr;gap:48px}
.l8-foot-brand img{height:64px;width:auto;margin-bottom:16px}
.l8-foot-brand p{font-size:13px;line-height:1.6;color:#e6e6e6;max-width:36ch;margin:0 0 26px}
.l8-soc{display:flex;gap:10px}.l8-soc a{width:34px;height:34px;border-radius:50%;background:#fff;color:#000;display:grid;place-items:center;padding:0}.l8-soc svg{width:18px;height:18px}
.l8-foot-note{display:flex;gap:8px;align-items:flex-start;font-size:13px;color:#ddd;margin:0 0 10px}.l8-foot-note svg{width:16px;height:16px;flex:none;margin-top:1px}
.l8-seals{display:flex;gap:8px;flex-wrap:wrap}.l8-seals span{display:inline-flex;align-items:center;gap:4px;border:1px solid #444;border-radius:6px;padding:6px 10px;font-size:11px;font-weight:600;color:#ddd}.l8-seals svg{width:13px;height:13px}
.l8-foot-sep{display:flex;align-items:center;gap:14px;margin:44px 0 26px;font-size:11px;letter-spacing:.14em;color:#aaa}.l8-foot-sep::before,.l8-foot-sep::after{content:"";flex:1;height:1px;background:#333}
.l8-foot-cols{display:grid;grid-template-columns:repeat(4,1fr);gap:32px}
.l8-foot-cols a{font-size:13px;color:#ddd}
.l8-copy{display:flex;justify-content:space-between;gap:16px;flex-wrap:wrap;border-top:1px solid #222;margin-top:40px;padding-top:20px;font-size:11px;color:#999}
@media(max-width:900px){.l8-foot-top,.l8-foot-cols{grid-template-columns:1fr 1fr;gap:28px}.l8-foot-brand{grid-column:1/-1}}
/* lista (categorias / busca) */
.l8-lista{display:none;padding:28px 0 64px;min-height:60vh}
.l8-crumb{font-size:12px;color:#777;margin:0 0 18px}.l8-crumb a{color:#111}
.l8-lista-h h1{font-size:32px;font-weight:400;margin:0;color:#000;text-transform:uppercase}
.l8-lista-h p{color:#424242;margin:6px 0 0;font-size:14px}
.l8-lista-bar{display:flex;flex-wrap:wrap;gap:14px;align-items:center;justify-content:space-between;margin:24px 0 28px;padding-bottom:18px;border-bottom:1px solid #e6e6e6}
.l8-chips{display:flex;flex-wrap:wrap;gap:8px}
.l8-chips .tab{border:1px solid #111;background:#fff;color:#111;border-radius:999px;padding:8px 16px;font:inherit;font-size:12px;font-weight:500;letter-spacing:.04em;text-transform:uppercase;cursor:pointer}
.l8-chips .tab.on{background:#000;color:#fff}
.l8-filt{display:flex;gap:10px;align-items:center;flex-wrap:wrap}
.l8-filt select{border:1px solid #cfcfcf;border-radius:8px;padding:9px 12px;font:inherit;font-size:13px;background:#fff;color:#111}
.l8-filt .count{font-size:13px;color:#777}
.l8-grid{display:grid;grid-template-columns:repeat(4,1fr);gap:40px 24px}
@media(max-width:1000px){.l8-grid{grid-template-columns:repeat(3,1fr)}}
@media(max-width:700px){.l8-grid{grid-template-columns:1fr 1fr;gap:28px 12px}.l8-lista-h h1{font-size:24px}}
.l8-more{display:flex;justify-content:center;margin-top:40px}
.l8-more button{border:1px solid #111;background:#fff;color:#111;border-radius:999px;padding:12px 30px;font:inherit;font-size:13px;font-weight:600;cursor:pointer}
.l8-more button:hover{background:#111;color:#fff}
.empty{grid-column:1/-1;text-align:center;color:#777;padding:40px 0}
/* quiz */
.l8-quiz{display:none;padding:48px 0 72px;min-height:60vh}
.l8-quiz .sh h2{font-size:32px;font-weight:400;text-transform:uppercase;color:#000}
.l8-quiz .kick{color:#777!important;letter-spacing:.2em;font-size:11px}
.l8-quiz .rule{display:none}
.l8-quiz .chips button{border:1px solid #111!important;background:#fff!important;color:#111!important;border-radius:999px;font-size:13px}
.l8-quiz .chips button.on{background:#000!important;color:#fff!important}
.l8-quiz #qz-res{display:grid;grid-template-columns:repeat(4,1fr);gap:32px 24px;margin-top:30px}
@media(max-width:700px){.l8-quiz #qz-res{grid-template-columns:1fr 1fr;gap:24px 12px}}
/* modos */
body.modo-lista .l8-home,body.modo-quiz .l8-home{display:none}
body.modo-lista .l8-lista{display:block}
body.modo-quiz .l8-quiz{display:block}
body.pg-p .l8-hero,body.pg-p .l8-ticker{display:none}
/* modal do produto no padrão */
.pv-box{border-radius:14px!important;border:0!important}
.pv-info h3{font-family:var(--l8)!important;font-weight:500!important;font-size:1.7rem!important}
.pv .pix{color:#000!important}
.pv-info .acts a.buy,.pv-info .acts .buy{background:#000!important;color:#fff!important;border-radius:999px!important}
.pv-info .acts .ask{border-radius:999px!important}
.pv-info .add-cart{background:#fff!important;color:#000!important;border:1px solid #000!important;border-radius:999px!important}
.mx-box{border-radius:14px!important}.mx .go{border-radius:999px!important}
.fab{right:20px!important;bottom:20px!important}.fab a{background:#25d366!important}
.ssr-p{background:#fff!important;border:0!important}.ssr-i h1{font-family:var(--l8)!important;font-weight:500!important}
.ssr-i .acts a.buy{background:#000!important;color:#fff!important;border-radius:999px!important}
.ssr-i .pix{color:#000!important}
"""

head = head.replace('</head>', '<style>' + CSS + '</style>\n</head>', 1)
out = head + BODY

# ------------------------------------------------------------------ JS patches
def rep(old, new):
    global out
    assert old in out, 'JS não achei: ' + old[:80]
    out = out.replace(old, new, 1)

# ticker
rep("""{const items=(FRETE_GRATIS>0?[`Frete grátis acima de ${brl(FRETE_GRATIS)}`]:[]).concat(PROMO);const s='<span>'+items.map(t=>`<em>${t}</em>`).join('<i>◆</i>')+'</span>';$('#promo-track').innerHTML=s;}""",
    """{const items=(FRETE_GRATIS>0?[`<b>Frete grátis</b> acima de ${brl(FRETE_GRATIS)}`]:[]).concat(['<b>100% originais</b> e lacrados','<b>10% de desconto</b> no PIX','Parcelamento em até <b>12x</b> no cartão','<b>Entrega para todo o Brasil</b> com rastreio','<b>Atendimento humano</b> pelo WhatsApp']);const s='<span>'+items.map(t=>`<em>${t}</em><i>•</i>`).join('')+'</span>';$('#promo-track').innerHTML=s+s;}""")

# card
card_start = out.index('function card(it,o={}){')
card_end = out.index('const byName=', card_start)
out = out[:card_start] + r"""function card(it,o={}){
  const off=offPct(it);
  const badge=off?`${off}% OFF`:(it.p!=null?`${Math.round(PIX_OFF*100)}% PIX`:'');
  const price=it.p==null?`<div class="l8-pr">Consultar</div>`:`${off?`<div class="l8-cmp">${brl(it.po)}</div>`:''}<div class="l8-pr">${brl(pix(it.p))}<small>no PIX</small></div><div class="l8-ins">ou ${brl(it.p)} em até 12x no cartão</div>`;
  return `<div class="l8-card"><div class="l8-card-ph" data-open="${it.id}">${it.img?`<img src="${it.img}" alt="${it.b} ${it.n}" loading="lazy">`:`<div class="l8-ph0">${bottle}</div>`}<span class="l8-card-g">${G[it.g]}</span>
   <div class="l8-card-btns"><a class="v" href="/p/${it.slug}" data-open="${it.id}" aria-label="Ver detalhes">${'EYE'}</a>${it.p!=null?`<button class="a" type="button" data-add="${it.id}" aria-label="Adicionar à sacola">${'BAG'}</button>`:''}</div></div>
   <div class="l8-card-b"><div class="l8-card-top"><a class="l8-card-n" href="/p/${it.slug}" data-open="${it.id}">${it.n}</a>${badge?`<span class="l8-badge">${badge}</span>`:''}</div><div class="l8-card-brand">${it.b}</div>${price}</div></div>`;
}
""".replace("${'EYE'}", ICON['eye']).replace("${'BAG'}", ICON['bag']) + out[card_end:]

# renderFixos
rf_start = out.index('function renderFixos(){')
rf_end = out.index('renderFixos();', rf_start)
out = out[:rf_start] + r"""let ST='best',OCCG='masculino';
const comFoto=a=>a.filter(i=>i.img&&i.p!=null);
function lista(st){const best=ITEMS.some(i=>i.best)?ITEMS.filter(i=>i.best):BEST.map(byName).filter(Boolean);
  if(st==='best')return best;
  const pool=comFoto(ITEMS).filter(i=>!i.splash&&!i.kit&&(st==='arabe'?!i.imp:i.g===st));
  return [...best.filter(i=>pool.includes(i)),...pool.filter(i=>!best.includes(i))].slice(0,12)}
function renderST(){$('#best').innerHTML=lista(ST).map(i=>card(i)).join('');$('#best').scrollLeft=0;document.querySelectorAll('#st-tabs button').forEach(b=>b.classList.toggle('on',b.dataset.st===ST))}
const OCC_BG={romantico:'linear-gradient(160deg,#f6d6dc,#e7a9b7)',dia:'linear-gradient(160deg,#fff3d6,#f7d8a3)',noite:'linear-gradient(160deg,#cfd3ea,#8f96c4)',trabalho:'linear-gradient(160deg,#eceae6,#cfcac1)'};
const OCC_NOME={romantico:'Encontros Românticos',dia:'Dia',noite:'Noite',trabalho:'Trabalho'};
function renderOcc(){const g=OCCG==='masculino'?'M':'F';
  $('#occ-tiles').innerHTML=['romantico','dia','noite','trabalho'].map(k=>{const p=comFoto(ITEMS).filter(i=>(i.g===g||i.g==='U')&&OCC[k].f.includes(i.fam[0]));const it=p[k.length%Math.max(1,p.length)]||p[0];
    return `<a class="l8-oc-card" href="/c/${k}-${OCCG}" data-cat="${k}-${OCCG}"><span class="bg" style="background:${OCC_BG[k]}"></span>${it?`<img src="${it.img}" alt="" loading="lazy">`:''}<div class="tx"><b>${OCC_NOME[k]}</b><em>VER SELEÇÃO</em></div></a>`}).join('');
  document.querySelectorAll('[data-occg]').forEach(b=>b.classList.toggle('on',b.dataset.occg===OCCG))}
function renderFixos(){
  renderST();renderOcc();
  $('#sale').innerHTML=comFoto(ITEMS).filter(i=>(i.p<=149||i.po>i.p)&&!i.splash).sort((a,b)=>a.p-b.p).slice(0,12).map(i=>card(i)).join('');
  $('#marca-track').innerHTML=comFoto(ITEMS).filter(i=>i.b==='Lattafa').sort((a,b)=>(!!b.best-!!a.best)).slice(0,10).map(i=>card(i)).join('');
  $('#imp-track').innerHTML=comFoto(ITEMS).filter(i=>i.imp&&!i.splash).slice(0,12).map(i=>card(i)).join('');
  const pick=g=>{const b=comFoto(ITEMS).filter(i=>i.g===g&&!i.kit&&!i.splash);return (b.find(i=>i.best)||b[0]||{}).img||''};
  $('#bcat').innerHTML=[['M','MASCULINO','masculinos','linear-gradient(180deg,#e5e9ef,#b9c3cf)'],['F','FEMININO','femininos','linear-gradient(180deg,#f6e4e8,#e1b8c3)'],['U','UNISSEX','unissex','linear-gradient(180deg,#f2ece1,#d8c7a8)']].map(([g,t,c,bg])=>`<a href="/c/${c}" data-cat="${c}" style="background:${bg}"><img src="${pick(g)}" alt="" loading="lazy"><b>${t}</b><span>Explorar</span></a>`).join('');
  const marcas=[...new Set(ITEMS.map(i=>i.b))].sort((a,b)=>a.localeCompare(b));
  const sel=$('#brand'),cur=sel.value;sel.innerHTML='<option value="">Todas as marcas</option>'+marcas.map(b=>`<option>${b}</option>`).join('');sel.value=cur;
  $('#nav-marcas').innerHTML=marcas.map(b=>`<a href="/c/${slug(b)}" data-cat="${slug(b)}">${b}</a>`).join('');
}
document.addEventListener('click',e=>{const b=e.target.closest('[data-st]');if(b){ST=b.dataset.st;renderST();return}const o=e.target.closest('[data-occg]');if(o){OCCG=o.dataset.occg;renderOcc()}});
""" + out[rf_end:]

# categorias combinadas ocasião × gênero
rep("Object.keys(OCC).forEach(k=>CATS[k]={occ:k,t:OCC[k].t,s:OCC[k].s});",
    "Object.keys(OCC).forEach(k=>{CATS[k]={occ:k,t:OCC[k].t,s:OCC[k].s};[['masculino','M','masculinos'],['feminino','F','femininos']].forEach(([n,g,pl])=>CATS[k+'-'+n]={occ:k,f:g,t:OCC[k].t+' · perfumes '+pl,s:OCC[k].s})});")
rep("if(OCCF&&!OCC[OCCF].f.includes(i.fam[0]))return false;", "if(OCCF&&!OCC[OCCF].f.includes(i.fam[0]))return false;if(OCCF&&(f==='M'||f==='F')&&i.g==='U')return true;")
# passF: com OCC + gênero, aceitar unissex
rep("function passF(i){switch(f){case'M':case'F':case'U':return i.g===f;",
    "function passF(i){switch(f){case'M':case'F':return i.g===f||(!!OCCF&&i.g==='U');case'U':return i.g===f;")

# modos
rep("function setF(v,scroll){", """window.setModo=function(m){document.body.classList.toggle('modo-lista',m==='lista');document.body.classList.toggle('modo-quiz',m==='quiz');if(m==='quiz'){document.title='Descubra o seu perfume ideal · Nota Perfumaria';(function(){try{history.pushState(null,'','/#descubra')}catch(e){}})()}};
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
# popstate: volta pra home
rep("""if(location.pathname.startsWith('/c/'))setCat(location.pathname.slice(3),false,false);else setCat('all',false,false)}});""",
    """if(location.pathname.startsWith('/c/'))setCat(location.pathname.slice(3),false,false);else{setCat('all',false,false);setModo(location.hash==='#descubra'?'quiz':'home')}}});""")
# "ver mais"
rep("""`<button class="btn btn-ghost" id="morebtn">Carregar mais (${out.length-show.length})</button>`""", """`<button type="button" id="morebtn">Carregar mais (${out.length-show.length})</button>`""")
# políticas: abre em modal
rep("""const pol=t.closest('[data-pol]');if(pol){e.preventDefault();const d=document.getElementById('pol-'+pol.dataset.pol);if(d){d.open=true;d.scrollIntoView({behavior:'smooth',block:'start'});return}""",
    """const pol=t.closest('[data-pol]');if(pol){e.preventDefault();const d=document.getElementById('pol-'+pol.dataset.pol);if(d){const s=d.querySelector('summary').textContent;const b=[...d.querySelectorAll('p')].map(p=>`<p style="color:#424242;line-height:1.6;margin:0 0 12px">${p.innerHTML}</p>`).join('');mx(`<h3>${s}</h3>${b}`,true);return}""")
# newsletter com nome
rep("""body:JSON.stringify({email:v,origem:'newsletter',utm:UTM,visitante:VIS})""", """body:JSON.stringify({email:v,nome:($('#nnome')&&$('#nnome').value.trim())||null,origem:'newsletter',utm:UTM,visitante:VIS})""")
# lead gate procurava .card + data-open
rep("""const z=a.closest('.card');""", """const z=a.closest('.l8-card');""")

open(P, 'w', encoding='utf-8').write(out)
print('ok', len(out.encode()) // 1024, 'KB')
