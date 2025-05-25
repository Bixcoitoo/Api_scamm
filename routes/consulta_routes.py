from fastapi import APIRouter, Depends, HTTPException, Query, Body
from fastapi.security.api_key import APIKeyHeader
from typing import List, Optional, Dict
from config.settings import SECURITY, DATABASES
from validators.cpf_validator import CPFValidator
from cache.redis_cache import cache_decorator
import apsw
from pathlib import Path
from services.firebase_service import FirebaseService
from pydantic import BaseModel, Field, ValidationError
import unicodedata
import logging
from services.pessoa_service import (
    get_emails, get_telefones, get_score, get_pis,
    get_profissao, get_dados_universitarios, get_dados_eleitorais,
    get_parentes, get_irpf, get_endereco, _consulta_cpf as consulta_cpf_service
)
from database.connection import get_db_connection
from utils.timeout import executar_com_timeout
import asyncio

try:
    from services.elasticsearch_service import ElasticsearchService
    HAS_ELASTICSEARCH = True
except ImportError:
    HAS_ELASTICSEARCH = False

router = APIRouter()
api_key_header = APIKeyHeader(name="X-API-Key")
firebase_service = FirebaseService()
logger = logging.getLogger(__name__)



def remover_acentos(texto: str) -> str:
    return ''.join(c for c in unicodedata.normalize('NFD', texto)
                  if unicodedata.category(c) != 'Mn')

async def _consulta_cpf(cpf: str, api_key: str):
    return await consulta_cpf_service(cpf, api_key)

async def _consulta_nome(nome: str, api_key: str, limit: int = 10):
    if not HAS_ELASTICSEARCH:
        raise HTTPException(
            status_code=501,
            detail="Busca por nome não disponível - Elasticsearch não instalado"
        )
    
    nome = remover_acentos(nome).upper()
    print(f"\n=== Iniciando consulta para nome: {nome} ===")
    
    try:
        # Validação de nome + sobrenome
        nomes = nome.strip().split()
        if len(nomes) < 2:
            raise HTTPException(
                status_code=400,
                detail="Por favor, forneça nome e sobrenome para busca"
            )

        conn = get_db_connection("SRS_CONTATOS")
        cursor = conn.cursor()
        
        result = cursor.execute("""
            SELECT NOME, CPF, NASC, NOME_MAE, NOME_PAI, SEXO 
            FROM SRS_CONTATOS 
            WHERE NOME LIKE ? 
            LIMIT ?
        """, (f"%{nome}%", limit))
        
        pessoas = []
        for row in result:
            pessoas.append({
                "nome": row[0],
                "cpf": row[1],
                "nascimento": row[2],
                "nome_mae": row[3],
                "nome_pai": row[4],
                "sexo": row[5]
            })
            
        return pessoas
    finally:
        conn.close()

async def _consulta_telefone(telefone: str, api_key: str):
    with get_db_connection("SRS_HISTORICO_TELEFONES") as conn:
        cursor = conn.cursor()
        
        try:
            result = cursor.execute("""
                SELECT NOME, CPF, NASC, NOME_MAE, NOME_PAI, SEXO 
                FROM SRS_CONTATOS 
                WHERE CPF IN (
                    SELECT CPF FROM SRS_HISTORICO_TELEFONES 
                    WHERE TELEFONE = ?
                )
            """, (telefone,))
            
            pessoas = []
            for row in result:
                pessoas.append({
                    "nome": row[0],
                    "cpf": row[1],
                    "nascimento": row[2],
                    "nome_mae": row[3],
                    "nome_pai": row[4],
                    "sexo": row[5]
                })
            
            return pessoas
        finally:
            cursor.close()

class ConsultaCPFRequest(BaseModel):
    cpf: str = Field(
        ..., 
        min_length=11, 
        max_length=11,
        description="CPF sem pontuação"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "cpf": "12345678901"
            }
        }

@router.post("/consulta/cpf")
async def consulta_cpf(
    user_id: str = Query(..., description="ID do usuário no Firebase"),
    api_key: str = Depends(api_key_header),
    payload: ConsultaCPFRequest = Body(...)
):
    try:
        logger.info(f"Recebido request para CPF")
        logger.info(f"User ID: {user_id}")
        logger.info(f"Payload CPF: {payload.cpf}")
        
        # Verifica saldo antes da consulta
        await firebase_service.verificar_saldo(user_id, "cpf")
        
        # Executa a consulta usando o service
        result = await consulta_cpf_service(payload.cpf, api_key)
        logger.info("Consulta realizada com sucesso")
        return result
        
    except ValidationError as e:
        logger.error(f"Erro de validação: {str(e)}")
        raise HTTPException(
            status_code=422,
            detail={
                "code": "VALIDATION_ERROR",
                "message": str(e)
            }
        )
    except Exception as e:
        logger.error(f"Erro na consulta: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail={
                "code": "INTERNAL_ERROR",
                "message": str(e)
            }
        )

