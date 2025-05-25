from pathlib import Path
import apsw
import logging
from config.settings import DATABASE_CONFIG, NETWORK_CONFIG
import os

logger = logging.getLogger(__name__)

def map_network_drive():
    """Mapeia o drive de rede se necessário"""
    try:
        if DATABASE_CONFIG['mode'] == 'network':
            if not os.path.exists(DATABASE_CONFIG['network_path']):
                # Comando para mapear unidade de rede no Windows
                os.system(f'net use Z: {DATABASE_CONFIG["network_path"]} /PERSISTENT:YES')
                logger.info(f"Drive de rede mapeado com sucesso: {DATABASE_CONFIG['network_path']}")
            return True
    except Exception as e:
        logger.error(f"Erro ao mapear drive de rede: {str(e)}")
        return False

def get_db_path():
    """Retorna o caminho correto do banco baseado na configuração"""
    if DATABASE_CONFIG['mode'] == 'local':
        return Path(DATABASE_CONFIG['local_path'])
    else:
        return Path(DATABASE_CONFIG['network_path'])
