import os
import json
import logging
from dotenv import load_dotenv

logger = logging.getLogger(__name__)

def get_firebase_credentials():
    """Obtém as credenciais do Firebase das variáveis de ambiente"""
    try:
        # Carrega as variáveis de ambiente
        load_dotenv()
        
        # Obtém as credenciais da variável de ambiente
        service_account_json = os.getenv('FIREBASE_SERVICE_ACCOUNT')
        
        if not service_account_json:
            logger.error("FIREBASE_SERVICE_ACCOUNT não está definido nas variáveis de ambiente")
            return None
            
        # Converte a string JSON para um dicionário
        try:
            credentials = json.loads(service_account_json)
            return credentials
        except json.JSONDecodeError as e:
            logger.error(f"Erro ao decodificar JSON das credenciais do Firebase: {str(e)}")
            return None
            
    except Exception as e:
        logger.error(f"Erro ao obter credenciais do Firebase: {str(e)}")
        return None 