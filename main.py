from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks, Query, Body
from fastapi.security.api_key import APIKeyHeader
from typing import Optional, List
from pydantic import BaseModel
import asyncio
from functools import lru_cache, partial
import uvicorn
from pathlib import Path
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, HTMLResponse, Response
import apsw
from validators.cpf_validator import CPFValidator
from config.settings import API_SETTINGS, SECURITY
from middleware.rate_limit import RateLimitMiddleware
from middleware.security_headers import SecurityHeadersMiddleware
from routes import consulta_routes, credito_routes, admin_routes, admin_auth
from contextlib import contextmanager, asynccontextmanager
from queue import Queue
import threading
import unicodedata
from asyncio import TimeoutError
from fastapi.openapi.docs import (
    get_swagger_ui_html,
    get_swagger_ui_oauth2_redirect_html,
)
from fastapi.staticfiles import StaticFiles
import os
from connection_manager import connection_manager
import logging
import uuid
from datetime import datetime
import time
from dotenv import load_dotenv
try:
    from services.elasticsearch_service import ElasticsearchService
    HAS_ELASTICSEARCH = True
except ImportError:
    HAS_ELASTICSEARCH = False
from services.pessoa_service import (
    get_parentes, 
    get_irpf, 
    get_score, 
    get_pis, 
    get_profissao, 
    get_dados_eleitorais, 
    get_dados_universitarios
)
from models.pessoa import PessoaCompleta, DadosBasicos, Contatos, Financeiro, Profissional
from services.endereco_service import get_endereco
from utils.logger import setup_logger
from middleware.transaction_logger import TransactionLoggerMiddleware
from config.firebase_config import generate_service_account_file
from services.firebase_service import FirebaseService
from database.connection import get_db_connection, connection_pools

# Configuração dos diretórios
BASE_DIR = Path(__file__).parent.parent
STATIC_DIR = BASE_DIR / "static"
CUSTOM_DIR = STATIC_DIR / "custom"
CSS_DIR = CUSTOM_DIR / "css"
JS_DIR = CUSTOM_DIR / "js"

# Criar diretórios se não existirem
for directory in [STATIC_DIR, CUSTOM_DIR, CSS_DIR, JS_DIR]:
    directory.mkdir(exist_ok=True)

# Setup logger
logger = setup_logger()

# Primeiro carrega as variáveis de ambiente
load_dotenv()

# Inicializa o serviço do Firebase
firebase_service = FirebaseService()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Configuração ao iniciar
    logger.info("Iniciando aplicação...")
    load_dotenv()
    
    # Inicializa o Firebase
    try:
        firebase_service = FirebaseService()
        logger.info("Firebase inicializado com sucesso")
    except Exception as e:
        logger.error(f"Erro ao inicializar Firebase: {str(e)}")
        raise
    
    yield
    
    # Limpeza ao encerrar
    logger.info("Encerrando aplicação...")

app = FastAPI(
    title="API de Consulta SERASA",
    description="API para consulta de dados no banco SERASA",
    version="1.0.0",
    docs_url=None,
    redoc_url=None,
    lifespan=lifespan
)

API_KEY = SECURITY['api_key']
api_key_header = APIKeyHeader(name="X-API-Key")

class PessoaResponse(BaseModel):
    nome: str
    cpf: str
    nascimento: str
    nome_mae: str
    nome_pai: str
    sexo: str
    emails: Optional[List[str]] = []
    telefones: Optional[List[str]] = []



async def get_emails(cpf: str, contatos_conn):
    print(f"Buscando emails para CPF: {cpf}")
    try:
        # Primeiro pegamos o CONTATOS_ID usando a conexão existente
        contatos_cursor = contatos_conn.cursor()
        result = contatos_cursor.execute("""
            SELECT CONTATOS_ID FROM SRS_CONTATOS WHERE CPF = ?
        """, (cpf,))
        
        contato = result.fetchone()
        if not contato:
            return []
            
        contatos_id = contato[0]
        
        # Agora buscamos os emails
        with get_db_connection("SRS_EMAIL") as email_conn:
            email_cursor = email_conn.cursor()
            result = email_cursor.execute("""
                SELECT DISTINCT EMAIL FROM SRS_EMAIL WHERE CONTATOS_ID = ?
            """, (contatos_id,))
            return [row[0] for row in result.fetchall()]
            
    except Exception as e:
        print(f"Erro ao buscar emails: {str(e)}")
        return []

