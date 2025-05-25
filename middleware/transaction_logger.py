from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
import logging
import time
from datetime import datetime

logger = logging.getLogger('transactions')

class TransactionLoggerMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        
        # Log da requisição
        transaction_id = f"{datetime.now().strftime('%Y%m%d%H%M%S')}-{request.client.host}"
        
        logger.info(f"""
        Transaction Start:
        ID: {transaction_id}
        Method: {request.method}
        URL: {request.url}
        Client: {request.client.host}
        User-Agent: {request.headers.get('user-agent')}
        """)
        
        try:
            response = await call_next(request)
            
            # Log do resultado
            process_time = time.time() - start_time
            logger.info(f"""
            Transaction Complete:
            ID: {transaction_id}
            Status: {response.status_code}
            Duration: {process_time:.2f}s
            """)
            
            return response
            
        except Exception as e:
            logger.error(f"""
            Transaction Failed:
            ID: {transaction_id}
            Error: {str(e)}
            Duration: {time.time() - start_time:.2f}s
            """)
            raise 