from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

DATABASES = {
    'default': {
        'db_path': r'G:\SERASA DB\SRS_CONTATOS.db\SRS_CONTATOS.db',
        'pool_size': 10,
        'max_overflow': 20
    }
}

REDIS_CONFIG = {
    'host': 'localhost',
    'port': 6379,
    'db': 0
}

API_SETTINGS = {
    'rate_limit': 100,  # requisições por minuto
    'cache_timeout': 3600,  # 1 hora
    'max_connections': 100,
    'port': 3000,  # Adicionar porta padrão
    'protocol': 'http'  # Adicionar protocolo padrão
}

SECURITY = {
    'api_key': 'maria1316',
    'ssl_cert': 'certificates/certificate.pem',
    'ssl_key': 'certificates/private_key.pem'
}

NETWORK_CONFIG = {
    'db_server': {
        'host': '192.168.1.100',  # IP da máquina com o HD
        'port': 8000,  # Porta para o serviço de banco
        'shared_folder': r'\\COMPUTADOR\SERASA DB'  # Caminho de rede do HD
    }
}

DATABASE_CONFIG = {
    'mode': 'local',  # Mudando para local ao invés de network
    'local_path': r'G:\SERASA DB',
    'network_path': None  # Desabilitando caminho de rede
}

FEATURES = {
    'elasticsearch': False,  # Será True se elasticsearch estiver instalado
    'redis': False,  # Será True se redis estiver instalado
    'rate_limit': False,  # Será True se redis estiver instalado
}

try:
    import elasticsearch
    FEATURES['elasticsearch'] = True
except ImportError:
    pass

try:
    import redis
    FEATURES['redis'] = True
    FEATURES['rate_limit'] = True
except ImportError:
    pass 