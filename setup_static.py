import os
import requests
import shutil
from pathlib import Path

# Cria a pasta static se não existir
if not os.path.exists('static'):
    os.makedirs('static')

# URLs dos arquivos necessários
files = {
    'swagger-ui.css': 'https://cdn.jsdelivr.net/npm/swagger-ui-dist@5.11.0/swagger-ui.css',
    'swagger-ui-bundle.js': 'https://cdn.jsdelivr.net/npm/swagger-ui-dist@5.11.0/swagger-ui-bundle.js',
    'favicon.png': 'https://cdn.jsdelivr.net/npm/swagger-ui-dist@5.11.0/favicon-32x32.png'
}

# Download dos arquivos
for filename, url in files.items():
    response = requests.get(url)
    if response.status_code == 200:
        with open(f'static/{filename}', 'wb') as f:
            f.write(response.content)
        print(f'✅ Arquivo {filename} baixado com sucesso')
    else:
        print(f'❌ Erro ao baixar {filename}')

# Configuração dos diretórios
BASE_DIR = Path(__file__).parent.parent
STATIC_DIR = BASE_DIR / "static"
CUSTOM_DIR = STATIC_DIR / "custom"
CSS_DIR = CUSTOM_DIR / "css"
JS_DIR = CUSTOM_DIR / "js"

# Criar diretórios
for directory in [STATIC_DIR, CUSTOM_DIR, CSS_DIR, JS_DIR]:
    directory.mkdir(exist_ok=True)

# Conteúdo do CSS
css_content = """/* Seu CSS aqui */"""

# Conteúdo do JS
js_content = """/* Seu JavaScript aqui */"""

# Criar arquivos
(CSS_DIR / "custom.css").write_text(css_content)
(JS_DIR / "custom.js").write_text(js_content)

print("✅ Arquivos estáticos configurados com sucesso!") 