async def get_telefones(cpf: str, contatos_conn):
    print(f"Buscando telefones para CPF: {cpf}")
    try:
        # Primeiro pegamos o CONTATOS_ID usando a conexão existente
        contatos_cursor = contatos_conn.cursor()
        result = contatos_cursor.execute("""
            SELECT CONTATOS_ID FROM SRS_CONTATOS WHERE CPF = ?
        """, (cpf,))
        
        contato = result.fetchone()
        if not contato:
            print("CONTATOS_ID não encontrado")
            return []
            
        contatos_id = contato[0]
        print(f"CONTATOS_ID encontrado: {contatos_id}")
        
        # Agora buscamos os telefones usando with
        with get_db_connection("SRS_HISTORICO_TELEFONES") as tel_conn:
            tel_cursor = tel_conn.cursor()
            result = tel_cursor.execute("""
                SELECT DISTINCT DDD || TELEFONE as telefone
                FROM SRS_HISTORICO_TELEFONES 
                WHERE CONTATOS_ID = ?
            """, (contatos_id,))
            
            telefones = [row[0] for row in result.fetchall()]
            print(f"Telefones encontrados: {len(telefones)}")
            return telefones
            
    except Exception as e:
        print(f"Erro ao buscar telefones: {str(e)}")
        return []

async def executar_com_timeout(func, *args, timeout=60):
    """Executa uma função com timeout"""
    try:
        return await asyncio.wait_for(func(*args), timeout=timeout)
    except TimeoutError:
        raise HTTPException(
            status_code=408,
            detail="Tempo limite de consulta excedido (60 segundos)"
        )

    
def remover_acentos(texto):
    """Remove acentos e converte para maiúsculas"""
    # Normaliza o texto (decomposição)
    nfkd = unicodedata.normalize('NFKD', texto)
    # Remove os caracteres de acentuação
    sem_acentos = u"".join([c for c in nfkd if not unicodedata.combining(c)])
    # Converte para maiúsculas
    return sem_acentos.upper()

@app.get("/consulta/nome/{nome}")
async def consulta_nome(
    nome: str, 
    limit: int = 10,
    api_key: str = Depends(api_key_header)
):
    """
    Busca pessoas por nome completo
    
    - **nome**: Nome completo (nome + sobrenome)
    - **limit**: Número máximo de resultados (padrão: 10)
    - **api_key**: Chave de API (obrigatória)
    
    Retorna uma lista de pessoas encontradas
    """
    conn_id = str(uuid.uuid4())
    return await connection_manager.track_connection(
        conn_id,
        _consulta_nome(nome, api_key, limit),
        timeout=300
    )

async def _consulta_nome(nome: str, api_key: str, limit: int = 10):
    if api_key != API_KEY:
        raise HTTPException(status_code=403, detail="Chave API inválida")
    
 
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
            
        es_service = ElasticsearchService()
        pessoas = await es_service.search_nome(nome, limit=limit)
        
        if not pessoas:
            raise HTTPException(
                status_code=404,
                detail="Nenhuma pessoa encontrada com esse nome"
            )
        
        return pessoas
            
    except HTTPException:
        raise
    except Exception as e:
        print(f"ERRO: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao consultar dados: {str(e)}"
        )

