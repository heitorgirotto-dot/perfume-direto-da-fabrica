import sys, json, threading, http.server, socketserver, os
from playwright.sync_api import sync_playwright
REPO = sys.argv[1]; OUT = sys.argv[2]
os.chdir(REPO)
class H(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *a): pass
    def do_GET(self):
        p = self.path.split('?')[0]
        if p.startswith('/api/'):
            self.send_response(404); self.end_headers(); return
        if p.startswith('/p/') or p.startswith('/c/'):
            self.path = '/index.html'
        return super().do_GET()
    def do_POST(self):
        self.send_response(204); self.end_headers()
socketserver.ThreadingTCPServer.allow_reuse_address = True
srv = socketserver.ThreadingTCPServer(('127.0.0.1', 8791), H)
threading.Thread(target=srv.serve_forever, daemon=True).start()
errs = []
with sync_playwright() as p:
    b = p.chromium.launch(executable_path='/usr/bin/google-chrome', args=['--no-sandbox'])
    for name, w in [('desk', 1366), ('mob', 390)]:
        pg = b.new_page(viewport={'width': w, 'height': 860})
        pg.on('pageerror', lambda e: errs.append(str(e)))
        pg.on('console', lambda m: errs.append('console.' + m.type + ': ' + m.text) if m.type == 'error' and 'Failed to load resource' not in m.text else None)
        pg.goto('http://127.0.0.1:8791/'); pg.wait_for_timeout(800)
        pg.screenshot(path=f'{OUT}/{name}-home.png', full_page=True)
        if name == 'desk':
            # dropdown marcas
            pg.click('#nav .dd:nth-of-type(2) > button'); pg.wait_for_timeout(200)
            pg.screenshot(path=f'{OUT}/{name}-menu-marcas.png')
            pg.click('#nav .dd:nth-of-type(2) > button')
            pg.click('#nav .dd:nth-of-type(3) > button'); pg.wait_for_timeout(200)
            pg.screenshot(path=f'{OUT}/{name}-menu-familias.png')
            pg.click('#nav-fam a[data-cat="doce"]'); pg.wait_for_timeout(600)
            print('url categoria:', pg.url, '| h2:', pg.text_content('#cat-title'), '|', pg.text_content('#count'))
            pg.screenshot(path=f'{OUT}/{name}-cat-doce.png')
            # produto
            pg.click('#grid .card .buy'); pg.wait_for_timeout(500)
            print('url produto:', pg.url, '| title:', pg.title())
            pg.screenshot(path=f'{OUT}/{name}-produto.png')
            pg.keyboard.press('Escape'); pg.wait_for_timeout(300)
            print('após fechar:', pg.url)
            # rota direta
            pg.goto('http://127.0.0.1:8791/p/lattafa-asad-edp-100ml'); pg.wait_for_timeout(800)
            print('rota direta produto:', pg.title(), '| modal aberto:', not pg.is_hidden('#pv'))
            pg.goto('http://127.0.0.1:8791/c/lattafa'); pg.wait_for_timeout(800)
            print('rota direta marca:', pg.text_content('#cat-title'), pg.text_content('#count'))
            pg.goto('http://127.0.0.1:8791/c/noite'); pg.wait_for_timeout(800)
            print('rota ocasião:', pg.text_content('#cat-title'), pg.text_content('#count'))
            # carrinho
            pg.click('#grid .card [data-add]'); pg.wait_for_timeout(300)
            print('carrinho:', pg.text_content('#cart-q'), pg.text_content('#cart-v'))
            pg.click('#cart-btn'); pg.wait_for_timeout(400)
            pg.screenshot(path=f'{OUT}/{name}-carrinho.png')
        else:
            pg.click('#nav .dd:nth-of-type(3) > button'); pg.wait_for_timeout(200)
            pg.screenshot(path=f'{OUT}/{name}-menu.png')
        pg.close()
    b.close()
srv.shutdown()
print('ERROS:', json.dumps(errs, ensure_ascii=False, indent=1) if errs else 'nenhum')
