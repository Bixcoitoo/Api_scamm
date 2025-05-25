from pydantic_settings import BaseSettings
from functools import lru_cache

class ExternalAPISettings(BaseSettings):
    EXTERNAL_API_URL: str = "https://api.externa.com"
    EXTERNAL_API_KEY: str = "sua_api_key_aqui"
    
    # Campos do Firebase
    FIREBASE_PROJECT_ID: str = ""
    FIREBASE_PRIVATE_KEY_ID: str = ""
    FIREBASE_PRIVATE_KEY: str = ""
    FIREBASE_CLIENT_EMAIL: str = ""
    FIREBASE_CLIENT_ID: str = ""
    FIREBASE_CLIENT_CERT_URL: str = ""
    
    # Campos da API
    API_KEY: str = ""
    API_URL: str = ""
    
    # Campos do banco de dados
    DB_PATH: str = ""
    
    # Campos do Redis
    REDIS_HOST: str = "redis"
    REDIS_PORT: str = "6379"
    REDIS_DB: str = "0"
    
    # Ambiente
    ENVIRONMENT: str = "development"
    
    class Config:
        env_file = ".env"
        extra = "allow"  # Permite campos extras

@lru_cache()
def get_external_api_settings():
    return ExternalAPISettings() 