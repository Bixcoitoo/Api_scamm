import asyncio
from fastapi import HTTPException

async def executar_com_timeout(func, *args, timeout=30):
    """Executa uma função com timeout e cancela a tarefa se exceder o tempo"""
    try:
        # Cria uma task para poder cancelar
        task = asyncio.create_task(func(*args))
        
        # Aguarda com timeout
        result = await asyncio.wait_for(task, timeout=timeout)
        return result
        
    except asyncio.TimeoutError:
        # Cancela a task se ainda estiver rodando
        if not task.done():
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass
                
        raise HTTPException(
            status_code=408,
            detail=f"Tempo limite de consulta excedido ({timeout} segundos)"
        ) 