from typing import AsyncContextManager
import asyncpg
from contextlib import asynccontextmanager

async def init_db():
    return await asyncpg.create_pool(
        user='seu_usuario',
        password='sua_senha',
        database='srs_db',
        host='localhost',
        port=5432,
        min_size=20,
        max_size=100
    )

@asynccontextmanager
async def get_db_connection() -> AsyncContextManager[asyncpg.Connection]:
    pool = await init_db()
    async with pool.acquire() as connection:
        yield connection 