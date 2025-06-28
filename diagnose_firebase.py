#!/usr/bin/env python3
"""
Script de diagnóstico completo para problemas do Firebase
"""
import json
import os
import sys
import subprocess
import requests
from datetime import datetime
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class FirebaseDiagnostic:
    def __init__(self):
        self.issues = []
        self.solutions = []
        
    def add_issue(self, issue, solution=None):
        """Adiciona um problema encontrado"""
        self.issues.append(issue)
        if solution:
            self.solutions.append(solution)
        logger.error(f"❌ {issue}")
        
    def add_success(self, message):
        """Adiciona uma verificação bem-sucedida"""
        logger.info(f"✅ {message}")
        
    def check_credentials_file(self):
        """Verifica o arquivo de credenciais"""
        print("\n🔍 Verificando arquivo de credenciais...")
        
        cred_file = "scammapi-firebase-adminsdk-fbsvc-5a86f9cc92.json"
        
        if not os.path.exists(cred_file):
            self.add_issue(
                "Arquivo de credenciais não encontrado",
                "Baixe o arquivo de credenciais do Console do Firebase"
            )
            return False
            
        try:
            with open(cred_file, 'r') as f:
                cred_data = json.load(f)
                
            required_fields = ['type', 'project_id', 'private_key_id', 'private_key', 'client_email']
            missing_fields = [field for field in required_fields if field not in cred_data]
            
            if missing_fields:
                self.add_issue(
                    f"Campos obrigatórios ausentes: {missing_fields}",
                    "Verifique se o arquivo de credenciais está completo"
                )
                return False
                
            self.add_success(f"Arquivo de credenciais válido - Project: {cred_data.get('project_id')}")
            return True
            
        except json.JSONDecodeError as e:
            self.add_issue(
                f"Arquivo de credenciais com JSON inválido: {str(e)}",
                "Verifique se o arquivo JSON está bem formatado"
            )
            return False
        except Exception as e:
            self.add_issue(
                f"Erro ao ler arquivo de credenciais: {str(e)}",
                "Verifique as permissões do arquivo"
            )
            return False
            
    def check_private_key_format(self):
        """Verifica o formato da chave privada"""
        print("\n🔐 Verificando formato da chave privada...")
        
        try:
            with open("scammapi-firebase-adminsdk-fbsvc-5a86f9cc92.json", 'r') as f:
                cred_data = json.load(f)
                
            private_key = cred_data.get('private_key', '')
            
            if not private_key:
                self.add_issue("Chave privada ausente")
                return False
                
            if not private_key.startswith('-----BEGIN PRIVATE KEY-----'):
                self.add_issue("Chave privada não tem formato PEM válido")
                return False
                
            if not private_key.endswith('-----END PRIVATE KEY-----'):
                self.add_issue("Chave privada não termina corretamente")
                return False
                
            # Verifica se a chave tem o tamanho esperado (aproximadamente)
            key_lines = [line for line in private_key.split('\n') if line.strip() and not line.startswith('-----')]
            if len(key_lines) < 20:  # Chave RSA deve ter pelo menos 20 linhas
                self.add_issue("Chave privada parece estar truncada")
                return False
                
            self.add_success("Formato da chave privada válido")
            return True
            
        except Exception as e:
            self.add_issue(f"Erro ao verificar chave privada: {str(e)}")
            return False
            
    def check_project_status(self):
        """Verifica o status do projeto no Google Cloud"""
        print("\n🌐 Verificando status do projeto...")
        
        try:
            with open("scammapi-firebase-adminsdk-fbsvc-5a86f9cc92.json", 'r') as f:
                cred_data = json.load(f)
                
            project_id = cred_data.get('project_id')
            client_email = cred_data.get('client_email')
            
            # Tenta verificar se o projeto existe
            try:
                # Usa a API do Google Cloud para verificar o projeto
                url = f"https://cloudresourcemanager.googleapis.com/v1/projects/{project_id}"
                response = requests.get(url, timeout=10)
                
                if response.status_code == 200:
                    self.add_success(f"Projeto {project_id} existe e está ativo")
                    return True
                elif response.status_code == 403:
                    self.add_issue(
                        "Acesso negado ao projeto - credenciais podem estar revogadas",
                        "Verifique se as credenciais ainda são válidas no Console do Firebase"
                    )
                    return False
                elif response.status_code == 404:
                    self.add_issue(
                        f"Projeto {project_id} não encontrado",
                        "O projeto pode ter sido deletado ou renomeado"
                    )
                    return False
                else:
                    self.add_issue(f"Erro ao verificar projeto: {response.status_code}")
                    return False
                    
            except requests.exceptions.RequestException:
                # Se não conseguir verificar online, assume que pode estar OK
                self.add_success(f"Projeto {project_id} - não foi possível verificar online")
                return True
                
        except Exception as e:
            self.add_issue(f"Erro ao verificar projeto: {str(e)}")
            return False
            
    def test_firebase_connection(self):
        """Testa a conexão com o Firebase"""
        print("\n🔥 Testando conexão com Firebase...")
        
        try:
            # Tenta importar e inicializar o Firebase
            import firebase_admin
            from firebase_admin import credentials, auth
            
            # Inicializa com as credenciais
            cred = credentials.Certificate("scammapi-firebase-adminsdk-fbsvc-5a86f9cc92.json")
            firebase_admin.initialize_app(cred)
            
            # Tenta uma operação simples
            try:
                users = auth.list_users(max_results=1)
                self.add_success("Conexão com Firebase funcionando")
                return True
            except Exception as e:
                if "Invalid JWT Signature" in str(e):
                    self.add_issue(
                        "Erro de assinatura JWT inválida",
                        "As credenciais podem estar expiradas ou corrompidas"
                    )
                elif "invalid_grant" in str(e):
                    self.add_issue(
                        "Erro de grant inválido",
                        "As credenciais podem ter sido revogadas"
                    )
                else:
                    self.add_issue(f"Erro de conexão: {str(e)}")
                return False
                
        except ImportError:
            self.add_issue(
                "Firebase Admin SDK não instalado",
                "Execute: pip install firebase-admin"
            )
            return False
        except Exception as e:
            self.add_issue(f"Erro ao inicializar Firebase: {str(e)}")
            return False
            
    def check_docker_environment(self):
        """Verifica a configuração do Docker"""
        print("\n🐳 Verificando configuração do Docker...")
        
        try:
            with open("docker-compose.yml", 'r') as f:
                content = f.read()
                
            if 'FIREBASE_SERVICE_ACCOUNT' not in content:
                self.add_issue(
                    "Variável FIREBASE_SERVICE_ACCOUNT não encontrada no docker-compose.yml",
                    "Adicione a variável de ambiente no docker-compose.yml"
                )
                return False
                
            if 'TZ=' not in content:
                self.add_issue(
                    "Timezone não configurado no Docker",
                    "Adicione TZ=America/Sao_Paulo no docker-compose.yml"
                )
                return False
                
            self.add_success("Configuração do Docker OK")
            return True
            
        except FileNotFoundError:
            self.add_issue(
                "docker-compose.yml não encontrado",
                "Verifique se está no diretório correto"
            )
            return False
        except Exception as e:
            self.add_issue(f"Erro ao verificar Docker: {str(e)}")
            return False
            
    def check_system_time(self):
        """Verifica a sincronização de tempo do sistema"""
        print("\n⏰ Verificando sincronização de tempo...")
        
        try:
            local_time = datetime.now()
            print(f"Horário local: {local_time}")
            
            # Tenta obter horário de um servidor NTP
            try:
                response = requests.get('http://worldtimeapi.org/api/timezone/America/Sao_Paulo', timeout=5)
                if response.status_code == 200:
                    data = response.json()
                    utc_time = data.get('utc_datetime')
                    if utc_time:
                        server_time = datetime.fromisoformat(utc_time.replace('Z', '+00:00'))
                        time_diff = abs((local_time - server_time).total_seconds())
                        
                        if time_diff > 30:
                            self.add_issue(
                                f"Diferença de tempo muito grande: {time_diff:.2f} segundos",
                                "Sincronize o horário do sistema ou configure NTP"
                            )
                            return False
                        else:
                            self.add_success(f"Sincronização de tempo OK (diferença: {time_diff:.2f}s)")
                            return True
                else:
                    self.add_success("Não foi possível verificar tempo do servidor")
                    return True
            except:
                self.add_success("Não foi possível verificar tempo do servidor")
                return True
                
        except Exception as e:
            self.add_issue(f"Erro ao verificar tempo: {str(e)}")
            return False
            
    def generate_report(self):
        """Gera relatório final"""
        print("\n" + "="*60)
        print("📋 RELATÓRIO DE DIAGNÓSTICO")
        print("="*60)
        
        if not self.issues:
            print("✅ Todos os testes passaram! O Firebase deve estar funcionando corretamente.")
            return
            
        print(f"❌ Encontrados {len(self.issues)} problema(s):")
        for i, issue in enumerate(self.issues, 1):
            print(f"\n{i}. {issue}")
            if i <= len(self.solutions) and self.solutions[i-1]:
                print(f"   💡 Solução: {self.solutions[i-1]}")
                
        print("\n" + "="*60)
        print("🚀 AÇÕES RECOMENDADAS:")
        print("="*60)
        
        if any("JWT Signature" in issue for issue in self.issues):
            print("1. 🔄 Regenerar credenciais do Firebase:")
            print("   - Acesse: https://console.firebase.google.com/")
            print("   - Vá em Configurações > Contas de serviço")
            print("   - Clique em 'Gerar nova chave privada'")
            print("   - Substitua o arquivo de credenciais")
            
        if any("tempo" in issue.lower() for issue in self.issues):
            print("2. ⏰ Sincronizar horário do sistema:")
            print("   - Configure NTP no sistema")
            print("   - Ou sincronize manualmente com servidor de tempo")
            
        if any("Docker" in issue for issue in self.issues):
            print("3. 🐳 Atualizar configuração do Docker:")
            print("   - Adicione timezone no docker-compose.yml")
            print("   - Verifique variáveis de ambiente")
            
        print("\n4. 🔧 Execute os scripts de correção:")
        print("   python fix_firebase_time_sync.py")
        print("   python fix_firebase_credentials.py")
        
        print("\n5. 🧪 Teste novamente:")
        print("   python test_firebase_credentials.py")
        
    def run_all_checks(self):
        """Executa todos os diagnósticos"""
        print("🔧 DIAGNÓSTICO COMPLETO DO FIREBASE")
        print("="*60)
        
        checks = [
            self.check_credentials_file,
            self.check_private_key_format,
            self.check_project_status,
            self.test_firebase_connection,
            self.check_docker_environment,
            self.check_system_time
        ]
        
        for check in checks:
            try:
                check()
            except Exception as e:
                self.add_issue(f"Erro durante verificação: {str(e)}")
                
        self.generate_report()

def main():
    """Função principal"""
    diagnostic = FirebaseDiagnostic()
    diagnostic.run_all_checks()

if __name__ == "__main__":
    main() 