"""Tira as 11 imagens base64 e o catálogo ITEMS de dentro do index.html.
Gera: img/*.jpg, produtos.js (const ITEMS=...), produtos.json."""
import re, base64, json, os, sys, hashlib

REPO = sys.argv[1]
html = open(os.path.join(REPO, 'index.html'), encoding='utf-8').read()
os.makedirs(os.path.join(REPO, 'img'), exist_ok=True)

# ---- imagens base64 -> arquivos (nome pelo contexto)
nomes = ['logo', 'capa', 'hero', 'colagem-1', 'colagem-2', 'colagem-3', 'colagem-4', 'atendimento', 'extra-1', 'extra-2', 'extra-3']
seen = {}
idx = [0]
def sub(m):
    mime, b64 = m.group(1), m.group(2)
    h = hashlib.md5(b64.encode()).hexdigest()[:8]
    if h in seen:
        return seen[h]
    ext = {'jpeg': 'jpg', 'jpg': 'jpg', 'png': 'png', 'webp': 'webp'}[mime]
    nome = nomes[idx[0]] if idx[0] < len(nomes) else f'img-{idx[0]}'
    idx[0] += 1
    path = f'img/{nome}.{ext}'
    open(os.path.join(REPO, path), 'wb').write(base64.b64decode(b64))
    seen[h] = path
    return path
html = re.sub(r'data:image/(jpeg|jpg|png|webp);base64,([A-Za-z0-9+/=]+)', sub, html)
print('imagens:', idx[0], 'únicas:', len(seen))

# ---- ITEMS -> produtos.js / produtos.json
m = re.search(r'^const ITEMS = (\[.*?\]);$', html, re.M | re.S)
items = json.loads(m.group(1))
for i, it in enumerate(items):
    it.setdefault('id', i)
json.dump(items, open(os.path.join(REPO, 'produtos.json'), 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))
open(os.path.join(REPO, 'produtos.js'), 'w', encoding='utf-8').write('const ITEMS=' + json.dumps(items, ensure_ascii=False, separators=(',', ':')) + ';\n')
html = html[:m.start()] + '// Catálogo embarcado: carregado de /produtos.js (cache) e atualizado por /api/produtos' + html[m.end():]
html = html.replace('<script>\n// ===== CONFIG =====', '<script src="/produtos.js?v=1"></script>\n<script>\n// ===== CONFIG =====', 1)
print('produtos:', len(items))

open(os.path.join(REPO, 'index.html'), 'w', encoding='utf-8').write(html)
print('index.html agora:', len(html.encode()) // 1024, 'KB')
