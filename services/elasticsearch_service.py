from elasticsearch import Elasticsearch
from pathlib import Path
import apsw
from typing import List, Dict
import logging
from database.connection import get_db_connection
from fastapi import HTTPException
import os

logger = logging.getLogger(__name__)

class ElasticsearchService:
    def __init__(self):
        try:
            # Inicializa o cliente do Elasticsearch
            self.es = Elasticsearch(
                hosts=['http://elasticsearch:9200'],
                verify_certs=False
            )
            logger.info("Elasticsearch inicializado com sucesso")
        except Exception as e:
            logger.error(f"Erro ao inicializar Elasticsearch: {str(e)}")
            raise
    
    def check_connection(self):
        """Verifica se a conexão com o Elasticsearch está funcionando"""
        try:
            return self.es.ping()
        except Exception as e:
            logger.error(f"Erro ao verificar conexão com Elasticsearch: {str(e)}")
            return False
    
    async def search_nome(self, nome: str, limit: int = 10):
        """Busca pessoas por nome"""
        try:
            query = {
                "query": {
                    "match": {
                        "nome": nome
                    }
                },
                "size": limit
            }
            
            response = self.es.search(
                index="pessoas",
                body=query
            )
            
            hits = response['hits']['hits']
            return [hit['_source'] for hit in hits]
            
        except Exception as e:
            logger.error(f"Erro ao buscar por nome: {str(e)}")
            raise
        
    async def create_index(self):
        settings = {
            "settings": {
                "index": {
                    "number_of_shards": 1,
                    "number_of_replicas": 0,
                    "codec": "best_compression"
                },
                "analysis": {
                    "analyzer": {
                        "nome_analyzer": {
                            "type": "custom",
                            "tokenizer": "standard",
                            "filter": ["lowercase", "asciifolding"]
                        }
                    }
                }
            },
            "mappings": {
                "properties": {
                    "nome": {
                        "type": "text",
                        "analyzer": "nome_analyzer"
                    },
                    "cpf": {
                        "type": "keyword"
                    },
                    "nascimento": {
                        "type": "date"
                    },
                    "sexo": {
                        "type": "keyword"
                    },
                    "nome_mae": {
                        "type": "text",
                        "analyzer": "nome_analyzer"
                    },
                    "nome_pai": {
                        "type": "text",
                        "analyzer": "nome_analyzer"
                    }
                }
            }
        }
        
        if not self.es.indices.exists(index=self.index_name):
            self.es.indices.create(index=self.index_name, body=settings)
            
    async def _get_telefones(self, contatos_id: str) -> List[str]:
        try:
            with get_db_connection("SRS_HISTORICO_TELEFONES") as tel_conn:
                tel_cursor = tel_conn.cursor()
                result = tel_cursor.execute("""
                    SELECT DISTINCT DDD || TELEFONE as telefone
                    FROM SRS_HISTORICO_TELEFONES 
                    WHERE CONTATOS_ID = ?
                """, (contatos_id,))
                
                return [row[0] for row in result.fetchall()]
                
        except Exception as e:
            logger.error(f"Erro ao buscar telefones: {str(e)}")
            return []
    
    async def index_data(self, batch_size: int = 1000):
        try:
            print("\n=== Iniciando indexação ===")
            
            if self.es.indices.exists(index=self.index_name):
                self.es.indices.delete(index=self.index_name)
                print("🗑️ Índice anterior removido")
            
            with get_db_connection("SRS_CONTATOS") as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT COUNT(*) FROM SRS_CONTATOS")
                total_registros = cursor.fetchone()[0]
                print(f"Total de registros a indexar: {total_registros:,}")
                
                offset = 0
                total_indexados = 0
                
                while True:
                    cursor.execute("""
                        SELECT NOME, CPF, NASC, SEXO, NOME_MAE, NOME_PAI
                        FROM SRS_CONTATOS 
                        LIMIT ? OFFSET ?
                    """, (batch_size, offset))
                    
                    rows = cursor.fetchall()
                    if not rows:
                        break
                    
                    actions = []
                    for row in rows:
                        # Converte a data para o formato ISO sem timezone
                        data_nascimento = row[2].split()[0] if row[2] else None
                        
                        doc = {
                            "nome": row[0],
                            "cpf": row[1],
                            "nascimento": data_nascimento,  # Apenas YYYY-MM-DD
                            "sexo": row[3],
                            "nome_mae": row[4],
                            "nome_pai": row[5] if row[5] != "N/A" else None
                        }
                        actions.extend([
                            {"index": {"_index": self.index_name}},
                            doc
                        ])
                    
                    if actions:
                        response = self.es.bulk(body=actions, refresh=True)
                        if response.get('errors'):
                            erros = [item for item in response['items'] if item['index'].get('error')]
                            print(f"❌ Erros na indexação do lote ({len(erros)} documentos):")
                            for erro in erros[:3]:
                                print(f"- {erro['index']['error']['reason']}")
                        else:
                            total_indexados += len(actions) // 2
                            print(f"✓ Indexados {total_indexados:,} de {total_registros:,} registros")
                    
                    offset += batch_size
                
            print(f"\n✅ Indexação concluída! Total de registros: {total_indexados:,}")
            
            # Força um refresh do índice
            self.es.indices.refresh(index=self.index_name)
            
            # Verifica o total indexado
            count = self.es.count(index=self.index_name)
            print(f"Total de documentos no Elasticsearch: {count['count']:,}")
                    
        except Exception as e:
            print(f"❌ Erro ao indexar dados: {str(e)}")
            raise

    async def _search_nome_sqlite(self, nome: str, limit: int = 10) -> List[Dict]:
        """Método de fallback para buscar por nome usando SQLite"""
        try:
            nomes = nome.strip().split()
            if len(nomes) < 2:
                raise HTTPException(
                    status_code=400,
                    detail="Por favor, forneça nome e sobrenome para busca"
                )

            with get_db_connection("SRS_CONTATOS") as conn, \
                 get_db_connection("SRS_HISTORICO_TELEFONES") as tel_conn:
                
                cursor = conn.cursor()
                cursor.execute("PRAGMA temp_store=MEMORY")
                cursor.execute("PRAGMA cache_size=-2000000")
                
                # Cria condições WHERE para cada parte do nome
                where_conditions = []
                params = []
                for parte_nome in nomes:
                    where_conditions.append("c.NOME LIKE ?")
                    params.append(f"%{parte_nome}%")
                
                where_clause = " AND ".join(where_conditions)
                
                tel_cursor = tel_conn.cursor()
                tel_cursor.execute("""
                    CREATE TEMP TABLE IF NOT EXISTS temp_telefones AS
                    SELECT CONTATOS_ID, GROUP_CONCAT(DDD || TELEFONE) as telefones
                    FROM SRS_HISTORICO_TELEFONES
                    GROUP BY CONTATOS_ID
                """)
                
                query = f"""
                    SELECT 
                        c.NOME, c.CPF, c.NASC, c.CONTATOS_ID,
                        COALESCE(t.telefones, '') as telefones
                    FROM SRS_CONTATOS c
                    LEFT JOIN temp_telefones t ON c.CONTATOS_ID = t.CONTATOS_ID
                    WHERE {where_clause}
                    LIMIT ?
                """
                
                params.append(limit)
                cursor.execute(query, params)
                
                results = []
                for row in cursor.fetchall():
                    results.append({
                        'nome': row[0],
                        'cpf': row[1],
                        'nascimento': row[2],
                        'contatos_id': row[3],
                        'telefones': row[4].split(',') if row[4] else []
                    })
                
                print(f"✓ Encontrados {len(results)} resultados via SQLite")
                return results
                
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Erro na busca SQLite por nome '{nome}': {str(e)}")
            return []
