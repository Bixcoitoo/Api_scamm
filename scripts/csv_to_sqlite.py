import sqlite3
import pandas as pd
from pathlib import Path
import logging
import os

# Configuração do logger
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger(__name__)

def convert_csv_to_sqlite():
    try:
        # Caminhos dos arquivos
        csv_path = Path(r"G:\SERASA DB\serasa_enderecos\srs_enderecos.csv")
        db_dir = Path(r"F:\SRS_TB_ENDERECOS")
        db_path = db_dir / "SRS_TB_ENDERECOS.db"
        
        # Criar diretório se não existir
        if not db_dir.exists():
            logger.info(f"Criando diretório {db_dir}")
            os.makedirs(db_dir, exist_ok=True)
        
        # Verificar permissões
        if not os.access(db_dir, os.W_OK):
            logger.error(f"Sem permissão de escrita em {db_dir}")
            raise PermissionError(f"Sem permissão de escrita em {db_dir}")
        
        # Ler primeira linha do CSV para pegar os nomes das colunas
        df_sample = pd.read_csv(csv_path, nrows=1)
        columns = df_sample.columns.tolist()
        
        logger.info(f"Colunas encontradas no CSV: {columns}")
        
        # Criar conexão com o banco SQLite
        logger.info(f"Criando banco de dados em {db_path}")
        conn = sqlite3.connect(str(db_path))
        
        # Criar tabela dinamicamente com as colunas do CSV
        columns_sql = ", ".join([f"{col} TEXT" for col in columns])
        create_table_sql = f"""
            CREATE TABLE IF NOT EXISTS enderecos (
                {columns_sql}
            )
        """
        
        logger.info("Criando tabela e índice...")
        conn.execute(create_table_sql)
        conn.execute("CREATE INDEX IF NOT EXISTS idx_contatos_id ON enderecos(CONTATOS_ID)")
        
        # Ler e inserir em chunks
        chunksize = 100000
        total_rows = 0
        
        logger.info(f"Iniciando conversão do arquivo {csv_path}")
        for chunk in pd.read_csv(csv_path, chunksize=chunksize, low_memory=False):
            chunk.to_sql('enderecos', conn, if_exists='append', index=False)
            total_rows += len(chunk)
            logger.info(f"Processadas {total_rows:,} linhas...")
            
        # Otimizar banco
        logger.info("Otimizando banco de dados...")
        conn.execute("VACUUM")
        conn.execute("ANALYZE")
        
        conn.close()
        logger.info("Conversão concluída com sucesso!")
        
    except Exception as e:
        logger.error(f"Erro durante a conversão: {str(e)}")
        raise

if __name__ == "__main__":
    convert_csv_to_sqlite() 