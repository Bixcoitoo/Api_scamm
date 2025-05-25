import sqlite3
from pathlib import Path
from contextlib import contextmanager
import logging
from queue import Queue
import os

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

if not logger.handlers:
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter('%(asctime)s [%(levelname)s] %(message)s'))
    logger.addHandler(handler)

# Pool de conexões por banco
connection_pools = {
    "SRS_CONTATOS": Queue(maxsize=10),
    "SRS_EMAIL": Queue(maxsize=10),
    "SRS_HISTORICO_TELEFONES": Queue(maxsize=10),
    "SRS_TB_MODELOS_ANALYTICS_SCORE": Queue(maxsize=10),
    "SRS_TB_PIS": Queue(maxsize=10),
    "SRS_TB_PROFISSAO": Queue(maxsize=10),
    "SRS_TB_TSE": Queue(maxsize=10),
    "SRS_TB_UNIVERSITARIOS": Queue(maxsize=10),
    "SRS_MAPA_PARENTES_ANALYTICS": Queue(maxsize=10),
    "SRS_TB_IRPF": Queue(maxsize=10)
}

def create_db_connection(db_name: str):
    """Cria uma nova conexão com o banco de dados"""
    # Define o diretório base para os bancos de dados
    base_dir = os.getenv('DB_BASE_DIR', '/mnt/hdexterno')
    
    db_paths = {
        "SRS_CONTATOS": f"{base_dir}/SRS_CONTATOS.db/SRS_CONTATOS.db",
        "SRS_HISTORICO_TELEFONES": f"{base_dir}/SRS_HISTORICO_TELEFONES.db/SRS_HISTORICO_TELEFONES.db",
        "SRS_TB_ENDERECOS": f"{base_dir}/SRS_TB_ENDERECOS.db/SRS_TB_ENDERECOS.db",
        "SRS_TB_MODELOS_ANALYTICS_SCORE": f"{base_dir}/SRS_TB_MODELOS_ANALYTICS_SCORE.db/SRS_TB_MODELOS_ANALYTICS_SCORE.db",
        "SRS_MAPA_PARENTES_ANALYTICS": f"{base_dir}/SRS_MAPA_PARENTES_ANALYTICS.db/SRS_MAPA_PARENTES_ANALYTICS.db",
        "SRS_TB_PIS": f"{base_dir}/SRS_TB_PIS.db/SRS_TB_PIS.db",
        "SRS_TB_PROFISSAO": f"{base_dir}/SRS_TB_PROFISSAO.db/SRS_TB_PROFISSAO.db",
        "SRS_TB_TSE": f"{base_dir}/SRS_TB_TSE.db/SRS_TB_TSE.db",
        "SRS_TB_UNIVERSITARIOS": f"{base_dir}/SRS_TB_UNIVERSITARIOS.db/SRS_TB_UNIVERSITARIOS.db",
        "SRS_TB_IRPF": f"{base_dir}/SRS_TB_IRPF.db/SRS_TB_IRPF.db"
    }
    
    if db_name not in db_paths:
        raise ValueError(f"Banco de dados não configurado: {db_name}")
        
    db_path = Path(db_paths[db_name])
    
    # Cria o diretório pai se não existir
    db_path.parent.mkdir(parents=True, exist_ok=True)
    
    if not db_path.exists():
        logger.warning(f"Banco de dados não encontrado: {db_path}")
        # Cria um banco vazio se não existir
        conn = sqlite3.connect(str(db_path))
        conn.close()
        logger.info(f"Banco de dados vazio criado: {db_path}")
    
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()
    cursor.execute("PRAGMA temp_store=MEMORY")
    cursor.execute("PRAGMA cache_size=-2000000")
    cursor.execute("PRAGMA page_size=4096")
    cursor.execute("PRAGMA journal_mode=OFF")
    cursor.execute("PRAGMA synchronous=OFF")
    cursor.execute("PRAGMA locking_mode=NORMAL")
    cursor.execute("PRAGMA read_uncommitted=1")
    
    return conn

@contextmanager
def get_db_connection(db_name: str):
    conn = None
    try:
        try:
            conn = connection_pools[db_name].get_nowait()
            logger.debug(f"Reusando conexão do pool para {db_name}")
        except:
            logger.debug(f"Criando nova conexão para {db_name}")
            conn = create_db_connection(db_name)
        yield conn
    finally:
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute("SELECT 1")
                cursor.fetchone()
                connection_pools[db_name].put(conn)
                logger.debug(f"Devolvendo conexão ao pool de {db_name}")
            except:
                try:
                    conn.close()
                except:
                    pass
                logger.debug(f"Fechando conexão com erro de {db_name}") 