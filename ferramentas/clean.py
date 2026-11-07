"""Passagem 'clean + autoridade + transparência' sobre o index.html já com a loja v2."""
import os, sys, re
REPO = sys.argv[1]
P = os.path.join(REPO, 'index.html')
html = open(P, encoding='utf-8').read()
def rep(old, new, count=1):
    global html
    assert old in html, 'não achei: ' + old[:90]
    html = html.replace(old, new, count)

CSS = r"""
/* ===== clean: menos ouro, mais ar, mais sobriedade ===== */
section{padding-block:72px}
.sh{margin-bottom:34px}
.sh h2{text-transform:none;letter-spacing:0;font-size:clamp(1.9rem,3.2vw,2.7rem);font-weight:600}
h2.gold-text,h3.gold-text{background:none;-webkit-text-fill-color:#f3ecdc;color:#f3ecdc}
.sh .rule{width:44px;height:1px;background:var(--gold3)}
.kick{color:var(--gold)}
.promo{background:#0a0908;color:#cdb77a;border-bottom:1px solid var(--line);font-size:.72rem;font-weight:500;letter-spacing:.14em}
.promo .track{animation:none;display:flex;justify-content:center;width:100%}
.promo .track span{gap:28px;flex-wrap:wrap;justify-content:center;padding:0 16px}
.promo .track i{opacity:.4}
@media(prefers-reduced-motion:no-preference){.promo .track{animation:none}}
/* cards sóbrios */
.card{background:#0c0b09}
.card .acts a.ask{display:none}
.card .acts{gap:8px}
.card h3{font-size:1rem}
.like{font-size:.74rem;color:#8d8678}.like b{color:#b9ad8f;font-weight:500}
.pix{font-size:1.35rem;color:#f3ecdc}.pix small{color:#9c8f70}
.card .full{color:#a79d86;font-size:.84rem;margin-top:4px}
.card .parc{color:#7f7765;font-size:.76rem}
.card .ph .fg{top:10px;left:auto;right:10px}
.card .ph .off{background:#f3ecdc;color:#140f05}
.exp-g>div:before{background:var(--gold3);height:1px;opacity:.6}
.exp-g h3{color:#f3ecdc}
.ex-n{color:var(--gold3)}
.bn .stats b{color:#f3ecdc}
.tile .tx b{color:#f3ecdc}
.benef .wrap{grid-template-columns:repeat(3,1fr);gap:22px 28px;padding-block:38px}
.benef div{text-align:left;display:grid;grid-template-columns:28px 1fr;gap:12px;align-items:start}
.benef svg{width:24px;height:24px;margin:2px 0 0;grid-row:1/3}
.benef b{letter-spacing:.08em;color:#f3ecdc;font-size:.74rem}
.benef span{font-size:.84rem;line-height:1.5;color:#a79d86}
@media(max-width:760px){.benef .wrap{grid-template-columns:1fr}}
/* sobre + transparência */
.sobre .wrap{display:grid;grid-template-columns:1.1fr .9fr;gap:48px;align-items:start}
.sobre h2{font-size:clamp(1.9rem,3vw,2.6rem);margin-top:10px}
.sobre .lead{color:#c9c2b2;font-size:1.05rem;line-height:1.7;margin-top:16px;max-width:58ch}
.sobre .lead+.lead{margin-top:12px}
.nao{border:1px solid var(--line);border-radius:18px;padding:28px;background:#0a0908}
.nao h3{font-size:1.4rem;color:#f3ecdc;margin-bottom:14px}
.nao ul{list-style:none;padding:0;margin:0;display:grid;gap:12px}
.nao li{display:grid;grid-template-columns:22px 1fr;gap:10px;color:#c9c2b2;line-height:1.55;font-size:.95rem}
.nao li b{color:#f3ecdc;font-weight:600}
.nao li i{font-style:normal;color:var(--gold);font-weight:700}
@media(max-width:860px){.sobre .wrap{grid-template-columns:1fr;gap:28px}}
.pol .faq summary{font-size:1.15rem}
.pol .faq p+p{margin-top:-8px}
/* fab mais discreto */
.fab-l{display:none}
"""
rep('</style>\n<style>.pv-desc', CSS + '</style>\n<style>.pv-desc')

