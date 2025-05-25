async function checarAPI() {
    try {
        const response = await fetch(`${API_CONFIG.baseUrl}${API_CONFIG.endpoints.status}`, {
            headers: API_CONFIG.headers
        });
        
        if (!response.ok) {
            throw new Error(`Erro ao verificar status: ${response.status}`);
        }
        
        const data = await response.json();
        console.log('📊 Status da API:', data);
        
        // Considera a API como operacional se o status for 'operational'
        // ou se o banco de dados estiver online
        if (data.status === 'operational' || 
            (data.services && data.services.database === 'online')) {
            console.log('✅ API operacional');
            return true;
        } else {
            console.log('⚠️ API em estado degradado');
            return false;
        }
    } catch (error) {
        console.error('❌ Erro ao verificar status da API:', error);
        return false;
    }
}

// Função para verificar periodicamente
async function verificarPeriodicamente() {
    console.log('🔵 Iniciando verificação periódica da API...');
    
    while (true) {
        const status = await checarAPI();
        if (status) {
            console.log('✅ API está online');
            break;
        }
        
        console.log('⏳ Aguardando 5 segundos para próxima verificação...');
        await new Promise(resolve => setTimeout(resolve, 5000));
    }
}

// Inicia a verificação quando a página carregar
window.addEventListener('load', () => {
    verificarPeriodicamente();
}); 