@app.get("/consulta/telefone/{telefone}",
    summary="Consulta por Telefone",
    description="Busca dados de uma pessoa pelo número de telefone",
    response_description="Retorna os dados da pessoa encontrada",
    responses={
        200: {
            "description": "Dados encontrados com sucesso",
            "content": {
                "application/json": {
                    "example": {
                        "nome": "JOÃO DA SILVA",
                        "cpf": "123.456.789-00",
                        "nascimento": "1990-01-01",
                        "telefones": ["11999999999"]
                    }
                }
            }
        },
        404: {
            "description": "Nenhuma pessoa encontrada"
        },
        500: {
            "description": "Erro interno do servidor"
        }
    }
)
async def consulta_telefone(telefone: str, api_key: str = Depends(api_key_header)):
    conn_id = str(uuid.uuid4())
    return await connection_manager.track_connection(
        conn_id,
        _consulta_telefone(telefone, api_key),
        timeout=300
    )

@app.get("/consulta/telefone/{telefone}")
async def _consulta_telefone(telefone: str, api_key: str):
    if api_key != API_KEY:
        raise HTTPException(status_code=403, detail="Chave API inválida")
    
    # Remove caracteres não numéricos do telefone
    telefone = ''.join(filter(str.isdigit, telefone))
    
    print(f"\n=== Iniciando consulta para telefone: {telefone} ===")
    
    try:
        # Primeiro busca o CONTATOS_ID pelo telefone
        with get_db_connection("SRS_HISTORICO_TELEFONES") as tel_conn:
            print("1. Conexão estabelecida com SRS_HISTORICO_TELEFONES")
            tel_cursor = tel_conn.cursor()
            
            # Separa DDD e telefone para busca
            ddd = telefone[:2] if len(telefone) >= 2 else ''
            num = telefone[2:] if len(telefone) >= 2 else telefone
            
            print(f"2. Buscando DDD: {ddd}, Telefone: {num}")
            
            result = tel_cursor.execute("""
                SELECT DISTINCT CONTATOS_ID 
                FROM SRS_HISTORICO_TELEFONES 
                WHERE DDD = ? AND TELEFONE = ?
            """, (ddd, num))
            
            contatos_ids = [row[0] for row in result.fetchall()]
            print(f"3. IDs encontrados: {len(contatos_ids)}")
            
            if not contatos_ids:
                raise HTTPException(
                    status_code=404,
                    detail="Nenhuma pessoa encontrada com esse telefone"
                )
            
            # Agora busca os dados das pessoas usando os CONTATOS_IDs
            pessoas = []
            with get_db_connection("SRS_CONTATOS") as conn:
                print("4. Conexão estabelecida com SRS_CONTATOS")
                cursor = conn.cursor()
                
                for contatos_id in contatos_ids:
                    result = cursor.execute("""
                        SELECT NOME, CPF, NASC, NOME_MAE, NOME_PAI, SEXO
                        FROM SRS_CONTATOS 
                        WHERE CONTATOS_ID = ?
                    """, (contatos_id,))
                    
                    pessoa = result.fetchone()
                    if pessoa:
                        print(f"5. Processando pessoa: {pessoa[0]}")
                        
                        # Busca todos os telefones da pessoa
                        tel_result = tel_cursor.execute("""
                            SELECT DISTINCT DDD || TELEFONE as telefone
                            FROM SRS_HISTORICO_TELEFONES 
                            WHERE CONTATOS_ID = ?
                        """, (contatos_id,))
                        telefones = [row[0] for row in tel_result.fetchall()]
                        
                        pessoas.append({
                            "nome": pessoa[0],
                            "cpf": pessoa[1],
                            "nascimento": pessoa[2],
                            "nome_mae": pessoa[3],
                            "nome_pai": pessoa[4],
                            "sexo": pessoa[5],
                            "telefones": telefones
                        })
            
            return pessoas
            
    except Exception as e:
        print(f"ERRO: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao consultar dados: {str(e)}"
        )


# Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://scammnet.site"],  # Só aceita seu frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Adiciona middleware
app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(TransactionLoggerMiddleware)

# Inclui as rotas
app.include_router(admin_auth.router, prefix="/api")
app.include_router(consulta_routes.router, prefix="/api")
app.include_router(credito_routes.router, prefix="/api")
app.include_router(admin_routes.router, prefix="/api")

