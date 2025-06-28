from fastapi import APIRouter, HTTPException, Depends
from models.creditos import CreditoUsuario, TransacaoCredito
from services.firebase_service import FirebaseService
from datetime import datetime, timedelta
import logging
from fastapi.responses import JSONResponse

router = APIRouter()
logger = logging.getLogger(__name__)

def get_firebase_service():
    """Função para obter instância do FirebaseService"""
    return FirebaseService()

@router.get("/creditos/saldo/{user_id}")
async def consultar_saldo(user_id: str):
    try:
        firebase_service = get_firebase_service()
        usuario_ref = firebase_service.db.collection('usuarios').document(user_id)
        usuario = usuario_ref.get()
        
        if not usuario.exists:
            return {"saldo": 0}
            
        dados_usuario = usuario.to_dict()
        return {"saldo": dados_usuario.get('coins', 0)}
    except Exception as e:
        logger.error(f"Erro ao consultar saldo: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/creditos/adicionar")
async def adicionar_creditos(transacao: TransacaoCredito):
    try:
        firebase_service = get_firebase_service()
        # Busca usuário
        usuario_ref = firebase_service.db.collection('usuarios').document(transacao.user_id)
        usuario = usuario_ref.get()
        
        if not usuario.exists:
            return JSONResponse(
                status_code=404,
                content={"detail": "Usuário não encontrado"}
            )
            
        dados_usuario = usuario.to_dict()
        saldo_atual = dados_usuario.get('coins', 0)
        novo_saldo = saldo_atual + transacao.valor
        
        # Registra a transação
        await firebase_service.registrar_transacao(
            user_id=transacao.user_id,
            tipo="recarga",
            valor=transacao.valor,
            descricao=transacao.descricao
        )
        
        # Atualiza saldo
        usuario_ref.update({
            'coins': novo_saldo,
            'ultima_recarga': datetime.now().isoformat()
        })
        
        return {
            "message": "Créditos adicionados com sucesso",
            "novo_saldo": novo_saldo
        }
    except Exception as e:
        logger.error(f"Erro ao adicionar créditos: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/creditos/historico/{user_id}")
async def historico_transacoes(user_id: str, dias: int = 30):
    try:
        firebase_service = get_firebase_service()
        transacoes_ref = firebase_service.db.collection('usuarios').document(user_id).collection('transacoes')
        transacoes = transacoes_ref.get()
        
        if not transacoes:
            return []
            
        data_limite = datetime.now() - timedelta(days=dias)
        
        historico = []
        for doc in transacoes:
            transacao = doc.to_dict()
            data_transacao = datetime.fromisoformat(transacao['data'])
            if data_transacao >= data_limite:
                transacao['id'] = doc.id
                historico.append(transacao)
                
        return sorted(historico, key=lambda x: x['data'], reverse=True)
        
    except Exception as e:
        logger.error(f"Erro ao buscar histórico: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/creditos/teste-conexao")
async def teste_conexao():
    try:
        firebase_service = get_firebase_service()
        # Tenta criar um documento de teste
        ref = firebase_service.db.collection('teste').document()
        ref.set({
            'timestamp': datetime.now().isoformat(),
            'status': 'ok'
        })
        
        logger.info("Teste de conexão com Firebase realizado com sucesso")
        return {
            "message": "Conexão com Firebase estabelecida com sucesso",
            "ref": ref.id,
            "database_url": "https://scammapi-default-rtdb.firebaseio.com"
        }
    except Exception as e:
        logger.error(f"Erro ao conectar com Firebase: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao conectar com Firebase: {str(e)}"
        ) 