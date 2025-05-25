import { userService } from './services/user.service.js';
import { auth, db } from './firebase-config.js';
import { authService } from './services/auth.service.js';
import { getDoc, doc } from 'https://www.gstatic.com/firebasejs/10.8.0/firebase-firestore.js';
import { coinsService } from './services/coins.service.js';
import API_CONFIG from './config.js';

// Função para atualizar o nome do usuário no menu
function updateUserDisplay(user, profile) {
    const userDisplay = document.getElementById('userDisplay');
    if (userDisplay) {
        userDisplay.textContent = profile?.username || user?.displayName || 'Usuário';
    }
}

// Middleware de autenticação
(async function() {
    try {
        document.documentElement.style.display = 'none';
        
        // Aguarda um momento para garantir que o Firebase Auth esteja inicializado
        await new Promise(resolve => setTimeout(resolve, 100));
        
        // Tenta verificar a sessão algumas vezes
        let session = null;
        let tentativas = 0;
        const maxTentativas = 3;
        
        while (!session && tentativas < maxTentativas) {
            try {
                session = await authService.checkSession();
                if (!session) {
                    console.log(`Tentativa ${tentativas + 1} de ${maxTentativas} falhou`);
                    await new Promise(resolve => setTimeout(resolve, 1000)); // Espera 1 segundo entre tentativas
                }
            } catch (error) {
                console.error(`Erro na tentativa ${tentativas + 1}:`, error);
            }
            tentativas++;
        }
        
        console.log('Verificação de sessão:', session);
        
        if (!session || !session.user) {
            console.error('❌ Usuário não autenticado após várias tentativas');
            window.location.replace('/pages/login.html');
            return;
        }

        // Atualiza a interface com os dados do usuário
        let profile = null;
        tentativas = 0;
        
        while (!profile && tentativas < maxTentativas) {
            try {
                profile = await userService.getUserProfile();
                if (!profile) {
                    console.log(`Tentativa ${tentativas + 1} de ${maxTentativas} falhou ao obter perfil`);
                    await new Promise(resolve => setTimeout(resolve, 1000));
                }
            } catch (error) {
                console.error(`Erro ao obter perfil na tentativa ${tentativas + 1}:`, error);
            }
            tentativas++;
        }
        
        console.log('Perfil do usuário:', profile);
        
        if (!profile) {
            console.error('❌ Perfil do usuário não encontrado após várias tentativas');
            window.location.replace('/pages/login.html');
            return;
        }

        updateUserDisplay(session.user, profile);
        await updateCoinsDisplay();
        
        document.documentElement.style.display = 'block';
    } catch (error) {
        console.error('Erro na verificação de autenticação:', error);
        window.location.replace('/pages/login.html');
    }
})();

async function updateCoinsDisplay() {
    try {
        const balance = await coinsService.getBalance();
        const coinsElements = [
            document.querySelector('.coins-display'),
            document.getElementById('topMenuCoins')
        ];
        
        coinsElements.forEach(element => {
            if (element) {
                if (element.classList.contains('coins-display')) {
                    element.innerHTML = `<i class="fas fa-coins"></i> ${balance || 0}`;
                } else {
                    element.textContent = balance || 0;
                }
            }
        });
    } catch (error) {
        console.error('Erro ao atualizar coins:', error);
    }
}

// Listener em tempo real para saldo de coins
const topMenuCoins = document.getElementById('topMenuCoins');
const coinsDisplay = document.querySelector('.coins-display');
(async () => {
    await userService.waitForAuth();
    if ((topMenuCoins || coinsDisplay) && userService.listenUserCoins) {
        userService.listenUserCoins((coins) => {
            if (topMenuCoins) topMenuCoins.textContent = coins || 0;
            if (coinsDisplay) coinsDisplay.innerHTML = `<i class="fas fa-coins"></i> ${coins || 0}`;
        });
    }
})();

// Função para verificar status da API
async function checarAPI() {
    try {
        const response = await fetch(`${API_CONFIG.BASE_URL}/status`, { 
            cache: 'no-store',
            headers: {
                'X-API-Key': API_CONFIG.API_KEY,
                'Origin': window.location.origin
            }
        });
        
        if (!response.ok) {
            console.error('API offline:', response.status);
            throw new Error('API offline');
        }
        
        const data = await response.json();
        console.log('Status da API:', data);
        
        // Aceita 'online', 'degraded' ou 'operational' como estados válidos
        if (data.status !== 'online' && data.status !== 'degraded' && data.status !== 'operational') {
            throw new Error('API em manutenção');
        }
        
        return true;
    } catch (e) {
        console.error('Erro ao verificar status da API:', e);
        window.location.replace('/pages/manutencao.html');
        return false;
    }
}

// Verifica a API a cada 30 segundos
let apiCheckInterval;
async function iniciarVerificacaoAPI() {
    try {
        const apiOnline = await checarAPI();
        if (apiOnline) {
            if (apiCheckInterval) {
                clearInterval(apiCheckInterval);
            }
            apiCheckInterval = setInterval(checarAPI, 30000);
        }
    } catch (error) {
        console.error('Erro ao iniciar verificação da API:', error);
    }
}

// Inicia a verificação da API
iniciarVerificacaoAPI(); 