
import time
import logging
from functools import wraps
from google.auth.exceptions import RefreshError
from firebase_admin import auth, firestore

logger = logging.getLogger(__name__)

def firebase_retry(max_retries=3, delay=1):
    """Decorator para retry automático em operações do Firebase"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except RefreshError as e:
                    last_exception = e
                    if "Invalid JWT Signature" in str(e):
                        logger.warning(f"JWT Signature error, attempt {attempt + 1}/{max_retries}")
                        if attempt < max_retries - 1:
                            time.sleep(delay * (2 ** attempt))  # Exponential backoff
                            continue
                    raise
                except Exception as e:
                    last_exception = e
                    logger.error(f"Firebase error: {str(e)}")
                    if attempt < max_retries - 1:
                        time.sleep(delay * (2 ** attempt))
                        continue
                    raise
            
            if last_exception:
                raise last_exception
        return wrapper
    return decorator

# Exemplo de uso:
@firebase_retry(max_retries=3, delay=2)
def get_user_safe(uid):
    """Versão segura de get_user com retry"""
    return auth.get_user(uid)

@firebase_retry(max_retries=3, delay=2)
def list_users_safe(max_results=1000):
    """Versão segura de list_users com retry"""
    return auth.list_users(max_results=max_results)
