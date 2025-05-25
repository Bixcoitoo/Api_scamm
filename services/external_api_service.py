import httpx
from fastapi import HTTPException
from config.external_api_settings import get_external_api_settings
import logging

logger = logging.getLogger(__name__)

class ExternalAPIService:
    def __init__(self):
        self.settings = get_external_api_settings()
        self.base_url = self.settings.EXTERNAL_API_URL
        self.api_key = self.settings.EXTERNAL_API_KEY
        self.client = httpx.AsyncClient(timeout=30.0)
    
    async def make_request(self, method: str, endpoint: str, **kwargs):
        try:
            headers = kwargs.pop('headers', {})
            headers['X-API-Key'] = self.api_key
            
            url = f"{self.base_url}{endpoint}"
            response = await self.client.request(
                method=method,
                url=url,
                headers=headers,
                **kwargs
            )
            
            response.raise_for_status()
            return response.json()
            
        except httpx.HTTPError as e:
            logger.error(f"Erro na requisição à API externa: {str(e)}")
            raise HTTPException(
                status_code=e.response.status_code if hasattr(e, 'response') else 500,
                detail=f"Erro na requisição à API externa: {str(e)}"
            )
        except Exception as e:
            logger.error(f"Erro inesperado: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Erro inesperado: {str(e)}"
            )
    
    async def get_consulta(self, params: dict):
        return await self.make_request('GET', '/consulta', params=params)
    
    async def get_coins(self, params: dict):
        return await self.make_request('GET', '/coins', params=params)
    
    async def get_precos(self, params: dict):
        return await self.make_request('GET', '/precos', params=params) 