import asyncio
import sys
from pathlib import Path
import os
import shutil

# Verifica permissões
db_path = Path(r"G:\SERASA DB")
if not os.access(db_path, os.R_OK):
    print(f"❌ Erro: Sem permissão de leitura em {db_path}")
    sys.exit(1)

# Verifica espaço em disco (compatível com Windows)
try:
    free_space = shutil.disk_usage(db_path).free
    required_space = 8 * 1024 * 1024 * 1024  # 8GB
    if free_space < required_space:
        print(f"❌ Erro: Espaço em disco insuficiente. Necessário: 8GB, Disponível: {free_space / (1024**3):.1f}GB")
        sys.exit(1)
except Exception as e:
    print(f"⚠️ Aviso: Não foi possível verificar espaço em disco: {e}")

# Adiciona o diretório raiz ao PYTHONPATH
root_dir = Path(__file__).parent.parent.parent
sys.path.append(str(root_dir))

from src.services.elasticsearch_service import ElasticsearchService

async def main():
    es_service = ElasticsearchService()
    
    if not await es_service.check_connection():
        print("❌ Erro: Elasticsearch não está rodando. Por favor, inicie o serviço primeiro.")
        return
        
    print("✅ Conectado ao Elasticsearch")
    await es_service.create_index()
    await es_service.index_data(batch_size=500)

if __name__ == "__main__":
    asyncio.run(main())
