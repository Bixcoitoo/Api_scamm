#!/usr/bin/env python3
import json
import os
import firebase_admin
from firebase_admin import credentials, auth
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_firebase_credentials():
    """Testa as credenciais do Firebase"""
    try:
        # Obtém as credenciais do arquivo JSON
        service_account_path = "scammapi-firebase-adminsdk-fbsvc-5a86f9cc92.json"
        
        if not os.path.exists(service_account_path):
            logger.error(f"Arquivo de credenciais não encontrado: {service_account_path}")
            return False
            
        # Carrega as credenciais do arquivo
        with open(service_account_path, 'r') as f:
            cred_data = json.load(f)
            
        logger.info("Credenciais carregadas com sucesso")
        logger.info(f"Project ID: {cred_data.get('project_id')}")
        logger.info(f"Client Email: {cred_data.get('client_email')}")
        
        # Verifica se a chave privada está presente
        private_key = cred_data.get('private_key')
        if not private_key:
            logger.error("Chave privada não encontrada nas credenciais")
            return False
            
        # Verifica se a chave privada tem o formato correto
        if not private_key.startswith('-----BEGIN PRIVATE KEY-----'):
            logger.error("Chave privada não tem o formato correto")
            return False
            
        logger.info("Chave privada tem formato válido")
        
        # Tenta inicializar o Firebase
        try:
            cred = credentials.Certificate(service_account_path)
            firebase_admin.initialize_app(cred)
            logger.info("Firebase inicializado com sucesso")
            
            # Testa uma operação simples
            try:
                # Tenta listar usuários (limitado a 1 para teste)
                users = auth.list_users(max_results=1)
                logger.info("Conexão com Firebase autenticada com sucesso")
                return True
            except Exception as e:
                logger.error(f"Erro ao testar autenticação: {str(e)}")
                return False
                
        except Exception as e:
            logger.error(f"Erro ao inicializar Firebase: {str(e)}")
            return False
            
    except Exception as e:
        logger.error(f"Erro geral: {str(e)}")
        return False

if __name__ == "__main__":
    success = test_firebase_credentials()
    if success:
        print("✅ Credenciais do Firebase estão funcionando corretamente")
    else:
        print("❌ Problema com as credenciais do Firebase") 