# promo estática (uma cópia só)
rep("$('#promo-track').innerHTML=s+s;}", "$('#promo-track').innerHTML=s;}")
rep("""const PROMO     = ["Cartão em até 12x","Desconto de até 10% OFF pagando com o PIX","Entrega em todo o Brasil","Produtos 100% originais"];""",
    """const PROMO     = ["100% originais e lacrados","10% de desconto no PIX","Cartão em até 12x","Entrega em todo o Brasil com rastreio"];""")

# cards: preço transparente, "lembra" rebaixado
rep("""<div class="full">${brl(it.p)} no boleto</div><div class="parc">ou em até 12x no cartão</div>`;""",
    """<div class="full">${brl(it.p)} no cartão ou boleto</div><div class="parc">em até 12x · taxas informadas antes de pagar</div>`;""")
rep("""${it.like?`<p class="like">Lembra: <b>${it.like}</b></p>`:""}""", """${it.like?`<p class="like">Perfil olfativo próximo a <b>${it.like}</b></p>`:""}""")
rep("""$('#pv-like').innerHTML=it.like?`Lembra: <b>${it.like}</b>`:'';""", """$('#pv-like').innerHTML=it.like?`Perfil olfativo próximo a <b>${it.like}</b>`:'';""")
rep("""<div class="full">${brl(unit)} no boleto · cartão em até 12x</div>`;""", """<div class="full">${brl(unit)} no cartão (até 12x) ou boleto · taxas exibidas abaixo</div>`;""")

# tira a vitrine duplicada "Ícones da semana" (Top 5)
html = re.sub(r'<section id="top5-sec">.*?</section>\n', '', html, count=1, flags=re.S)
rep("""$('#top5').innerHTML=top.map((i,k)=>card(i,{rank:k+1})).join('');""", """if($('#top5'))$('#top5').innerHTML=top.map((i,k)=>card(i,{rank:k+1})).join('');""")

# hero: texto mais sóbrio
rep('<h1>O luxo que <span class="gold-text">assina a sua presença</span></h1>', '<h1>Alta perfumaria original, escolhida com você</h1>')
rep('<p class="lead">Fragrâncias exclusivas das casas mais desejadas do Oriente Médio e da perfumaria internacional. 100% originais, lacradas, e escolhidas com você por quem entende de perfume.</p>',
    '<p class="lead">Fragrâncias das casas mais desejadas do Oriente Médio e da perfumaria internacional. Sempre originais e lacradas, com um especialista para indicar a certa para você.</p>')

