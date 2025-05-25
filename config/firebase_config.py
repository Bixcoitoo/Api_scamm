import os
from pathlib import Path

FIREBASE_CONFIG = {
    'type': 'service_account',
    'project_id': 'scammapi',
    'private_key_id': os.getenv('FIREBASE_PRIVATE_KEY_ID'),
    'private_key': os.getenv('FIREBASE_PRIVATE_KEY').replace('\\n', '\n'),
    'client_email': os.getenv('FIREBASE_CLIENT_EMAIL'),
    'client_id': '306542693551',
    'auth_uri': 'https://accounts.google.com/o/oauth2/auth',
    'token_uri': 'https://oauth2.googleapis.com/token',
    'auth_provider_x509_cert_url': 'https://www.googleapis.com/oauth2/v1/certs',
    'client_x509_cert_url': os.getenv('FIREBASE_CLIENT_CERT_URL'),
    'storageBucket': 'scammapi.firebasestorage.app'
}

# Gera o arquivo serviceAccountKey.json
def generate_service_account_file():
    service_account_path = Path('serviceAccountKey.json')
    import json
    
    with open(service_account_path, 'w') as f:
        json.dump(FIREBASE_CONFIG, f, indent=2)
    
    return service_account_path 