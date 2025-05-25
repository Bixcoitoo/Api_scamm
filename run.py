import os
import sys
from pathlib import Path

# Adiciona o diretório raiz ao PYTHONPATH
root_dir = Path(__file__).parent
sys.path.append(str(root_dir))

import uvicorn

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=4200,
        ssl_keyfile="certificates/private_key.pem",
        ssl_certfile="certificates/certificate.pem",
        reload=True
    ) 