# faixa de garantias concretas
rep('''<div class="benef"><div class="wrap">
  <div><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6"><path d="M12 2l2.6 6.5L21 9l-5 4.3L17.5 21 12 17.5 6.5 21 8 13.3 3 9l6.4-.5z"/></svg><b>Alta perfumaria</b><span>Curadoria das casas mais desejadas</span></div>
  <div><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6"><path d="M12 3v18M5 10c3 0 4-3 7-3s4 3 7 3"/></svg><b>Alta fixação</b><span>Fragrâncias de longa duração</span></div>
  <div><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6"><path d="M12 3l7 3v5c0 5-3.5 8-7 10-3.5-2-7-5-7-10V6z"/><path d="M9 12l2 2 4-4"/></svg><b>100% originais</b><span>Lacrados, com selo do importador</span></div>
  <div><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6"><rect x="3" y="6" width="18" height="12" rx="2"/><path d="M3 10h18"/></svg><b>Pagamento facilitado</b><span>PIX, boleto ou cartão em até 12x</span></div>
  <div><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6"><path d="M3 7h11v9H3zM14 10h4l3 3v3h-7z"/><circle cx="7" cy="18" r="2"/><circle cx="17" cy="18" r="2"/></svg><b>Entrega segura</b><span>Entrega em todo o Brasil</span></div>
  <div><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6"><path d="M4 5h16v11H8l-4 4z"/></svg><b>Atendimento</b><span>Suporte humano pelo WhatsApp</span></div>
</div></div>''', '''<div class="benef" id="garantias"><div class="wrap">
  <div><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6"><path d="M12 3l7 3v5c0 5-3.5 8-7 10-3.5-2-7-5-7-10V6z"/><path d="M9 12l2 2 4-4"/></svg><b>Originalidade garantida</b><span>Só frascos originais e lacrados, com selo do importador. Nada de decants ou contratipos.</span></div>
  <div><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6"><rect x="3" y="6" width="18" height="12" rx="2"/><path d="M3 10h18"/></svg><b>Preço sem surpresa</b><span>PIX com 10% de desconto, boleto ou cartão em até 12x. A taxa do cartão aparece antes de você pagar.</span></div>
  <div><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6"><rect x="5" y="10" width="14" height="10" rx="2"/><path d="M8 10V7a4 4 0 0 1 8 0v3"/></svg><b>Pagamento seguro</b><span>Processado pelo Asaas, com criptografia e antifraude. A loja não armazena os dados do seu cartão.</span></div>
  <div><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6"><path d="M3 7h11v9H3zM14 10h4l3 3v3h-7z"/><circle cx="7" cy="18" r="2"/><circle cx="17" cy="18" r="2"/></svg><b>Entrega rastreada</b><span>Postagem em até 2 dias úteis após o pagamento, pelos Correios, com código de rastreio no seu WhatsApp.</span></div>
  <div><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6"><path d="M4 12a8 8 0 1 0 2.3-5.7"/><path d="M4 4v4h4"/></svg><b>7 dias para trocar</b><span>Troca ou devolução em até 7 dias após o recebimento, produto lacrado, conforme o Código de Defesa do Consumidor.</span></div>
  <div><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6"><path d="M4 5h16v11H8l-4 4z"/></svg><b>Atendimento humano</b><span>Um especialista de verdade no WhatsApp, de segunda a sábado, das 9h às 18h. Sem robô.</span></div>
</div></div>''')

# seção "Sobre a Nota" + "o que a Nota não faz" (antes do FAQ)
SOBRE = '''
<section class="sobre" id="sobre"><div class="wrap">
  <div>
    <p class="kick">Sobre a Nota</p>
    <h2>Uma curadoria pequena, feita por quem usa o que vende</h2>
    <p class="lead">A Nota Perfumaria nasceu de uma ideia simples: vender alta perfumaria árabe e importada do jeito que a gente gostaria de comprar. Sem mistério sobre o que é o produto, sem pressão, com alguém do outro lado que conhece cada fragrância da coleção.</p>
    <p class="lead">Selecionamos as casas mais respeitadas do Oriente Médio e da perfumaria internacional, trabalhamos só com frascos originais e lacrados e acompanhamos o seu pedido do pagamento até a entrega.</p>
    <div class="stats" style="display:flex;gap:28px;flex-wrap:wrap;margin-top:26px"><div><b style="display:block;font-family:var(--display);font-size:2.2rem;color:#f3ecdc;line-height:1">35+</b><span style="font-size:.72rem;letter-spacing:.14em;text-transform:uppercase;color:var(--muted)">casas e marcas</span></div><div><b style="display:block;font-family:var(--display);font-size:2.2rem;color:#f3ecdc;line-height:1">350+</b><span style="font-size:.72rem;letter-spacing:.14em;text-transform:uppercase;color:var(--muted)">fragrâncias</span></div><div><b style="display:block;font-family:var(--display);font-size:2.2rem;color:#f3ecdc;line-height:1">100%</b><span style="font-size:.72rem;letter-spacing:.14em;text-transform:uppercase;color:var(--muted)">originais e lacrados</span></div></div>
  </div>
  <div class="nao">
    <h3>O que a Nota não faz</h3>
    <ul>
      <li><i>✕</i><span><b>Não vende decants nem frascos abertos.</b> Todo perfume sai lacrado, do jeito que o importador entregou.</span></li>
      <li><i>✕</i><span><b>Não vende contratipos.</b> Quando dizemos que um perfume tem perfil próximo a outro, é uma referência olfativa, não uma cópia.</span></li>
      <li><i>✕</i><span><b>Não esconde taxa.</b> O valor do PIX, do boleto e de cada parcela aparece antes de você confirmar o pagamento.</span></li>
      <li><i>✕</i><span><b>Não guarda dados do seu cartão.</b> O pagamento é processado pelo Asaas; a loja só recebe a confirmação.</span></li>
      <li><i>✕</i><span><b>Não deixa você sem resposta.</b> Atendimento humano pelo WhatsApp, de segunda a sábado.</span></li>
    </ul>
  </div>
</div></section>
'''
rep('<section id="faq"><div class="wrap">', SOBRE + '<section id="faq"><div class="wrap">')

