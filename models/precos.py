from pydantic import BaseModel
from typing import Dict
from datetime import datetime

class PrecoConfig(BaseModel):
    precos: Dict[str, float]
    ultima_atualizacao: datetime

class PrecoConsulta(BaseModel):
    tipo: str
    valor: float
    descricao: str
    ativo: bool = True

class PrecosConfig(BaseModel):
    precos: Dict[str, PrecoConsulta]
    ultima_atualizacao: datetime

class PrecoHistorico(BaseModel):
    tipo: str
    valor_anterior: float
    valor_novo: float
    data_alteracao: datetime
    alterado_por: str 