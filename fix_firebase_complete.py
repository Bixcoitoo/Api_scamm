#!/usr/bin/env python3
"""
Script completo para corrigir problemas do Firebase
Combina todas as soluções em um único script
"""
import json
import os
import sys
import shutil
import webbrowser
from datetime import datetime
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class FirebaseFixer:
    def __init__(self):
        self.backup_created = False
        
    def create_backups(self):
        """Cria backups de todos os arquivos importantes"""
        print("💾 Criando backups...")
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        files_to_backup = [
            "scammapi-firebase-adminsdk-fbsvc-5a86f9cc92.json",
            "docker-compose.yml",
            "serviceAccountKey.json"
        ]
        
        for file_path in files_to_backup:
            if os.path.exists(file_path):
                backup_path = f"backup_{timestamp}_{os.path.basename(file_path)}"
                try:
                    shutil.copy2(file_path, backup_path)
                    print(f"✅ Backup criado: {backup_path}")
                    self.backup_created = True
                except Exception as e:
                    print(f"❌ Erro ao criar backup de {file_path}: {str(e)}")
                    
    def check_credentials_issue(self):
        """Verifica se há problema com as credenciais"""
        print("\n🔍 Analisando problema das credenciais...")
        
        cred_file = "scammapi-firebase-adminsdk-fbsvc-5a86f9cc92.json"
        
        if not os.path.exists(cred_file):
            print("❌ Arquivo de credenciais não encontrado")
            return True
            
        try:
            with open(cred_file, 'r') as f:
                cred_data = json.load(f)
                
            private_key = cred_data.get('private_key', '')
            
            # Verifica se a chave privada está corrompida
            if not private_key.endswith('-----END PRIVATE KEY-----'):
                print("❌ Chave privada corrompida - não termina corretamente")
                return True
                
            # Verifica se a chave tem o tamanho correto
            key_lines = [line for line in private_key.split('\n') if line.strip() and not line.startswith('-----')]
            if len(key_lines) < 20:
                print("❌ Chave privada truncada")
                return True
                
            print("✅ Chave privada parece estar OK")
            return False
            
        except Exception as e:
            print(f"❌ Erro ao verificar credenciais: {str(e)}")
            return True
            
    def open_firebase_console(self):
        """Abre o console do Firebase no navegador"""
        print("\n🌐 Abrindo Console do Firebase...")
        
        try:
            webbrowser.open("https://console.firebase.google.com/")
            print("✅ Console do Firebase aberto no navegador")
            return True
        except Exception as e:
            print(f"❌ Erro ao abrir navegador: {str(e)}")
            return False
            
    def show_regeneration_instructions(self):
        """Mostra instruções para regenerar credenciais"""
        print("\n" + "="*60)
        print("🔄 INSTRUÇÕES PARA REGENERAR CREDENCIAIS")
        print("="*60)
        
        instructions = """
1. No Console do Firebase (já aberto no navegador):
   - Selecione o projeto: scammapi
   - Clique no ícone de engrenagem (⚙️) ao lado de "Visão geral do projeto"
   - Vá para a aba "Contas de serviço"
   - Clique em "Gerar nova chave privada"
   - Confirme a ação
   - Baixe o arquivo JSON

2. Substitua o arquivo atual:
   - Renomeie o arquivo baixado para: scammapi-firebase-adminsdk-fbsvc-5a86f9cc92.json
   - Substitua o arquivo existente no projeto

3. Se o projeto foi deletado:
   - Crie um novo projeto no Firebase
   - Configure Authentication e Firestore
   - Gere novas credenciais de service account
   - Atualize o project_id no código se necessário

4. Após obter as novas credenciais:
   - Execute: python test_firebase_credentials.py
   - Se funcionar, execute: python update_docker_credentials.py
        """
        
        print(instructions)
        
    def create_update_script(self):
        """Cria script para atualizar credenciais no Docker"""
        print("\n📝 Criando script para atualizar Docker...")
        
        script_content = '''#!/usr/bin/env python3
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
        lines = content.split('\\n')
        new_lines = []
        
        for line in lines:
            if line.strip().startswith('- FIREBASE_SERVICE_ACCOUNT='):
                new_line = f'      - FIREBASE_SERVICE_ACCOUNT={cred_json}'
                new_lines.append(new_line)
            else:
                new_lines.append(line)
                
        # Salva o novo conteúdo
        new_content = '\\n'.join(new_lines)
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
'''
        
        try:
            with open('update_docker_credentials.py', 'w', encoding='utf-8') as f:
                f.write(script_content)
            print("✅ Script criado: update_docker_credentials.py")
            return True
        except Exception as e:
            print(f"❌ Erro ao criar script: {str(e)}")
            return False
            
    def show_final_instructions(self):
        """Mostra instruções finais"""
        print("\n" + "="*60)
        print("🎯 RESUMO DAS AÇÕES")
        print("="*60)
        
        print("✅ Backups criados (se aplicável)")
        print("✅ Console do Firebase aberto")
        print("✅ Script de atualização criado")
        
        print("\n📋 PRÓXIMOS PASSOS:")
        print("1. Siga as instruções acima para regenerar credenciais")
        print("2. Após obter novas credenciais, execute:")
        print("   python update_docker_credentials.py")
        print("3. Se tudo funcionar, os containers serão reiniciados automaticamente")
        print("4. Teste a aplicação: http://localhost:4200")
        
        print("\n🔧 COMANDOS ÚTEIS:")
        print("- Testar credenciais: python test_firebase_credentials.py")
        print("- Ver logs: docker-compose logs fastapi_app")
        print("- Parar containers: docker-compose down")
        print("- Iniciar containers: docker-compose up -d")
        
    def run_complete_fix(self):
        """Executa o processo completo de correção"""
        print("🔧 CORRETOR COMPLETO DO FIREBASE")
        print("="*60)
        
        # Cria backups
        self.create_backups()
        
        # Verifica problema das credenciais
        has_issue = self.check_credentials_issue()
        
        if has_issue:
            # Abre console do Firebase
            self.open_firebase_console()
            
            # Mostra instruções
            self.show_regeneration_instructions()
            
            # Cria script de atualização
            self.create_update_script()
            
            # Mostra instruções finais
            self.show_final_instructions()
        else:
            print("✅ Credenciais parecem estar OK")
            print("💡 Se ainda há problemas, pode ser questão de sincronização de tempo")
            print("🔧 Execute: python fix_firebase_time_sync.py")

def main():
    """Função principal"""
    fixer = FirebaseFixer()
    fixer.run_complete_fix()

if __name__ == "__main__":
    main() 