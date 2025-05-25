from firebase_admin import firestore
from datetime import datetime, timedelta
from models.admin import PrecoHistorico, MetricasUso, DashboardData
import logging

logger = logging.getLogger(__name__)

class AdminService:
    def __init__(self):
        self.db = firestore.client()
        
    async def get_dashboard_data(self):
        try:
            # Busca preços atuais
            precos = await self.get_precos_atuais()
            
            # Busca histórico de alterações
            historico = await self.get_historico_alteracoes()
            
            # Busca métricas de uso
            metricas = await self.calcular_metricas_uso()
            
            return DashboardData(
                precos_atuais=precos,
                historico_alteracoes=historico,
                metricas=metricas,
                ultima_atualizacao=datetime.now()
            )
            
        except Exception as e:
            logger.error(f"Erro ao buscar dados do dashboard: {str(e)}")
            raise
            
    async def registrar_alteracao_preco(self, tipo: str, valor_anterior: float, 
                                      valor_novo: float, admin_id: str):
        try:
            historico = PrecoHistorico(
                tipo=tipo,
                valor_anterior=valor_anterior,
                valor_novo=valor_novo,
                data_alteracao=datetime.now(),
                alterado_por=admin_id
            )
            
            self.db.collection('configuracoes').document('historico_precos').collection('alteracoes').add(
                historico.dict()
            )
            
        except Exception as e:
            logger.error(f"Erro ao registrar alteração de preço: {str(e)}")
            raise 