from contextlib import asynccontextmanager
import asyncio
from typing import Dict
import signal
import sys
from fastapi import HTTPException
import logging
import time
from datetime import datetime

# Configuração do logger para usar UTF-8
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('app.log', encoding='utf-8')
    ]
)
logger = logging.getLogger(__name__)

class ConnectionManager:
    def __init__(self):
        self._active_connections: Dict[str, asyncio.Task] = {}
        self._shutdown_event = asyncio.Event()
        self._last_reconnect = time.time()
        self._setup_signal_handlers()
        logger.info("ConnectionManager iniciado")
        
    def _setup_signal_handlers(self):
        for sig in (signal.SIGTERM, signal.SIGINT):
            signal.signal(sig, self._handle_shutdown)
            
    def _handle_shutdown(self, signum, frame):
        logger.info("Iniciando desligamento gracioso...")
        self._shutdown_event.set()
        self._cancel_all_connections()
        sys.exit(0)
        
    def _cancel_all_connections(self):
        for conn_id, task in self._active_connections.items():
            if not task.done():
                logger.info(f"Cancelando conexão {conn_id}")
                task.cancel()
                
    async def check_reconnect(self):
        current_time = time.time()
        elapsed = current_time - self._last_reconnect
        
        # Formatação da mensagem sem emojis para evitar problemas de encoding
        logger.info(f"""
[RECONEXAO] Executando reconexão programada
[TEMPO] Última reconexão: {time.strftime('%H:%M:%S', time.localtime(self._last_reconnect))}
[STATUS] Conexões ativas: {len(self._active_connections)}
""")
        
        if elapsed >= 5:  # 5 segundos
            logger.info(f"""
🔄 Executando reconexão programada
⏱️ Última reconexão: {datetime.fromtimestamp(self._last_reconnect).strftime('%H:%M:%S')}
📊 Conexões ativas: {len(self._active_connections)}
""")
            self._last_reconnect = current_time
            self._cancel_all_connections()
            return True
        return False

    async def track_connection(self, conn_id: str, coro, timeout: int = 300):
        if self._shutdown_event.is_set():
            raise HTTPException(
                status_code=503, 
                detail="Servidor em processo de desligamento"
            )
            
        try:
            await self.check_reconnect()
            
            task = asyncio.create_task(coro)
            self._active_connections[conn_id] = task
            
            result = await asyncio.wait_for(task, timeout=timeout)
            return result
            
        except asyncio.TimeoutError:
            if conn_id in self._active_connections:
                self._active_connections[conn_id].cancel()
                del self._active_connections[conn_id]
            raise HTTPException(
                status_code=408,
                detail="Tempo limite da requisição excedido (5 minutos)"
            )
            
        finally:
            if conn_id in self._active_connections:
                del self._active_connections[conn_id]

connection_manager = ConnectionManager() 