from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
import time
import redis
from typing import Dict, Tuple
import logging
from config.public_settings import PUBLIC_CONFIG
from config.redis_config import REDIS_CONFIG, RATE_LIMIT_CONFIG

logger = logging.getLogger(__name__)

class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app):
        super().__init__(app)
        try:
            self.redis_client = redis.Redis(**REDIS_CONFIG)
            # Testa a conexão
            self.redis_client.ping()
            logger.info("Conexão com Redis estabelecida com sucesso")
        except redis.ConnectionError as e:
            logger.error(f"Erro ao conectar com Redis: {str(e)}")
            self.redis_client = None
        
        self.rate_limits = RATE_LIMIT_CONFIG
        self.window_size = RATE_LIMIT_CONFIG['window_size']

    async def dispatch(self, request: Request, call_next) -> Response:
        # Se o Redis não estiver disponível, permite a requisição
        if not self.redis_client:
            logger.warning("Redis não disponível, rate limiting desativado")
            return await call_next(request)

        # Ignora rate limiting para endpoints de status e configuração
        if request.url.path in ['/api/status', '/api/config']:
            return await call_next(request)

        client_ip = request.client.host
        current_time = int(time.time())
        
        try:
            # Verifica limite por minuto
            minute_key = f"rate_limit:{client_ip}:minute:{current_time // self.window_size}"
            minute_count = int(self.redis_client.get(minute_key) or 0)
            
            if minute_count >= self.rate_limits['requests_per_minute']:
                logger.warning(f"Rate limit excedido para IP {client_ip} (minuto)")
                raise HTTPException(
                    status_code=429,
                    detail="Muitas requisições. Tente novamente em alguns segundos."
                )
            
            # Verifica limite por hora
            hour_key = f"rate_limit:{client_ip}:hour:{current_time // 3600}"
            hour_count = int(self.redis_client.get(hour_key) or 0)
            
            if hour_count >= self.rate_limits['requests_per_hour']:
                logger.warning(f"Rate limit excedido para IP {client_ip} (hora)")
                raise HTTPException(
                    status_code=429,
                    detail="Limite de requisições por hora excedido. Tente novamente mais tarde."
                )
            
            # Incrementa contadores
            pipe = self.redis_client.pipeline()
            pipe.incr(minute_key)
            pipe.incr(hour_key)
            pipe.expire(minute_key, self.window_size)
            pipe.expire(hour_key, 3600)  # 1 hora
            pipe.execute()
            
            # Adiciona headers de rate limit
            response = await call_next(request)
            response.headers["X-RateLimit-Limit-Minute"] = str(self.rate_limits['requests_per_minute'])
            response.headers["X-RateLimit-Remaining-Minute"] = str(self.rate_limits['requests_per_minute'] - minute_count - 1)
            response.headers["X-RateLimit-Limit-Hour"] = str(self.rate_limits['requests_per_hour'])
            response.headers["X-RateLimit-Remaining-Hour"] = str(self.rate_limits['requests_per_hour'] - hour_count - 1)
            
            return response
            
        except redis.RedisError as e:
            logger.error(f"Erro no Redis durante rate limiting: {str(e)}")
            # Em caso de erro no Redis, permite a requisição mas loga o erro
            return await call_next(request)
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Erro inesperado no rate limiting: {str(e)}")
            return await call_next(request) 