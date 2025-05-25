import asyncio
import asyncpg
import apsw
from pathlib import Path

async def migrate_data():
    # Conexão com PostgreSQL
    pg_conn = await asyncpg.connect(
        user='seu_usuario',
        password='sua_senha',
        database='srs_db',
        host='localhost'
    )
    
    # Conexão com SQLite
    sqlite_conn = apsw.Connection("SRS_CONTATOS")
    cursor = sqlite_conn.cursor()
    
    try:
        # Migra em lotes de 10000
        batch_size = 10000
        offset = 0
        
        while True:
            # Lê do SQLite
            cursor.execute("""
                SELECT NOME, CPF, NASC, NOME_MAE, NOME_PAI, SEXO, CONTATOS_ID
                FROM SRS_CONTATOS 
                LIMIT ? OFFSET ?
            """, (batch_size, offset))
            
            rows = cursor.fetchall()
            if not rows:
                break
                
            # Insere no PostgreSQL
            await pg_conn.executemany("""
                INSERT INTO srs_contatos (nome, cpf, nasc, nome_mae, nome_pai, sexo, contatos_id)
                VALUES ($1, $2, $3, $4, $5, $6, $7)
            """, rows)
            
            print(f"Migrados {offset + len(rows)} registros")
            offset += batch_size
            
    finally:
        await pg_conn.close()
        sqlite_conn.close()

if __name__ == "__main__":
    asyncio.run(migrate_data()) 