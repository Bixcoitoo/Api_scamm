from fastapi import APIRouter, Depends, HTTPException, Security
from fastapi.security import APIKeyHeader, HTTPBearer
from services.firebase_service import FirebaseService
import logging
from pydantic import BaseModel
from fastapi.responses import Response

router = APIRouter(prefix="/auth", tags=["auth"])
security = HTTPBearer()
firebase_service = FirebaseService()
logger = logging.getLogger(__name__)

class LoginRequest(BaseModel):
    email: str
    password: str

@router.post("/login")
async def login(request: LoginRequest):
    try:
        # Autentica com Firebase
        user = await firebase_service.authenticate_user(request.email, request.password)
        
        if not user:
            raise HTTPException(
                status_code=401,
                detail="Credenciais inválidas"
            )
            
        # Gera token JWT
        token = await firebase_service.create_custom_token(user.uid)
        
        return {
            "status": "success",
            "token": token,
            "user": {
                "uid": user.uid,
                "email": user.email,
                "isAdmin": user.custom_claims.get('admin', False) if user.custom_claims else False
            }
        }
        
    except Exception as e:
        logger.error(f"Erro no login: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Erro ao realizar login"
        )

@router.options("/login")
async def options_login():
    return Response(status_code=200)

async def verify_admin_token(credentials: HTTPBearer = Security(security)):
    try:
        # Verifica se o token é de um admin
        token = credentials.credentials
        claims = await firebase_service.verify_admin_token(token)
        
        if not claims.get('admin', False):
            raise HTTPException(
                status_code=403,
                detail="Acesso não autorizado. Necessário privilégios de administrador."
            )
        return claims
        
    except Exception as e:
        logger.error(f"Erro na autenticação admin: {str(e)}")
        raise HTTPException(
            status_code=401,
            detail="Token inválido ou expirado"
        ) 