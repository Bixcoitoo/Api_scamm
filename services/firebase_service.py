import firebase_admin
from firebase_admin import credentials, db, auth, firestore
from fastapi import HTTPException
from datetime import datetime
import logging
import json
import time
from functools import wraps
from google.auth.exceptions import RefreshError
from config.firebase_config import get_firebase_credentials

logger = logging.getLogger(__name__)

def firebase_retry(max_retries=3, delay=2):
    """Decorator para retry automático em operações do Firebase"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except RefreshError as e:
                    last_exception = e
                    if "Invalid JWT Signature" in str(e):
                        logger.warning(f"JWT Signature error, attempt {attempt + 1}/{max_retries}")
                        if attempt < max_retries - 1:
                            time.sleep(delay * (2 ** attempt))  # Exponential backoff
                            continue
                    raise
                except Exception as e:
                    last_exception = e
                    logger.error(f"Firebase error: {str(e)}")
                    if attempt < max_retries - 1:
                        time.sleep(delay * (2 ** attempt))
                        continue
                    raise
            
            if last_exception:
                raise last_exception
        return wrapper
    return decorator

class FirebaseService:
    _instance = None
    _initialized = False
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(FirebaseService, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not self._initialized:
            try:
                # Obtém as credenciais das variáveis de ambiente ou arquivo JSON
                credentials_dict = get_firebase_credentials()
                
                if not credentials_dict:
                    logger.error("Não foi possível obter as credenciais do Firebase")
                    FirebaseService._initialized = False
                    return
                
                # Verifica se o Firebase já foi inicializado
                try:
                    firebase_admin.get_app()
                    logger.info("Firebase já foi inicializado anteriormente")
                    FirebaseService._initialized = True
                    return
                except ValueError:
                    # Firebase não foi inicializado, vamos inicializar
                    pass
                
                # Inicializa o Firebase Admin SDK com timeout
                cred = credentials.Certificate(credentials_dict)
                firebase_admin.initialize_app(cred, options={'timeout': 30})
                logger.info("Firebase inicializado com sucesso")
                FirebaseService._initialized = True
                
            except Exception as e:
                logger.error(f"Erro ao inicializar Firebase: {str(e)}")
                FirebaseService._initialized = False
        
    @firebase_retry(max_retries=3, delay=2)
    def check_connection(self):
        """Verifica conexão com Firestore com retry"""
        try:
            db = firestore.client()
            docs = db.collection('usuarios').limit(1).get()
            return True
        except Exception as e:
            logger.error(f"Erro ao verificar conexão com Firestore: {str(e)}")
            return False
        
    @firebase_retry(max_retries=3, delay=2)
    async def verificar_saldo(self, user_id: str, tipo_consulta: str, valor_consulta: float, detalhes: dict = None) -> bool:
        logger.info(f"Verificando saldo para usuário {user_id} - tipo consulta: {tipo_consulta} - valor: {valor_consulta}")
        
        try:
            # Busca o usuário no Firestore
            db_firestore = firestore.client()
            doc_ref = db_firestore.collection('usuarios').document(user_id)
            doc = doc_ref.get()
            if not doc.exists:
                raise HTTPException(status_code=404, detail="Usuário não encontrado")

            usuario = doc.to_dict()
            saldo_atual = usuario.get('coins', 0)
            
            if saldo_atual < valor_consulta:
                raise HTTPException(
                    status_code=402,
                    detail=f"Saldo insuficiente. Necessário: {valor_consulta}, Disponível: {saldo_atual}"
                )
            
            novo_saldo = saldo_atual - valor_consulta
            
            # Formata detalhes para evitar campos undefined
            detalhes_formatados = {
                'tipo_consulta': tipo_consulta,
                'params': {
                    'nome': detalhes.get('nome') if detalhes else None
                }
            }
            
            # Registra transação
            transacoes_ref = doc_ref.collection('transacoes')
            transacao_data = {
                'tipo': 'consulta',
                'valor': -valor_consulta,
                'data': datetime.now().isoformat(),
                'descricao': f"Consulta {tipo_consulta}",
                'detalhes': detalhes_formatados
            }
            transacoes_ref.add(transacao_data)
            
            # Atualiza saldo
            doc_ref.update({
                'coins': novo_saldo,
                'ultima_consulta': datetime.now().isoformat()
            })
            
            return True
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Erro ao verificar saldo: {str(e)}")
            raise HTTPException(status_code=500, detail="Erro ao processar verificação de saldo")
            
    @firebase_retry(max_retries=3, delay=2)
    async def registrar_transacao(self, user_id: str, tipo: str, valor: float, descricao: str):
        try:
            transacao = {
                'tipo': tipo,
                'valor': valor,
                'data': datetime.now().isoformat(),
                'descricao': descricao
            }
            
            transacao_ref = self.db.child('usuarios').child(user_id).child('transacoes').push()
            transacao_ref.set(transacao)
            
            logger.info(f"Transação registrada: {transacao}")
            
        except Exception as e:
            logger.error(f"Erro ao registrar transação: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail="Erro ao registrar transação"
            )

    @firebase_retry(max_retries=3, delay=2)
    async def authenticate_user(self, email: str, password: str):
        """Autentica um usuário com email e senha"""
        try:
            # Tenta fazer login com email/senha
            user = auth.get_user_by_email(email)
            return user
        except auth.UserNotFoundError:
            logger.error(f"Usuário não encontrado: {email}")
            return None
        except Exception as e:
            logger.error(f"Erro ao autenticar usuário: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail="Erro ao autenticar usuário"
            )

    @firebase_retry(max_retries=3, delay=2)
    async def create_custom_token(self, uid: str) -> str:
        """Cria um token JWT personalizado para o usuário"""
        try:
            return auth.create_custom_token(uid)
        except Exception as e:
            logger.error(f"Erro ao criar token: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail="Erro ao gerar token de autenticação"
            )

    @firebase_retry(max_retries=3, delay=2)
    async def verify_admin_token(self, token: str):
        """Verifica se o token é válido e pertence a um admin"""
        try:
            decoded_token = auth.verify_id_token(token)
            return decoded_token
        except Exception as e:
            logger.error(f"Erro ao verificar token: {str(e)}")
            raise HTTPException(
                status_code=401,
                detail="Token inválido ou expirado"
            ) 