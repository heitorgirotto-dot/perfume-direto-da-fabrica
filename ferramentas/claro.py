"""Tema claro (padrão Nuvemshop/LAB 8): cabeçalho preto, corpo branco, cards brancos."""
import os, sys, re
REPO = sys.argv[1]
P = os.path.join(REPO, 'index.html')
html = open(P, encoding='utf-8').read()

# 1) textos claros usados inline/CSS -> escuros (globalmente; o que precisa ficar claro é re-forçado no bloco CSS)
MAP = {
    '#f3ecdc': '#161412', '#e9e2d2': '#161412', '#f6efe0': '#161412', '#f0e8d6': '#161412', '#f5efe2': '#161412',
    '#c9c2b2': '#4a453c', '#cfc6b2': '#4a453c', '#d9d2c2': '#4a453c', '#e8dfcc': '#4a453c', '#b9b2a3': '#5c564c', '#bdb6a6': '#5c564c',
    '#a9a294': '#6b655a', '#a79d86': '#6b655a', '#b9ad8f': '#6b655a', '#9c8f70': '#6b655a', '#9a9385': '#6b655a', '#a4987f': '#6b655a',
    '#8d8678': '#7a7466', '#7f7765': '#8a8375', '#bbb': '#777',
}
for a, b in MAP.items():
    html = html.replace(a, b)

