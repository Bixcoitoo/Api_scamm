import logging
from logging.handlers import RotatingFileHandler
import os
from datetime import datetime
import json

def setup_logger():
    # Cria diretório de logs se não existir
    log_dir = 'logs'
    os.makedirs(log_dir, exist_ok=True)
    
    # Configura logger principal
    logger = logging.getLogger('api')
    logger.setLevel(logging.INFO)
    
    # Handler para arquivo
    log_file = f"{log_dir}/api_{datetime.now().strftime('%Y%m')}.log"
    file_handler = RotatingFileHandler(
        log_file,
        maxBytes=10485760,  # 10MB
        backupCount=5
    )
    
    # Handler para console
    console_handler = logging.StreamHandler()
    
    # Formato do log
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)
    
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger

# Loggers específicos
transaction_logger = logging.getLogger('transactions')
error_logger = logging.getLogger('errors')
security_logger = logging.getLogger('security')

class APILogger:
    @staticmethod
    def log_request(request_data, response_data, user_id):
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'user_id': user_id,
            'request': request_data,
            'response': response_data
        }
        logging.info(json.dumps(log_entry)) 