#!/usr/bin/env python3
"""
Script para atualizar credenciais no docker-compose.yml
Execute após obter novas credenciais do Firebase
"""
import json
import os
import shutil
from datetime import datetime

def update_docker_credentials():
    """Atualiza as credenciais no docker-compose.yml"""
    print("🐳 Atualizando credenciais no Docker...")
    
    # Verifica se o arquivo de credenciais existe
    cred_file = "scammapi-firebase-adminsdk-fbsvc-5a86f9cc92.json"
    if not os.path.exists(cred_file):
        print("❌ Arquivo de credenciais não encontrado")
        return False
        
    try:
        # Lê as novas credenciais
        with open(cred_file, 'r') as f:
            cred_data = json.load(f)
            
        # Converte para string JSON
        cred_json = json.dumps(cred_data)
        
        # Lê o docker-compose atual
        with open('docker-compose.yml', 'r') as f:
            content = f.read()
            
        # Cria backup
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = f"backup_docker_compose_{timestamp}.yml"
        shutil.copy2('docker-compose.yml', backup_file)
        print(f"✅ Backup criado: {backup_file}")
        
        # Substitui a linha FIREBASE_SERVICE_ACCOUNT
        lines = content.split('\n')
        new_lines = []
        
        for line in lines:
            if line.strip().startswith('- FIREBASE_SERVICE_ACCOUNT='):
                new_line = f'      - FIREBASE_SERVICE_ACCOUNT={cred_json}'
                new_lines.append(new_line)
            else:
                new_lines.append(line)
                
        # Salva o novo conteúdo
        new_content = '\n'.join(new_lines)
        with open('docker-compose.yml', 'w') as f:
            f.write(new_content)
            
        print("✅ Docker-compose atualizado com novas credenciais")
        return True
        
    except Exception as e:
        print(f"❌ Erro ao atualizar Docker: {str(e)}")
        return False

def test_credentials():
    """Testa as credenciais atualizadas"""
    print("🧪 Testando credenciais...")
    
    try:
        import subprocess
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

def restart_containers():
    """Reinicia os containers Docker"""
    print("🔄 Reiniciando containers...")
    
    try:
        import subprocess
        
        # Para os containers
        print("Parando containers...")
        subprocess.run(["docker-compose", "down"], check=True)
        
        # Inicia os containers
        print("Iniciando containers...")
        subprocess.run(["docker-compose", "up", "-d"], check=True)
        
        print("✅ Containers reiniciados com sucesso")
        return True
        
    except Exception as e:
        print(f"❌ Erro ao reiniciar containers: {str(e)}")
        return False

def main():
    """Função principal"""
    print("🔧 Atualizador de Credenciais do Firebase")
    print("="*50)
    
    # Atualiza credenciais no Docker
    if update_docker_credentials():
        # Testa as credenciais
        if test_credentials():
            # Reinicia containers
            restart_containers()
        else:
            print("⚠️  Credenciais ainda com problemas. Verifique manualmente.")
    else:
        print("❌ Falha ao atualizar credenciais")

if __name__ == "__main__":
    main()