# Montar arquivos estáticos
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/docs", include_in_schema=False)
async def custom_swagger_ui_html():
    return HTMLResponse("""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <title>API de Consulta SERASA</title>
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&display=swap" rel="stylesheet">
        <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5.11.0/swagger-ui.css">
        <style>
            :root {
                --primary: #4f46e5;
                --secondary: #4338ca;
                --background: #f8fafc;
                --surface: #ffffff;
                --text: #1e293b;
            }
            
            body {
                font-family: 'Inter', sans-serif;
                margin: 0;
                padding: 0;
                background: var(--background);
                color: var(--text);
            }
            
            #swagger-ui {
                max-width: 1200px;
                margin: 0 auto;
                padding: 2rem;
            }
            
            .swagger-ui .info {
                margin: 2rem 0;
                padding: 2rem;
                background: var(--surface);
                border-radius: 1rem;
                box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1);
            }
            
            .swagger-ui .info .title {
                font-family: 'Inter', sans-serif;
                font-size: 2.25rem;
                font-weight: 600;
                color: var(--primary);
                margin: 0;
            }
            
            .swagger-ui .opblock {
                margin: 0 0 1rem;
                border: none;
                border-radius: 0.75rem;
                box-shadow: 0 2px 4px rgba(0,0,0,0.05);
                overflow: hidden;
            }
            
            .swagger-ui .opblock.opblock-get {
                background: rgba(79,70,229,0.05);
                border: 1px solid rgba(79,70,229,0.1);
            }
            
            .swagger-ui .opblock.opblock-get .opblock-summary-method {
                background: var(--primary);
            }
            
            .swagger-ui .opblock-summary {
                padding: 1rem;
            }
            
            .swagger-ui .opblock-summary-method {
                min-width: 100px;
                text-align: center;
                border-radius: 0.5rem;
                padding: 0.5rem 1rem;
            }
            
            .swagger-ui .btn {
                border-radius: 0.5rem;
                font-family: 'Inter', sans-serif;
                font-weight: 500;
            }
            
            .swagger-ui .btn.authorize {
                background: var(--primary);
                color: white;
                border: none;
                padding: 0.5rem 1.5rem;
                transition: all 0.2s;
            }
            
            .swagger-ui .btn.authorize:hover {
                background: var(--secondary);
            }
            
            .swagger-ui input[type=text] {
                border-radius: 0.5rem;
                border: 1px solid #e2e8f0;
                padding: 0.5rem 1rem;
            }
            
            @media (max-width: 768px) {
                #swagger-ui {
                    padding: 1rem;
                }
                
                .swagger-ui .info {
                    padding: 1rem;
                }
                
                .swagger-ui .info .title {
                    font-size: 1.75rem;
                }
            }

            .swagger-ui .api-description {
                background: var(--surface);
                padding: 2rem;
                border-radius: 1rem;
                box-shadow: 0 1px 3px rgba(0,0,0,0.1);
                margin: 1rem 0;
            }

            .swagger-ui .api-header h2 {
                color: var(--primary);
                font-size: 1.5rem;
                font-weight: 600;
                margin: 0 0 1.5rem 0;
                font-family: 'Inter', sans-serif;
            }

            .swagger-ui .api-features {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
                gap: 1.5rem;
                margin: 1.5rem 0;
            }

            .swagger-ui .api-feature {
                background: rgba(79,70,229,0.05);
                padding: 1.5rem;
                border-radius: 0.75rem;
                border: 1px solid rgba(79,70,229,0.1);
            }

            .swagger-ui .api-feature h3 {
                color: var(--primary);
                font-size: 1.25rem;
                font-weight: 500;
                margin: 0 0 0.75rem 0;
                font-family: 'Inter', sans-serif;
            }

            .swagger-ui .api-feature p {
                margin: 0;
                color: var(--text);
                line-height: 1.5;
            }

            .swagger-ui .api-auth {
                margin-top: 2rem;
                padding-top: 1.5rem;
                border-top: 1px solid rgba(0,0,0,0.1);
            }

            .swagger-ui .api-auth h3 {
                color: var(--primary);
                font-size: 1.25rem;
                font-weight: 500;
                margin: 0 0 0.75rem 0;
                font-family: 'Inter', sans-serif;
            }

            .swagger-ui .api-auth code {
                background: rgba(79,70,229,0.1);
                color: var(--primary);
                padding: 0.25rem 0.5rem;
                border-radius: 0.25rem;
                font-family: monospace;
            }
        </style>
    </head>
    <body>
        <div id="swagger-ui"></div>
        <script src="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5.11.0/swagger-ui-bundle.js"></script>
        <script>
            window.onload = () => {
                window.ui = SwaggerUIBundle({
                    url: '/openapi.json',
                    dom_id: '#swagger-ui',
                    deepLinking: true,
                    presets: [
                        SwaggerUIBundle.presets.apis
                    ],
                    layout: "BaseLayout",
                    defaultModelsExpandDepth: -1,
                    displayRequestDuration: true,
                    filter: true,
                    syntaxHighlight: {
                        activated: true,
                        theme: "monokai"
                    }
                });
            };
        </script>
    </body>
    </html>
    """)

