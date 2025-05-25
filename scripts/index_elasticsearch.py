import asyncio
import sys
from pathlib import Path
import os

# Corrige o caminho para importação
current_dir = Path(__file__).resolve().parent
src_dir = current_dir.parent
sys.path.append(str(src_dir))

from services.elasticsearch_service import ElasticsearchService

async def main():
    # Corrige o caminho do HD com barras normais
    es_service = ElasticsearchService("E:/Elastic_search")
    
    try:
        if not await es_service.check_connection():
            print("❌ Erro: Elasticsearch não está rodando")
            return
            
        print("✅ Conectado ao Elasticsearch")
        
        print("Criando índice...")
        await es_service.create_index()
        
        print("Iniciando indexação dos dados...")
        await es_service.index_data(batch_size=1000)
        
        print("✅ Indexação concluída com sucesso!")
        
    except Exception as e:
        print(f"❌ Erro durante a indexação: {str(e)}")

if __name__ == "__main__":
    asyncio.run(main()) 