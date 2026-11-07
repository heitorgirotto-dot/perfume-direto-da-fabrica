import sys, json, threading, http.server, socketserver, os
from playwright.sync_api import sync_playwright
REPO, OUT = sys.argv[1], sys.argv[2]
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
    def do_POST(self): self.send_response(204); self.end_headers()
socketserver.ThreadingTCPServer.allow_reuse_address = True
srv = socketserver.ThreadingTCPServer(('127.0.0.1', 8799), H)
threading.Thread(target=srv.serve_forever, daemon=True).start()
errs = []
B = 'http://127.0.0.1:8799'
with sync_playwright() as p:
    b = p.chromium.launch(executable_path='/usr/bin/google-chrome', args=['--no-sandbox'])
    for name, w in [('desk', 1366), ('mob', 390)]:
        pg = b.new_page(viewport={'width': w, 'height': 900})
        pg.on('pageerror', lambda e: errs.append(name + ': ' + str(e)))
        pg.goto(B + '/'); pg.wait_for_timeout(900)
        # força lazy images
        pg.evaluate("document.querySelectorAll('img[loading=lazy]').forEach(i=>i.loading='eager')"); pg.wait_for_timeout(1500)
        pg.screenshot(path=f'{OUT}/h-{name}-home.png', full_page=True)
        if name == 'desk':
            print('best:', pg.locator('#best .h-card').count(), 'grid:', pg.locator('#grid .h-card').count(), 'marcas:', pg.locator('#brands a').count())
            pg.click('#grid .h-card [data-add] >> nth=0'); pg.wait_for_timeout(300); print('sacola:', pg.text_content('#cart-q'))
            pg.click('#morebtn'); pg.wait_for_timeout(300); print('carregar mais:', pg.locator('#grid .h-card').count())
            pg.click('#grid .h-card .h-n >> nth=1'); pg.wait_for_timeout(500); print('produto:', pg.url, not pg.is_hidden('#pv'))
            pg.screenshot(path=f'{OUT}/h-desk-produto.png'); pg.keyboard.press('Escape'); pg.wait_for_timeout(200)
            pg.click('#nav > ul > li:nth-child(3) > a'); pg.wait_for_timeout(500); print('arabes:', pg.url, pg.text_content('#cat-title'), pg.text_content('#count'))
            pg.screenshot(path=f'{OUT}/h-desk-lista.png')
            pg.click('.h-logo'); pg.wait_for_timeout(400); print('logo->home:', pg.url, pg.is_visible('.h-banner'))
            pg.click('#brands a >> nth=0'); pg.wait_for_timeout(400); print('marca chip:', pg.text_content('#cat-title'), pg.text_content('#count'))
            pg.fill('#q', 'yara'); pg.press('#q', 'Enter'); pg.wait_for_timeout(400); print('busca:', pg.text_content('#count'))
            pg.click('.h-foot a[data-pol="trocas"]'); pg.wait_for_timeout(300); print('política:', pg.is_visible('#mx')); pg.keyboard.press('Escape')
            pg.goto(B + '/c/lattafa'); pg.wait_for_timeout(800); print('rota marca:', pg.text_content('#cat-title'), pg.text_content('#count'))
            pg.goto(B + '/p/lattafa-asad-edp-100ml'); pg.wait_for_timeout(800); print('rota produto:', not pg.is_hidden('#pv'))
            pg.goto(B + '/'); pg.wait_for_timeout(600); pg.click('a[data-jump="colecoes"]'); pg.wait_for_timeout(700); print('mostrar todos:', pg.evaluate('Math.round(document.getElementById("colecoes").getBoundingClientRect().top)'))
            pg.hover('#nav .h-dd >> nth=0'); pg.wait_for_timeout(200); pg.click('#nav a[data-modo="quiz"]'); pg.wait_for_timeout(300); pg.click('.chips[data-q="f"] button >> nth=1'); pg.wait_for_timeout(300); print('quiz:', pg.locator('#qz-res .h-card').count())
        else:
            pg.click('#burger'); pg.wait_for_timeout(300); pg.screenshot(path=f'{OUT}/h-mob-menu.png')
        pg.close()
    b.close()
srv.shutdown()
print('ERROS:', json.dumps(errs, ensure_ascii=False, indent=1) if errs else 'nenhum')