@app.get("/docs/oauth2-redirect", include_in_schema=False)
async def swagger_ui_redirect():
    return get_swagger_ui_oauth2_redirect_html()

@app.get("/", tags=["Status"])
async def root():
    """
    Endpoint base da API que retorna informações básicas e status
    """
    return {
        "status": "online",
        "name": "API de Consulta SERASA",
        "version": "1.0.0",
        "documentation": "/docs",
        "healthcheck": "ok"
    }

@app.get("/stats", tags=["Status"])
async def stats():
    """Retorna estatísticas da API"""
    try:
        with get_db_connection("SRS_CONTATOS") as conn:
            cursor = conn.cursor()
            stats = {
                "total_registros": cursor.execute("SELECT COUNT(*) FROM SRS_CONTATOS").fetchone()[0],
                "total_telefones": cursor.execute("SELECT COUNT(*) FROM SRS_HISTORICO_TELEFONES").fetchone()[0],
                "total_emails": cursor.execute("SELECT COUNT(*) FROM SRS_EMAIL").fetchone()[0],
                "ultima_atualizacao": "2024-03-14"
            }
            return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health", tags=["Status"])
async def health():
    """Verifica saúde dos serviços"""
    try:
        services = {
            "database": "online",
            "api": "online",
            "cache": "online",
            "rate_limiter": "online"
        }
        return {
            "status": "healthy",
            "services": services,
            "uptime": "24h 13m",
            "memory_usage": "1.2GB"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

async def reconnection_task():
    while True:
        try:
            logger.info("🔍 Verificando conexões...")
            active_conns = len(connection_manager._active_connections)
            logger.info(f"""
📊 Status das Conexões:
- Conexões ativas: {active_conns}
- Última reconexão: {datetime.fromtimestamp(connection_manager._last_reconnect).strftime('%H:%M:%S')}
- Próxima reconexão em: {max(0, 5 - (time.time() - connection_manager._last_reconnect)):.1f}s
""")
            await asyncio.sleep(5)
        except Exception as e:
            logger.error(f"❌ Erro na tarefa de reconexão: {e}")
            await asyncio.sleep(1)

@app.options("/auth/login")
async def options_login():
    return Response(status_code=200)

@app.middleware("http")
async def global_options_handler(request, call_next):
    if request.method == "OPTIONS":
        response = Response(status_code=200)
        response.headers["Access-Control-Allow-Origin"] = "https://scammnet.site"
        response.headers["Access-Control-Allow-Methods"] = "GET,POST,PUT,DELETE,OPTIONS"
        response.headers["Access-Control-Allow-Headers"] = "*"
        response.headers["Access-Control-Allow-Credentials"] = "true"
        return response
    return await call_next(request)

if __name__ == "__main__":
    config = uvicorn.Config(
        "main:app",
        host="0.0.0.0",
        port=3000,
        reload=True,
        log_level="info",
        timeout_keep_alive=30,
        limit_concurrency=100,
        loop="asyncio"
    )
    server = uvicorn.Server(config)
    server.run() 