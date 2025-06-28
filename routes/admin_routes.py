from fastapi import APIRouter, Depends, HTTPException
from services.preco_service import PrecoService
from models.precos import PrecoConsulta, PrecosConfig
from fastapi.security import APIKeyHeader
import logging

router = APIRouter(prefix="/admin", tags=["admin"])
logger = logging.getLogger(__name__)

def get_preco_service():
    """Função para obter instância do PrecoService"""
    return PrecoService()

@router.get("/precos")
async def listar_precos():
    preco_service = get_preco_service()
    return await preco_service.get_precos()

@router.put("/precos")
async def atualizar_precos(config: PrecosConfig):
    preco_service = get_preco_service()
    return await preco_service.atualizar_precos(config.precos)

@router.get("/admin/test-dashboard")
async def test_dashboard():
    """Rota de teste que retorna dados mockados do dashboard"""
    preco_service = get_preco_service()
    precos_atuais = await preco_service.get_precos()
    
    return {
        "precos_atuais": precos_atuais,
        "historico_alteracoes": [
            {
                "tipo": "cpf",
                "valor_anterior": 8.0,
                "valor_novo": 10.0,
                "data_alteracao": "2024-02-09T00:00:00",
                "alterado_por": "admin@teste.com"
            }
        ],
        "metricas": [
            {
                "tipo_consulta": "cpf",
                "total_consultas": 150,
                "receita_total": 1500.0,
                "periodo": "mensal"
            }
        ],
        "ultima_atualizacao": "2024-02-09T00:00:00"
    }

@router.get("/admin/test-auth")
async def test_auth():
    """Rota de teste para verificar autenticação"""
    return {
        "status": "success",
        "message": "Autenticação bem sucedida",
        "user": {
            "email": "admin@teste.com",
            "isAdmin": True
        }
    }

@router.get("/")
async def admin_home():
    return {
        "status": "ok",
        "message": "Bem-vindo ao painel administrativo"
    }

@router.get("/test")
async def test_admin():
    try:
        # Testa conexão com Firestore
        preco_service = get_preco_service()
        precos = await preco_service.get_precos()
        return {
            "status": "ok",
            "precos": precos
        }
    except Exception as e:
        logger.error(f"Erro no teste admin: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e)) 