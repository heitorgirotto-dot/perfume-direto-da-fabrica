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
srv = socketserver.ThreadingTCPServer(('127.0.0.1', 8797), H)
threading.Thread(target=srv.serve_forever, daemon=True).start()
errs = []
B = 'http://127.0.0.1:8797'
with sync_playwright() as p:
    b = p.chromium.launch(executable_path='/usr/bin/google-chrome', args=['--no-sandbox'])
    for name, w in [('desk', 1366), ('mob', 390)]:
        pg = b.new_page(viewport={'width': w, 'height': 900})
        pg.on('pageerror', lambda e: errs.append(name + ': ' + str(e)))
        pg.goto(B + '/'); pg.wait_for_timeout(900)
        # força lazy images
        pg.evaluate("document.querySelectorAll('img[loading=lazy]').forEach(i=>i.loading='eager')"); pg.wait_for_timeout(1500)
        pg.screenshot(path=f'{OUT}/l8-{name}-home.png', full_page=True)
        if name == 'desk':
            print('cards best:', pg.locator('#best .l8-card').count(), 'sale:', pg.locator('#sale .l8-card').count(), 'marca:', pg.locator('#marca-track .l8-card').count(), 'imp:', pg.locator('#imp-track .l8-card').count())
            pg.click('#st-tabs [data-st="F"]'); pg.wait_for_timeout(200); print('aba F:', pg.locator('#best .l8-card').count())
            pg.click('[data-occg="feminino"]'); pg.wait_for_timeout(200)
            pg.click('#occ-tiles a >> nth=2'); pg.wait_for_timeout(500)
            print('ocasião ->', pg.url, '|', pg.text_content('#cat-title'), pg.text_content('#count'))
            pg.screenshot(path=f'{OUT}/l8-desk-lista.png')
            pg.click('#grid .l8-card [data-add] >> nth=0'); pg.wait_for_timeout(300); print('sacola:', pg.text_content('#cart-q'))
            pg.click('#grid .l8-card .l8-card-n >> nth=1'); pg.wait_for_timeout(500); print('produto:', pg.url, not pg.is_hidden('#pv'))
            pg.screenshot(path=f'{OUT}/l8-desk-produto.png'); pg.keyboard.press('Escape'); pg.wait_for_timeout(200)
            pg.click('.l8-logo'); pg.wait_for_timeout(400); print('logo -> home:', pg.url, pg.is_visible('#hero'))
            pg.hover('.l8-dd >> nth=1'); pg.wait_for_timeout(300); pg.screenshot(path=f'{OUT}/l8-desk-marcas.png')
            pg.fill('#q', 'yara'); pg.press('#q', 'Enter'); pg.wait_for_timeout(400); print('busca yara:', pg.text_content('#count'))
            pg.click('.l8-foot a[data-pol="trocas"]'); pg.wait_for_timeout(300); print('política modal:', pg.is_visible('#mx'))
            pg.keyboard.press('Escape')
            pg.goto(B + '/c/lattafa'); pg.wait_for_timeout(800); print('rota marca:', pg.text_content('#cat-title'), pg.text_content('#count'))
            pg.goto(B + '/p/lattafa-asad-edp-100ml'); pg.wait_for_timeout(800); print('rota produto modal:', not pg.is_hidden('#pv'))
            pg.goto(B + '/'); pg.wait_for_timeout(600); pg.click('a[data-modo="quiz"]'); pg.wait_for_timeout(300)
            pg.click('.chips[data-q="f"] button >> nth=0'); pg.wait_for_timeout(300); print('quiz res:', pg.locator('#qz-res .l8-card').count())
            pg.screenshot(path=f'{OUT}/l8-desk-quiz.png')
        else:
            pg.click('#burger'); pg.wait_for_timeout(300); pg.screenshot(path=f'{OUT}/l8-mob-menu.png')
        pg.close()
    b.close()
srv.shutdown()
print('ERROS:', json.dumps(errs, ensure_ascii=False, indent=1) if errs else 'nenhum')
