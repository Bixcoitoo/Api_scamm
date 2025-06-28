#!/usr/bin/env python3
"""
Script para corrigir problemas com credenciais do Firebase
"""
import json
import os
import subprocess
import sys
from datetime import datetime

def check_project_status():
    """Verifica o status do projeto Firebase"""
    print("🔍 Verificando status do projeto Firebase...")
    
    # Verifica se o arquivo de credenciais existe
    cred_file = "scammapi-firebase-adminsdk-fbsvc-5a86f9cc92.json"
    if not os.path.exists(cred_file):
        print(f"❌ Arquivo de credenciais não encontrado: {cred_file}")
        return False
    
    # Carrega as credenciais
    try:
        with open(cred_file, 'r') as f:
            cred_data = json.load(f)
        
        project_id = cred_data.get('project_id')
        client_email = cred_data.get('client_email')
        
        print(f"📋 Project ID: {project_id}")
        print(f"📧 Client Email: {client_email}")
        
        return True
    except Exception as e:
        print(f"❌ Erro ao carregar credenciais: {str(e)}")
        return False

def backup_current_credentials():
    """Faz backup das credenciais atuais"""
    print("💾 Fazendo backup das credenciais atuais...")
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_file = f"backup_credentials_{timestamp}.json"
    
    try:
        if os.path.exists("scammapi-firebase-adminsdk-fbsvc-5a86f9cc92.json"):
            with open("scammapi-firebase-adminsdk-fbsvc-5a86f9cc92.json", 'r') as src:
                with open(backup_file, 'w') as dst:
                    dst.write(src.read())
            print(f"✅ Backup criado: {backup_file}")
            return True
    except Exception as e:
        print(f"❌ Erro ao criar backup: {str(e)}")
        return False

def generate_new_credentials():
    """Gera novas credenciais do Firebase"""
    print("🔄 Gerando novas credenciais...")
    
    instructions = """
    Para resolver o problema "Invalid JWT Signature", você precisa:

    1. Acessar o Console do Firebase: https://console.firebase.google.com/
    2. Selecionar o projeto: scammapi
    3. Ir em Configurações do Projeto (ícone de engrenagem)
    4. Aba "Contas de serviço"
    5. Clicar em "Gerar nova chave privada"
    6. Baixar o arquivo JSON
    7. Substituir o arquivo: scammapi-firebase-adminsdk-fbsvc-5a86f9cc92.json

    OU

    Se o projeto foi deletado:
    1. Criar um novo projeto no Firebase
    2. Configurar Authentication e Firestore
    3. Gerar novas credenciais de service account
    4. Atualizar o project_id no código
    """
    
    print(instructions)
    
    # Pergunta se o usuário quer abrir o console do Firebase
    response = input("\nDeseja abrir o Console do Firebase no navegador? (s/n): ")
    if response.lower() in ['s', 'sim', 'y', 'yes']:
        try:
            import webbrowser
            webbrowser.open("https://console.firebase.google.com/")
            print("🌐 Console do Firebase aberto no navegador")
        except Exception as e:
            print(f"❌ Erro ao abrir navegador: {str(e)}")

def update_docker_compose():
    """Atualiza o docker-compose.yml com novas credenciais"""
    print("🐳 Atualizando docker-compose.yml...")
    
    try:
        # Lê o arquivo atual
        with open("docker-compose.yml", 'r') as f:
            content = f.read()
        
        # Cria backup do docker-compose
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = f"backup_docker_compose_{timestamp}.yml"
        
        with open(backup_file, 'w') as f:
            f.write(content)
        
        print(f"✅ Backup do docker-compose criado: {backup_file}")
        
        instructions = """
        Para atualizar o docker-compose.yml:

        1. Após obter as novas credenciais do Firebase
        2. Abra o arquivo: scammapi-firebase-adminsdk-fbsvc-5a86f9cc92.json
        3. Copie todo o conteúdo JSON
        4. Abra o arquivo: docker-compose.yml
        5. Substitua a linha FIREBASE_SERVICE_ACCOUNT= com o novo JSON
        6. Certifique-se de que o JSON está entre aspas duplas
        """
        
        print(instructions)
        
    except Exception as e:
        print(f"❌ Erro ao atualizar docker-compose: {str(e)}")

def test_new_credentials():
    """Testa as novas credenciais"""
    print("🧪 Testando novas credenciais...")
    
    try:
        result = subprocess.run([sys.executable, "test_firebase_credentials.py"], 
                              capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Credenciais funcionando corretamente!")
            return True
        else:
            print("❌ Credenciais ainda com problemas")
            print("Output:", result.stdout)
            print("Error:", result.stderr)
            return False
            
    except Exception as e:
        print(f"❌ Erro ao testar credenciais: {str(e)}")
        return False

def main():
    """Função principal"""
    print("🔧 Corretor de Credenciais do Firebase")
    print("=" * 50)
    
    # Verifica status atual
    if not check_project_status():
        print("❌ Não foi possível verificar o status do projeto")
        return
    
    # Faz backup
    backup_current_credentials()
    
    # Gera novas credenciais
    generate_new_credentials()
    
    # Atualiza docker-compose
    update_docker_compose()
    
    print("\n" + "=" * 50)
    print("📝 Próximos passos:")
    print("1. Siga as instruções acima para obter novas credenciais")
    print("2. Substitua o arquivo de credenciais")
    print("3. Atualize o docker-compose.yml")
    print("4. Execute: python test_firebase_credentials.py")
    print("5. Se funcionar, reinicie os containers: docker-compose down && docker-compose up -d")
    
    # Pergunta se quer testar agora
    response = input("\nDeseja testar as credenciais agora? (s/n): ")
    if response.lower() in ['s', 'sim', 'y', 'yes']:
        test_new_credentials()

if __name__ == "__main__":
    main() 