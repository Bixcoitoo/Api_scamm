import os
import json
import logging
from pathlib import Path
from dotenv import load_dotenv

logger = logging.getLogger(__name__)

def get_firebase_credentials():
    """Obtém as credenciais do Firebase das variáveis de ambiente ou arquivo JSON"""
    try:
        # Carrega as variáveis de ambiente
        load_dotenv()
        
        # Primeiro tenta obter das variáveis de ambiente
        service_account_json = os.getenv('FIREBASE_SERVICE_ACCOUNT')
        
        if service_account_json:
            try:
                credentials = json.loads(service_account_json)
                logger.info("Credenciais do Firebase carregadas das variáveis de ambiente")
                return credentials
            except json.JSONDecodeError as e:
                logger.error(f"Erro ao decodificar JSON das credenciais do Firebase: {str(e)}")
        
        # Se não encontrar nas variáveis de ambiente, tenta carregar do arquivo JSON
        logger.info("Tentando carregar credenciais do arquivo JSON...")
        
        # Lista de possíveis locais do arquivo de credenciais
        possible_paths = [
            "scammapi-firebase-adminsdk-fbsvc-5a86f9cc92.json",
            "serviceAccountKey.json",
            "config/scammapi-firebase-adminsdk-fbsvc-5a86f9cc92.json",
            "config/serviceAccountKey.json"
        ]
        
        for file_path in possible_paths:
            if os.path.exists(file_path):
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        credentials = json.load(f)
                        logger.info(f"Credenciais do Firebase carregadas do arquivo: {file_path}")
                        return credentials
                except (json.JSONDecodeError, IOError) as e:
                    logger.error(f"Erro ao ler arquivo {file_path}: {str(e)}")
                    continue
        
        logger.error("Nenhuma credencial do Firebase encontrada (variável de ambiente ou arquivo JSON)")
        return None
            
    except Exception as e:
        logger.error(f"Erro ao obter credenciais do Firebase: {str(e)}")
        return None 