# políticas completas (seção própria, antes do Instagram)
POL = '''
<section id="politicas" class="pol"><div class="wrap">
  <div class="sh"><h2 class="gold-text">Políticas da loja</h2><p>Tudo o que vale na sua compra, escrito por extenso</p><div class="rule"></div></div>
  <div class="faq">
    <details id="pol-prazos"><summary>Prazos e entregas</summary><p>Postamos o pedido em até 2 dias úteis após a confirmação do pagamento (PIX e cartão confirmam na hora; boleto, em até 2 dias úteis). O envio é feito pelos Correios, com PAC ou SEDEX conforme a opção escolhida no checkout.</p><p>O prazo de entrega é o informado pelos Correios para o seu CEP no momento da compra e começa a contar a partir da postagem. Em datas de alto volume (Black Friday, Natal, Dia das Mães) o prazo dos Correios pode aumentar; avisamos pelo WhatsApp se isso acontecer.</p><p>O valor do frete é calculado pelo CEP e somado ao total antes do pagamento.</p></details>
    <details id="pol-rastreio"><summary>Rastreamento do pedido</summary><p>Assim que o pedido é postado, você recebe o código de rastreio pelo WhatsApp informado na compra. Quem compra logado também acompanha o status (pagamento, separação, envio e entrega) em <b>Minha conta</b>.</p></details>
    <details id="pol-trocas"><summary>Trocas e devoluções</summary><p>Você pode desistir da compra em até 7 dias corridos após o recebimento, conforme o art. 49 do Código de Defesa do Consumidor, desde que o produto esteja lacrado e sem uso. Nesse caso devolvemos o valor integral, incluindo o frete, pelo mesmo meio de pagamento.</p><p>Produtos com defeito de fabricação ou danificados no transporte são trocados sem custo. Fotografe a embalagem e o produto no recebimento e nos chame no WhatsApp em até 7 dias.</p><p>Por questões de higiene e segurança, não aceitamos troca de perfumes abertos ou com lacre rompido quando o motivo for gosto pessoal. Para evitar isso, use a consultoria antes de comprar: é de graça.</p></details>
    <details id="pol-pagamento"><summary>Pagamento e preços</summary><p>Aceitamos PIX (com 10% de desconto sobre o preço de tabela), boleto bancário e cartão de crédito em até 12x. No cartão, a taxa da operadora é repassada e exibida parcela por parcela antes de você confirmar. Todo pagamento é processado pelo Asaas; a loja não armazena número, validade ou código do cartão.</p><p>Os preços podem mudar sem aviso, mas o valor que vale é sempre o exibido no momento da confirmação do pedido.</p></details>
    <details id="pol-originalidade"><summary>Originalidade dos produtos</summary><p>Vendemos exclusivamente perfumes originais, adquiridos de importadores e distribuidores autorizados, lacrados e com selo do importador quando aplicável. Não trabalhamos com decants, frascos abertos, réplicas ou contratipos. Se você receber um produto que não corresponda ao anunciado, devolvemos o valor integral.</p></details>
    <details id="pol-privacidade"><summary>Privacidade e dados (LGPD)</summary><p>Usamos nome, CPF, e-mail, WhatsApp e endereço apenas para processar o pagamento, enviar o pedido e atender você. Os dados ficam em ambiente seguro e não são vendidos nem compartilhados com terceiros, exceto o necessário para pagamento (Asaas) e entrega (Correios).</p><p>Você pode pedir a correção ou a exclusão dos seus dados a qualquer momento pelo WhatsApp. Mensagens de ofertas só são enviadas com o seu consentimento, e você pode cancelar quando quiser.</p></details>
    <details id="pol-contato"><summary>Contato</summary><p>Atendimento pelo WhatsApp <b>(11) 98265-9792</b>, de segunda a sábado, das 9h às 18h. Fora desse horário, deixe sua mensagem que respondemos no próximo dia útil.</p></details>
  </div>
</div></section>
'''
rep('<section id="instagram"><div class="wrap">', POL + '<section id="instagram"><div class="wrap">')