@router.get("/consulta/", response_model=List[Dict])
async def consulta_nome(
    nome: str = Query(..., min_length=3),
    limit: int = Query(default=10, le=100),
    api_key: str = Depends(api_key_header)
):
    """Consulta pessoas por nome"""
    if api_key != SECURITY["API_KEY"]:
        raise HTTPException(status_code=403, detail="Chave API inválida")
        
    try:
        with get_db_connection("SRS_CONTATOS") as conn:
            cursor = conn.cursor()
            nome_busca = f"%{remover_acentos(nome.upper())}%"
            
            result = cursor.execute("""
                SELECT NOME, CPF, NASC, NOME_MAE, NOME_PAI, SEXO 
                FROM SRS_CONTATOS 
                WHERE NOME LIKE ? 
                LIMIT ?
            """, (nome_busca, limit))
            
            pessoas = []
            for row in result:
                pessoas.append({
                    "nome": row[0],
                    "cpf": row[1],
                    "nascimento": row[2],
                    "nome_mae": row[3],
                    "nome_pai": row[4],
                    "sexo": row[5]
                })
                
            if not pessoas:
                raise HTTPException(
                    status_code=404,
                    detail="Nenhuma pessoa encontrada"
                )
                
            return pessoas
            
    except Exception as e:
        logger.error(f"Erro na consulta por nome: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail={"code": "SEARCH_ERROR", "message": str(e)}
        )

@router.post("/consulta/nome", response_model=List[Dict])
async def consulta_nome_post(
    nome: str = Query(..., min_length=3),
    user_id: str = Query(..., description="ID do usuário no Firebase"),
    limit: int = Query(default=10, le=100),
    api_key: str = Depends(api_key_header)
):
    """Consulta pessoas por nome (POST)"""
    try:
        # Verifica saldo antes da consulta
        await firebase_service.verificar_saldo(user_id, "nome", {"nome": nome})
        
        logger.info(f"Iniciando consulta para nome: {nome}")
        
        with get_db_connection("SRS_CONTATOS") as conn:
            cursor = conn.cursor()
            
            # Otimizações SQLite
            cursor.execute("PRAGMA temp_store = MEMORY")
            cursor.execute("PRAGMA cache_size = -2000000")  # Usa ~2GB de RAM para cache
            cursor.execute("PRAGMA synchronous = OFF")
            cursor.execute("PRAGMA journal_mode = MEMORY")
            
            # Normaliza e divide o nome
            nome_normalizado = remover_acentos(nome.upper())
            nomes = nome_normalizado.strip().split()
            
            if len(nomes) < 2:
                raise HTTPException(
                    status_code=400,
                    detail="Por favor, forneça nome e sobrenome para busca"
                )
            
            # Cria índice temporário se não existir
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_nome_upper 
                ON SRS_CONTATOS(upper(nome))
            """)
            
            # Monta query dinâmica com LIKE otimizado
            where_conditions = []
            params = []
            
            # Primeiro nome e último nome são mais importantes
            where_conditions.append("upper(nome) LIKE ?")
            params.append(f"{nomes[0]}%")
            
            where_conditions.append("upper(nome) LIKE ?")
            params.append(f"%{nomes[-1]}")
            
            # Nomes do meio (se houver)
            for nome_meio in nomes[1:-1]:
                where_conditions.append("upper(nome) LIKE ?")
                params.append(f"%{nome_meio}%")
            
            query = f"""
                SELECT 
                    NOME, 
                    CPF, 
                    NASC, 
                    NOME_MAE, 
                    NOME_PAI, 
                    SEXO,
                    CASE 
                        WHEN upper(NOME) = ? THEN 100
                        WHEN upper(NOME) LIKE ? THEN 90
                        ELSE (
                            length(?) - (
                                abs(length(NOME) - length(?)) + 
                                (length(NOME) - length(replace(upper(NOME), ?, '')))
                            )
                        )
                    END as score
                FROM SRS_CONTATOS 
                WHERE {' AND '.join(where_conditions)}
                ORDER BY score DESC
                LIMIT ?
            """
            
            # Adiciona parâmetros para o CASE
            params = [nome_normalizado, f"{nome_normalizado}%", 
                     nome_normalizado, nome_normalizado, 
                     nome_normalizado] + params + [limit]
            
            result = cursor.execute(query, params)
            
            pessoas = []
            for row in result:
                pessoas.append({
                    "nome": row[0],
                    "cpf": row[1],
                    "nascimento": row[2],
                    "nome_mae": row[3],
                    "nome_pai": row[4],
                    "sexo": row[5]
                })
            
            if not pessoas:
                return []
                
            return pessoas
            
    except Exception as e:
        logger.error(f"Erro na consulta por nome: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail={"code": "SEARCH_ERROR", "message": str(e)}
        )

@router.post("/consulta/telefone")
async def consulta_telefone_post(
    telefone: str = Query(..., min_length=8, description="Telefone para consulta"),
    user_id: str = Query(..., description="ID do usuário no Firebase"),
    api_key: str = Depends(api_key_header)
):
    """Consulta pessoas por telefone (POST)"""
    await firebase_service.verificar_saldo(user_id, "telefone", {"telefone": telefone})
    return await _consulta_telefone(telefone, api_key)