import subprocess
import sys
import os
import time
import redis
from config.redis_config import REDIS_CONFIG

def install_redis():
    """Instala o Redis no Linux"""
    commands = [
        'sudo apt update',
        'sudo apt install -y redis-server',
        'sudo systemctl start redis-server',
        'sudo systemctl enable redis-server'
    ]
    
    for cmd in commands:
        subprocess.run(cmd, shell=True, check=True)
        print(f"Executado: {cmd}")

def check_redis_connection():
    """Verifica a conexão com o Redis"""
    try:
        r = redis.Redis(**REDIS_CONFIG)
        r.ping()
        print("✅ Conexão com Redis estabelecida com sucesso!")
        return True
    except redis.ConnectionError as e:
        print(f"❌ Erro ao conectar com Redis: {str(e)}")
        return False

def main():
    print("🔍 Verificando ambiente...")
    
    # Verifica se está rodando no Linux
    if sys.platform != 'linux':
        print("❌ Este script deve ser executado no Linux")
        return
    
    # Tenta conectar ao Redis
    if not check_redis_connection():
        print("📝 Instalando Redis...")
        install_redis()
        
        # Aguarda o Redis iniciar
        print("⏳ Aguardando o Redis iniciar...")
        time.sleep(5)
        
        # Verifica novamente
        if not check_redis_connection():
            print("❌ Falha ao conectar com Redis após instalação")
            return
    
    print("✅ Redis está configurado e funcionando!")

if __name__ == "__main__":
    main() 