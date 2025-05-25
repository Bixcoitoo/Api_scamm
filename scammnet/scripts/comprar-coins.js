import { auth } from './firebase-config.js';
import { authService } from './services/auth.service.js';
import { userService } from './services/user.service.js';
import { coinsService } from './services/coins.service.js';
import { showNotification } from './utils/notifications.js';

// Middleware de autenticação
(async function() {
    try {
        document.documentElement.style.display = 'none';
        
        // Aguarda um momento para garantir que o Firebase Auth esteja inicializado
        await new Promise(resolve => setTimeout(resolve, 100));
        
        const user = await authService.checkSession();
        
        if (!user) {
            console.error('❌ Usuário não autenticado');
            window.location.replace('/pages/404.html');
            throw new Error('Acesso não autorizado');
        }
        
        // Verifica token em ambos storages
        const token = localStorage.getItem('authToken') || sessionStorage.getItem('authToken');
        if (!token) {
            console.error('❌ Token não encontrado');
            await authService.logout();
            return;
        }
        
        // Carrega os dados do usuário antes de exibir a página
        await loadUserData();
        document.documentElement.style.display = 'block';
    } catch (error) {
        console.error('Erro na verificação de autenticação:', error);
        window.location.replace('/pages/404.html');
    }
})();

async function loadUserData() {
    try {
        const profile = await userService.getUserProfile();
        if (!profile) {
            throw new Error('Perfil não encontrado');
        }

        // Atualiza elementos apenas se existirem
        const userDisplay = document.getElementById('userDisplay');
        const topMenuCoins = document.getElementById('topMenuCoins');

        if (userDisplay) {
            userDisplay.textContent = profile.username || 'Usuário';
        }

        if (topMenuCoins) {
            topMenuCoins.textContent = profile.coins || '0';
        }

    } catch (error) {
        console.error('Erro ao carregar dados do usuário:', error);
        throw error;
    }
}

// Observador de mudanças na autenticação
auth.onAuthStateChanged(async (user) => {
    if (!user) {
        window.location.replace('/pages/404.html');
    }
});

// Adiciona event listeners nos botões de compra
document.querySelectorAll('.buy-btn').forEach(button => {
    button.addEventListener('click', async (e) => {
        e.preventDefault();
        const coins = e.target.dataset.coins;
        const value = e.target.dataset.value;
        
        try {
            // Aqui você implementará a lógica de pagamento
            console.log(`Iniciando compra de ${coins} coins por R$ ${value}`);
        } catch (error) {
            console.error('Erro ao processar compra:', error);
        }
    });
});

document.addEventListener('DOMContentLoaded', async () => {
    try {
        // Atualiza display de coins
        const updateCoinsDisplay = async () => {
            const coinsDisplay = document.getElementById('topMenuCoins');
            if (!coinsDisplay) {
                console.warn('❌ Elemento de exibição de coins não encontrado');
                return;
            }
            const coins = await coinsService.getBalance(true);
            coinsDisplay.textContent = coins;
        };

        // Aguarda autenticação antes de atualizar o saldo
        await userService.waitForAuth();
        await updateCoinsDisplay();

        // Adiciona listeners aos botões de compra
        document.querySelectorAll('.buy-btn').forEach(button => {
            button.addEventListener('click', async () => {
                const coins = parseInt(button.dataset.coins);
                const value = parseFloat(button.dataset.value);

                try {
                    button.disabled = true;
                    button.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Processando...';

                    await coinsService.processTransaction('purchase', coins, {
                        valor: value,
                        metodo: 'cartao'
                    });

                    showNotification(`Compra de ${coins} coins realizada com sucesso!`, 'success');
                    await updateCoinsDisplay();

                } catch (error) {
                    console.error('Erro na compra:', error);
                    showNotification('Erro ao processar a compra', 'error');
                } finally {
                    button.disabled = false;
                    button.innerHTML = 'Comprar';
                }
            });
        });

        // Listener em tempo real para saldo de coins
        (async () => {
            await userService.waitForAuth();
            if (topMenuCoins && userService.listenUserCoins) {
                userService.listenUserCoins((coins) => {
                    topMenuCoins.textContent = coins || 0;
                });
            }
        })();
    } catch (error) {
        console.error('Erro ao inicializar página:', error);
    }
});

(async function checarAPI() {
    try {
        const response = await fetch('https://api.magalha.space/', { cache: 'no-store' });
        if (!response.ok) throw new Error('API offline');
        const data = await response.json();
        if (data.status !== 'online') throw new Error('API em manutenção');
    } catch (e) {
        window.location.replace('/pages/manutencao.html');
    }
})(); 