CSS = r"""
/* ===== tema claro ===== */
:root{--bg:#ffffff;--bg2:#f7f5f0;--card:#ffffff;--line:#e6e1d8;--fg:#161412;--muted:#6b655a;--gold:#b8923a;--gold2:#9c7a2e;--gold3:#7a5f22;color-scheme:light}
body{background:#fff;color:var(--fg)}
body::before{background:#0a0908}
/* cabeçalho preto, logo dourado */
.promo{background:#0a0908;color:#e8d9ad;border-bottom:0}
header.top{background:#0a0908;border-bottom:1px solid #1e1b16}
header.top .search{background:#17150f;border-color:#2a261e}header.top .search input{color:#f3ecdc}header.top .search button{background:#d9b25a;color:#140f05}
header.top .acc{color:#f3ecdc;border-color:#3a3328}header.top .acc:hover{background:#1a1712}header.top .cartb .cq{background:#d9b25a;color:#140f05}
.nav{border-top:1px solid #1e1b16;background:#0a0908}
.nav>a,.nav>.dd>button{color:#efe8d8}.nav>a:hover,.nav>.dd>button:hover,.nav>a.on,.nav>.dd.on>button{color:#f5dd95;border-bottom-color:#d9b25a}
.nav .hl{color:#f5dd95}
.dd-box{background:#fff;border-color:var(--line);border-top:2px solid #0a0908;box-shadow:0 24px 50px rgba(0,0,0,.14)}
.dd-box a{color:var(--fg)}.dd-box a:hover{color:var(--gold2)}.dd-box h5{color:#161412}
.dd-box .tiles a{background:var(--bg2)}.dd-box .tiles a b{color:#161412}
/* hero e capa continuam escuros (imagem) */
.cover-wide{background:#0a0908;border-bottom:0}
.hero{background:#0a0908}.hero h1,.hero .lead,.hero-benef{color:#f3ecdc}.hero .lead{color:#cfc6b2}.hero .kick{color:#d9b25a}
.hero .btn-ghost{border-color:#d9b25a;color:#f5dd95}
.cw-h{color:#f6efe0}.cw-s{color:#e8dfcc}.cw-txt{color:#f3ead7}.cw-k{color:#d9b25a}
/* corpo */
.gold-text{background:none;-webkit-text-fill-color:#161412;color:#161412}
h2.gold-text,h3.gold-text{-webkit-text-fill-color:#161412;color:#161412}
.kick{color:var(--gold)}
.sh .rule{background:#161412;height:2px;width:40px}
.exp{background:#fff}.exp-g>div{background:var(--bg2);border-color:var(--line)}.exp-g>div:before{display:none}.exp-g h3{color:#161412}.ex-n{color:var(--gold)}.exp-g p{color:#5c564c}
.card{background:#fff;border-color:var(--line)}.card:hover{border-color:#161412}
.card .ph{background:#fff;border-bottom:1px solid var(--line)}
.card .brand{color:var(--gold2)}.card h3{color:#161412}.card h3 a{color:#161412}
.notes{color:#6b655a}.notes b{color:#161412}
.pix{color:#161412}.pix small{color:#6b655a}
.pill{background:rgba(255,255,255,.92);border-color:var(--line);color:#6b655a}.pill.M{color:#2f5aa8;border-color:#b9c9e8}.pill.F{color:#b43a76;border-color:#eab6cf}.pill.U{color:#7a5f22;border-color:#e0cf9a}
.card .ph .off{background:#161412;color:#fff}
.card .ph .fg{background:#e8f5ea;color:#1b6b32}
.acts .buy,.buy{background:#161412;color:#fff;border:1px solid #161412}.acts .buy:hover{background:#2a2622}
.acts .cart-ic,.cart-ic{border-color:#cfc7b6;color:#161412}.acts .ask{background:#fff;color:#1b6b32;border-color:#25a05a}.acts button.in{background:#161412;color:#fff}
.btn-gold{background:#161412;color:#fff}
.btn-ghost{border-color:#161412;color:#161412}
.tab{color:#6b655a;border-color:var(--line)}.tab.on{background:#161412;border-color:#161412;color:#fff}
.filters select{background:#fff;color:#161412}
.count{color:#6b655a}
.tile{border-color:var(--line);background:#f3f0e9}.tile img{opacity:.9}.tile::after{background:linear-gradient(180deg,rgba(255,255,255,0) 35%,rgba(22,20,18,.9))}.tile .tx b{color:#fff}.tile .tx span{color:#e8e2d6}.tile .tx em{color:#f5dd95}
.bn{background:#0a0908}.bn .txt,.bn .lead,.bn li{color:#f3ecdc}.bn .lead{color:#cfc6b2}.bn .stats b{color:#f3ecdc}.bn .kick{color:#d9b25a}.bn h2.gold-text{-webkit-text-fill-color:#f3ecdc;color:#f3ecdc}
.quiz{background:var(--bg2)}.qz-s b{color:#161412}.chips button{border-color:#cfc7b6;color:#4a453c;background:#fff}.chips button.on{background:#161412;color:#fff}
.benef{background:var(--bg2)}.benef b{color:#161412}.benef svg{color:var(--gold)}
.sobre{background:#fff}.sobre h2{color:#161412}.sobre .lead{color:#4a453c}
.nao{background:var(--bg2);border-color:var(--line)}.nao h3,.nao li b{color:#161412}.nao li{color:#4a453c}.nao li i{color:var(--gold)}
.faq summary{color:#161412}.faq details p{color:#5c564c}.faq summary::after{color:var(--gold)}
.insta{background:var(--bg2)}.insta h3{color:#161412}
footer{background:#0a0908;border-top:0;color:#cfc6b2}footer h4{color:#d9b25a}.fcols ul{color:#cfc6b2}.fcols a:hover{color:#f5dd95}
.news{border-color:#3a3328}.news input{color:#f3ecdc}.news button{background:#d9b25a}
footer .note{color:#8d8678}.pay span{border-color:#3a3328;color:#cfc6b2}
.seg>div{background:#12100c;border-color:#2a261e}.seg b{color:#f3ecdc}.seg span{color:#a9a294}
.copy{color:#8d8678;border-color:#2a261e}
/* modal produto */
.pv{background:rgba(0,0,0,.6)}.pv-box{background:#fff;border-color:var(--line)}.pv-main{background:#fff}.pv-info h3{color:#161412}.pv-info .brand{color:var(--gold2)}.pv-close{color:#161412}
.frete{background:var(--bg2)}.frete h4{color:#161412}.frete input,.frete select{background:#fff;color:#161412}.frete button.calc{border-color:#161412;color:#161412}
.opt{background:#fff}.opt.on{border-color:#161412;background:#f3f0e9}.opt b{color:#161412}
.tot b{color:#161412}.msg{color:#6b655a}
.ask{border-color:#25a05a;color:#1b6b32;background:#fff}
/* modais (carrinho, login, pagamento) */
.mx{background:rgba(22,20,18,.6)}.mx-box{background:#fff;border-color:var(--line)}.mx h3{color:#161412}.mx p.sub{color:#6b655a}
.mx-tabs{background:#f0ece4}.mx-tabs button{color:#5c564c}.mx-tabs button.on{background:#161412;color:#fff}
.mx label{color:#6b655a}.mx input[type=text],.mx input[type=email],.mx input[type=password],.mx input[type=tel],.mx select{background:#fff;border-color:#d6d0c4;color:#161412}
.mx .ck{color:#4a453c}.mx .go{background:#161412;color:#fff}.mx .lnk{color:var(--gold2)}.mx .err{color:#c0392b}
.ped{background:var(--bg2)}.ped-h{color:#6b655a}.ped-h b{color:#161412}.ck-sec h4{color:#161412}
.mx .opt.on{background:#f3f0e9;border-color:#161412}.mx .opt small{color:#6b655a}
.cart-l .br{color:var(--gold2)}.cart-l .nm{color:#161412}.cart-l .pr{color:#6b655a}.cart-l .rm{color:#b43a3a}
.cart-vazio{color:#6b655a}
.st-badge{background:#f0ece4;color:#161412}
.toast{background:#161412;color:#fff}
.ok-bar{background:#e8f5ea;border-color:#9fd6ad;color:#1b6b32}
/* página de produto SSR */
.ssr-p{background:#fff}.ssr-m{background:var(--bg2);border:1px solid var(--line)}.ssr-i h1{color:#161412}.ssr-i .brand{color:var(--gold2)}
.cat-crumb{color:#6b655a}.cat-crumb a{color:var(--gold2)}
.fab a{background:#25d366}
.old{color:#8a8375}
"""
html = html.replace('</head>', '<style>' + CSS + '</style>\n</head>', 1)
assert CSS in html

# tag theme-color para a barra do celular
html = html.replace('<meta name="viewport"', '<meta name="theme-color" content="#0a0908">\n<meta name="viewport"', 1)
open(P, 'w', encoding='utf-8').write(html)
print('ok', len(html.encode()) // 1024, 'KB')
