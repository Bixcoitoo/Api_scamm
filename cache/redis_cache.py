from redis import Redis
import json
from functools import wraps

redis_client = Redis(host='localhost', port=6379, db=1)

def cache_decorator(expire_time=3600):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Gera chave única baseada nos parâmetros
            cache_key = f"{func.__name__}:{str(args)}:{str(kwargs)}"
            
            # Verifica cache
            cached_result = redis_client.get(cache_key)
            if cached_result:
                return json.loads(cached_result)
            
            # Executa função e armazena resultado
            result = await func(*args, **kwargs)
            redis_client.setex(
                cache_key,
                expire_time,
                json.dumps(result)
            )
            return result
        return wrapper
    return decorator 