import os
from dotenv import load_dotenv

# Carrega as variáveis de ambiente
load_dotenv()

REDIS_CONFIG = {
    'host': os.getenv('REDIS_HOST', 'redis'),  # Usando o nome do serviço do Docker
    'port': int(os.getenv('REDIS_PORT', 6379)),
    'db': int(os.getenv('REDIS_DB', 0)),
    'decode_responses': True,
    'socket_timeout': 5,
    'socket_connect_timeout': 5,
    'retry_on_timeout': True
}

# Configurações específicas para rate limiting
RATE_LIMIT_CONFIG = {
    'window_size': 60,  # 1 minuto em segundos
    'requests_per_minute': 60,
    'requests_per_hour': 1000
} 