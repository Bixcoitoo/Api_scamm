from pydantic import BaseModel
from datetime import datetime
from typing import List, Dict, Optional

class PrecoHistorico(BaseModel):
    tipo: str
    valor_anterior: float
    valor_novo: float
    data_alteracao: datetime
    alterado_por: str

class MetricasUso(BaseModel):
    tipo_consulta: str
    total_consultas: int
    receita_total: float
    periodo: str  # "diario", "semanal", "mensal"

class DashboardData(BaseModel):
    precos_atuais: Dict[str, float]
    historico_alteracoes: List[PrecoHistorico]
    metricas: List[MetricasUso]
    ultima_atualizacao: datetime 