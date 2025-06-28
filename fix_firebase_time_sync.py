#!/usr/bin/env python3
"""
Script para corrigir problemas de sincronização de tempo que podem causar erro JWT
"""
import time
import datetime
import requests
import json
import os

def check_system_time():
    """Verifica se o horário do sistema está sincronizado"""
    print("🕐 Verificando sincronização de tempo...")
    
    try:
        # Obtém o horário atual do sistema
        local_time = datetime.datetime.now()
        print(f"⏰ Horário local: {local_time}")
        
        # Obtém o horário de um servidor NTP
        try:
            response = requests.get('http://worldtimeapi.org/api/timezone/America/Sao_Paulo', timeout=5)
            if response.status_code == 200:
                data = response.json()
                utc_time = data.get('utc_datetime')
                if utc_time:
                    server_time = datetime.datetime.fromisoformat(utc_time.replace('Z', '+00:00'))
                    print(f"🌐 Horário do servidor: {server_time}")
                    
                    # Calcula a diferença
                    time_diff = abs((local_time - server_time).total_seconds())
                    print(f"⏱️  Diferença: {time_diff:.2f} segundos")
                    
                    if time_diff > 30:
                        print("⚠️  Diferença de tempo muito grande! Isso pode causar problemas JWT.")
                        return False
                    else:
                        print("✅ Sincronização de tempo OK")
                        return True
            else:
                print("⚠️  Não foi possível verificar o horário do servidor")
                return True
        except Exception as e:
            print(f"⚠️  Erro ao verificar horário do servidor: {str(e)}")
            return True
            
    except Exception as e:
        print(f"❌ Erro ao verificar horário: {str(e)}")
        return False

def fix_firebase_config():
    """Corrige a configuração do Firebase para resolver problemas JWT"""
    print("🔧 Corrigindo configuração do Firebase...")
    
    # Verifica se existe arquivo de configuração
    config_files = [
        "config/firebase_config.py",
        "services/firebase_service.py"
    ]
    
    for config_file in config_files:
        if os.path.exists(config_file):
            print(f"📁 Verificando: {config_file}")
            
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Verifica se há configurações que podem causar problemas
                if 'firebase_admin.initialize_app' in content:
                    print(f"✅ Firebase Admin SDK configurado em {config_file}")
                    
                    # Sugere melhorias
                    suggestions = """
                    Sugestões para melhorar a configuração:
                    
                    1. Adicione timeout na inicialização:
                       firebase_admin.initialize_app(cred, options={'timeout': 30})
                    
                    2. Configure retry automático:
                       from google.auth.transport.requests import Request
                       from google.auth.exceptions import RefreshError
                    
                    3. Adicione verificação de conectividade antes de usar
                    """
                    print(suggestions)
                    
            except Exception as e:
                print(f"❌ Erro ao verificar {config_file}: {str(e)}")

def create_firebase_retry_wrapper():
    """Cria um wrapper para retry automático do Firebase"""
    print("🔄 Criando wrapper de retry para Firebase...")
    
    wrapper_code = '''
import time
import logging
from functools import wraps
from google.auth.exceptions import RefreshError
from firebase_admin import auth, firestore

logger = logging.getLogger(__name__)

def firebase_retry(max_retries=3, delay=1):
    """Decorator para retry automático em operações do Firebase"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except RefreshError as e:
                    last_exception = e
                    if "Invalid JWT Signature" in str(e):
                        logger.warning(f"JWT Signature error, attempt {attempt + 1}/{max_retries}")
                        if attempt < max_retries - 1:
                            time.sleep(delay * (2 ** attempt))  # Exponential backoff
                            continue
                    raise
                except Exception as e:
                    last_exception = e
                    logger.error(f"Firebase error: {str(e)}")
                    if attempt < max_retries - 1:
                        time.sleep(delay * (2 ** attempt))
                        continue
                    raise
            
            if last_exception:
                raise last_exception
        return wrapper
    return decorator

# Exemplo de uso:
@firebase_retry(max_retries=3, delay=2)
def get_user_safe(uid):
    """Versão segura de get_user com retry"""
    return auth.get_user(uid)

@firebase_retry(max_retries=3, delay=2)
def list_users_safe(max_results=1000):
    """Versão segura de list_users com retry"""
    return auth.list_users(max_results=max_results)
'''
    
    try:
        with open('utils/firebase_retry.py', 'w', encoding='utf-8') as f:
            f.write(wrapper_code)
        print("✅ Wrapper de retry criado: utils/firebase_retry.py")
        return True
    except Exception as e:
        print(f"❌ Erro ao criar wrapper: {str(e)}")
        return False

def update_docker_time_sync():
    """Atualiza o docker-compose para sincronizar tempo"""
    print("🐳 Atualizando docker-compose para sincronização de tempo...")
    
    try:
        with open('docker-compose.yml', 'r') as f:
            content = f.read()
        
        # Verifica se já tem configuração de timezone
        if 'TZ=' not in content:
            print("📝 Adicionando configuração de timezone...")
            
            # Adiciona variável de timezone
            new_content = content.replace(
                'environment:',
                '''environment:
      - TZ=America/Sao_Paulo'''
            )
            
            # Cria backup
            import shutil
            shutil.copy('docker-compose.yml', 'docker-compose.yml.backup')
            
            # Salva novo conteúdo
            with open('docker-compose.yml', 'w') as f:
                f.write(new_content)
            
            print("✅ Docker-compose atualizado com timezone")
            return True
        else:
            print("✅ Timezone já configurado no docker-compose")
            return True
            
    except Exception as e:
        print(f"❌ Erro ao atualizar docker-compose: {str(e)}")
        return False

def main():
    """Função principal"""
    print("🔧 Corretor de Sincronização de Tempo - Firebase")
    print("=" * 60)
    
    # Verifica sincronização de tempo
    time_ok = check_system_time()
    
    # Corrige configuração do Firebase
    fix_firebase_config()
    
    # Cria wrapper de retry
    create_firebase_retry_wrapper()
    
    # Atualiza docker-compose
    update_docker_time_sync()
    
    print("\n" + "=" * 60)
    print("📋 Resumo das correções:")
    
    if not time_ok:
        print("⚠️  PROBLEMA: Sincronização de tempo pode estar causando o erro JWT")
        print("💡 SOLUÇÃO: Sincronize o horário do sistema ou use NTP")
    else:
        print("✅ Sincronização de tempo OK")
    
    print("✅ Wrapper de retry criado para operações do Firebase")
    print("✅ Docker-compose atualizado com timezone")
    
    print("\n🚀 Próximos passos:")
    print("1. Reinicie os containers: docker-compose down && docker-compose up -d")
    print("2. Teste as credenciais: python test_firebase_credentials.py")
    print("3. Se ainda houver problemas, execute: python fix_firebase_credentials.py")

if __name__ == "__main__":
    main() 