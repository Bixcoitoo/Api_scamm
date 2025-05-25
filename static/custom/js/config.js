const API_CONFIG = {
    baseUrl: 'https://api.magalha.space',
    endpoints: {
        status: '/api/status',
        health: '/api/health',
        consulta: '/api/consulta',
        coins: '/api/coins',
        precos: '/api/precos'
    },
    headers: {
        'Content-Type': 'application/json',
        'X-API-Key': localStorage.getItem('api_key')
    }
};

// Exporta a configuração para uso em outros arquivos
window.API_CONFIG = API_CONFIG; 