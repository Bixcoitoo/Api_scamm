import os
import sys
import time
from pathlib import Path

# Adiciona o diretório raiz ao PYTHONPATH
root_dir = Path(__file__).parent
sys.path.append(str(root_dir))

import uvicorn
import redis
from config.redis_config import REDIS_CONFIG

def check_redis_connection():
    """Verifica a conexão com o Redis"""
    max_retries = 5
    retry_delay = 2
    
    for attempt in range(max_retries):
        try:
            r = redis.Redis(**REDIS_CONFIG)
            r.ping()
            print("✅ Conexão com Redis estabelecida com sucesso!")
            return True
        except redis.ConnectionError as e:
            if attempt < max_retries - 1:
                print(f"⚠️ Tentativa {attempt + 1} de {max_retries} de conectar ao Redis...")
                time.sleep(retry_delay)
            else:
                print(f"❌ Erro ao conectar com Redis após {max_retries} tentativas: {str(e)}")
                return False

if __name__ == "__main__":
    # Verifica conexão com Redis
    if not check_redis_connection():
        print("⚠️ Redis não está disponível. A API iniciará sem rate limiting.")
    
    # Inicia a API
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=4200,
        reload=True,
        proxy_headers=True,
        forwarded_allow_ips="*"
    ) 