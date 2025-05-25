from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class CreditoUsuario(BaseModel):
    user_id: str
    saldo: float

class TransacaoCredito(BaseModel):
    user_id: str
    tipo: str  # "recarga" ou "consulta"
    valor: float
    data: datetime = datetime.now()
    descricao: str
    