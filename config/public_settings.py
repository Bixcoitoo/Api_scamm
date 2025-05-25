from typing import Dict

PUBLIC_CONFIG: Dict = {
    "api_name": "API de Consulta SERASA",
    "version": "1.0.0",
    "environment": "production",
    "features": {
        "consulta_nome": True,
        "consulta_telefone": True,
        "consulta_cpf": True,
        "consulta_endereco": True
    },
    "rate_limits": {
        "requests_per_minute": 60,
        "requests_per_hour": 1000
    },
    "maintenance_mode": False,
    "allowed_origins": ["https://scammnet.site"]
} 