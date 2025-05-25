from fastapi import HTTPException, Request
try:
    from redis import Redis
    HAS_REDIS = True
except ImportError:
    HAS_REDIS = False
from starlette.middleware.base import BaseHTTPMiddleware

class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app):
        super().__init__(app)
        self.redis = Redis(host='localhost', port=6379, db=0) if HAS_REDIS else None
    
    async def dispatch(self, request: Request, call_next):
        if not self.redis:
            return await call_next(request)
            
        client_ip = request.client.host
        key = f"rate_limit:{client_ip}"
        
        # Limite de 100 requisições por minuto
        requests = self.redis.get(key)
        if requests and int(requests) > 100:
            raise HTTPException(status_code=429, detail="Muitas requisições")
            
        pipe = self.redis.pipeline()
        pipe.incr(key)
        pipe.expire(key, 60)
        pipe.execute()
        
        response = await call_next(request)
        return response 