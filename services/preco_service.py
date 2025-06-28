from firebase_admin import firestore
from fastapi import HTTPException
from datetime import datetime
import logging
from typing import Dict

logger = logging.getLogger(__name__)

class PrecoService:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(PrecoService, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        try:
            self.db = firestore.client()
            self._collection = 'configuracoes'
            self._document = 'precos'
        except Exception as e:
            logger.error(f"Erro ao inicializar cliente Firestore: {str(e)}")
            raise HTTPException(status_code=500, detail="Erro ao conectar com Firebase")
        
    async def get_precos(self) -> Dict[str, float]:
        try:
            doc_ref = self.db.collection(self._collection).document(self._document)
            doc = doc_ref.get()
            if doc.exists:
                data = doc.to_dict()
                return data.get('precos', {})
            else:
                # Cria configuração padrão
                precos_padrao = {
                    'cpf': 25.0,
                    'nome': 25.0,
                    'telefone': 25.0,
                    'score': 25.0,
                    'endereco': 25.0,
                    'parentes': 25.0,
                    'email': 25.0,
                    'pis': 25.0,
                    'profissao': 25.0,
                    'educacao': 25.0,
                    'eleitoral': 25.0,
                    'irpf': 25.0
                }
                doc_ref.set({
                    'precos': precos_padrao,
                    'ultima_atualizacao': datetime.now().isoformat()
                })
                return precos_padrao
        except Exception as e:
            logger.error(f"Erro ao buscar preços: {str(e)}")
            raise HTTPException(status_code=500, detail="Erro ao buscar preços")
        
    async def atualizar_precos(self, novos_precos: dict):
        try:
            doc_ref = self.db.collection(self._collection).document(self._document)
            doc_ref.update({
                'precos': novos_precos,
                'ultima_atualizacao': datetime.now().isoformat()
            })
            return novos_precos
        except Exception as e:
            logger.error(f"Erro ao atualizar preços: {str(e)}")
            raise HTTPException(status_code=500, detail="Erro ao atualizar preços")

    async def get_preco_consulta(self, tipo_consulta: str) -> float:
        precos = await self.get_precos()
        if tipo_consulta not in precos:
            raise HTTPException(
                status_code=400,
                detail=f"Tipo de consulta inválido: {tipo_consulta}"
            )
        return precos[tipo_consulta] 