# links do rodapé apontam para as políticas completas
rep('<div><h4>Ajuda &amp; Suporte</h4><ul><li><a href="#" data-pol="prazos">Política de prazos e entregas</a></li><li><a href="#" data-pol="trocas">Política de trocas e devoluções</a></li><li><a href="#" data-pol="rastreio">Rastreie o seu pedido</a></li><li><a href="#" data-pol="contato">Contato</a></li></ul></div>',
    '<div><h4>Ajuda &amp; Suporte</h4><ul><li><a href="#pol-prazos" data-pol="prazos">Prazos e entregas</a></li><li><a href="#pol-trocas" data-pol="trocas">Trocas e devoluções</a></li><li><a href="#pol-rastreio" data-pol="rastreio">Rastreie o seu pedido</a></li><li><a href="#pol-pagamento" data-pol="pagamento">Pagamento e preços</a></li><li><a href="#pol-originalidade" data-pol="originalidade">Originalidade</a></li><li><a href="#pol-privacidade" data-pol="privacidade">Privacidade (LGPD)</a></li><li><a href="#faq">Perguntas frequentes</a></li></ul></div>')
rep('<div><h4>Atendimento</h4><ul><li id="f-wa">WhatsApp: (11) 98265-9792</li><li>Seg. a sáb., 9h às 18h</li><li>Siga-nos: @notaperfumaria</li></ul></div>',
    '<div><h4>Atendimento</h4><ul><li id="f-wa">WhatsApp: (11) 98265-9792</li><li>Seg. a sáb., 9h às 18h</li><li>Instagram: @notaperfumaria</li><li>Pagamentos: Asaas · Envios: Correios</li></ul></div>')
rep('<div class="copy"><span>NOTA PERFUMARIA · 2026. Todos os direitos reservados.</span><span>Preços sujeitos a alteração. Consulte disponibilidade.</span></div>',
    '<div class="copy"><span>Nota Perfumaria · 2026. Todos os direitos reservados.</span><span>Preços sujeitos a alteração; vale o valor exibido na confirmação do pedido.</span></div>')

# data-pol: abre a política completa em vez do aviso curto
rep("const pol=t.closest('[data-pol]');if(pol){e.preventDefault();", "const pol=t.closest('[data-pol]');if(pol){e.preventDefault();const d=document.getElementById('pol-'+pol.dataset.pol);if(d){d.open=true;d.scrollIntoView({behavior:'smooth',block:'start'});return}")

open(P, 'w', encoding='utf-8').write(html)
print('ok', len(html.encode()) // 1024, 'KB')
