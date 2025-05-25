import { auth } from './firebase-config.js';
import { authService } from './services/auth.service.js';
import { userService } from './services/user.service.js';

// Middleware de autenticação
(async function() {
    try {
        document.documentElement.style.display = 'none';
        
        // Aguarda um momento para garantir que o Firebase Auth esteja inicializado
        await new Promise(resolve => setTimeout(resolve, 100));
        
        const session = await authService.checkSession();
        console.log('Verificação de sessão em profile:', session);
        
        if (!session || !session.user) {
            console.error('❌ Usuário não autenticado');
            window.location.replace('/pages/404.html');
            return;
        }
        
        // Carrega o perfil do usuário
        await loadUserProfile();
        document.documentElement.style.display = 'block';
    } catch (error) {
        console.error('Erro na verificação de autenticação:', error);
        window.location.replace('/pages/404.html');
    }
})();

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

async function initializePage(user) {
    try {
        if (!user) {
            console.error('❌ Usuário não autenticado');
            window.location.replace('/pages/404.html');
            return;
        }

        document.documentElement.style.display = 'block';
        
        // Carrega os dados do perfil
        const profile = await userService.getUserProfile();
        if (profile) {
            document.getElementById('headerUsername').textContent = profile.username || 'Usuário';
            document.getElementById('headerEmail').textContent = profile.email || '';
            document.getElementById('username').value = profile.username || '';
            document.getElementById('email').value = profile.email || '';
        }
    } catch (error) {
        console.error('Erro ao carregar perfil:', error);
        window.location.replace('/pages/404.html');
    }
}

// Função para atualizar o header
function updateHeaderInfo(user, profile) {
    // Atualiza o nome e email no header
    const headerUsername = document.getElementById('headerUsername');
    const headerEmail = document.getElementById('headerEmail');
    
    if (headerUsername) {
        headerUsername.textContent = profile.username || user.displayName || 'Usuário';
    }
    
    if (headerEmail) {
        headerEmail.textContent = user.email;
    }

    // Atualiza o nome no menu superior
    const userDisplay = document.getElementById('userDisplay');
    if (userDisplay) {
        userDisplay.textContent = profile.username || user.displayName || 'Usuário';
    }
}

// Observador de mudanças na autenticação
auth.onAuthStateChanged((user) => {
    if (!user) {
        console.log('❌ Usuário desconectado');
        window.location.replace('/index.html'); // Alterado para redirecionar para index
    }
});

async function loadUserProfile() {
    try {
        const session = await authService.checkSession();
        if (!session || !session.user) {
            console.error('❌ Sessão inválida');
            window.location.replace('/pages/404.html');
            return;
        }

        const profile = await userService.getUserProfile();
        if (!profile) {
            console.error('❌ Perfil não encontrado');
            window.location.replace('/pages/404.html');
            return;
        }

        console.log('Carregando perfil:', profile);

        // Atualiza informações básicas com verificação de elementos
        const displayNameElement = document.getElementById('userDisplay');
        const userEmailElement = document.getElementById('headerEmail');
        const usernameElement = document.getElementById('username');
        const coinBalanceElement = document.getElementById('coinBalance');
        const headerUsernameElement = document.getElementById('headerUsername');

        // Atualiza elementos apenas se existirem
        if (displayNameElement) {
            displayNameElement.textContent = profile.username || 'Usuário';
        }
        
        if (headerUsernameElement) {
            headerUsernameElement.textContent = profile.username || 'Usuário';
        }

        if (userEmailElement) {
            userEmailElement.textContent = session.user.email || '';
        }

        if (usernameElement) {
            usernameElement.value = profile.username || '';
        }

        if (coinBalanceElement) {
            coinBalanceElement.textContent = `${profile.coins || 0} coins`;
        }

        try {
            // Carrega histórico de transações se existir o elemento
            const transactions = await userService.getTransactionHistory();
            if (transactions) {
                displayTransactions(transactions);
            }
        } catch (error) {
            console.error('Erro ao carregar transações:', error);
            // Não redireciona para 404 se houver erro ao carregar transações
            displayTransactions([]);
        }

        // Após carregar o perfil normalmente, adicionar o listener para coins em tempo real
        if (coinBalanceElement && userService.listenUserCoins) {
            userService.listenUserCoins((coins) => {
                coinBalanceElement.textContent = `${coins || 0} coins`;
            });
        }
    } catch (error) {
        console.error('Erro ao carregar perfil:', error);
        window.location.replace('/pages/404.html');
    }
}

// Função para validar o nome de usuário
function validateUsername(username) {
    // Regex que permite apenas letras e underscores
    const regex = /^[a-zA-Z_]+$/;
    
    if (username.length > 16) {
        throw new Error('O nome de usuário não pode ter mais que 16 caracteres');
    }
    
    if (!regex.test(username)) {
        throw new Error('O nome de usuário só pode conter letras e underscores');
    }
    
    if (username.length < 3) {
        throw new Error('O nome de usuário deve ter pelo menos 3 caracteres');
    }
    
    return true;
}

// Função para atualizar o perfil
async function updateUserProfile(event) {
    event.preventDefault();
    
    try {
        const username = document.getElementById('username').value.trim();
        
        // Valida o nome de usuário
        validateUsername(username);
        
        // Atualiza o perfil no Firebase
        await userService.updateProfile({
            username: username
        });

        // Atualiza a interface
        const user = auth.currentUser;
        const profile = await userService.getUserProfile();
        updateHeaderInfo(user, profile);

        showNotification('Perfil atualizado com sucesso!', 'success');
    } catch (error) {
        console.error('Erro ao atualizar perfil:', error);
        showNotification(error.message, 'error');
    }
}

// Adiciona o event listener no formulário
document.getElementById('personalInfoForm').addEventListener('submit', updateUserProfile);

// Adiciona validação em tempo real
document.getElementById('username').addEventListener('input', function(e) {
    const input = e.target;
    const submitButton = document.querySelector('#personalInfoForm button[type="submit"]');
    const helpText = document.getElementById('username-help') || createHelpText();
    
    try {
        validateUsername(input.value.trim());
        input.classList.remove('invalid');
        submitButton.disabled = false;
        helpText.textContent = 'Nome de usuário válido';
        helpText.style.color = 'var(--primary-color)';
    } catch (error) {
        input.classList.add('invalid');
        submitButton.disabled = true;
        helpText.textContent = error.message;
        helpText.style.color = '#ff0000';
    }
});

// Função para criar o elemento de texto de ajuda
function createHelpText() {
    const helpText = document.createElement('small');
    helpText.id = 'username-help';
    helpText.style.display = 'block';
    helpText.style.marginTop = '0.5rem';
    document.querySelector('.form-group').appendChild(helpText);
    return helpText;
}

// Função para mostrar notificações
function showNotification(message, type) {
    // Implementar sua lógica de notificação aqui
    alert(message); // Temporário, substitua por sua implementação de notificação
}

function displayTransactions(transactions) {
    const transactionsList = document.querySelector('.transactions-list');
    if (!transactionsList) return;

    if (!transactions || transactions.length === 0) {
        transactionsList.innerHTML = `
            <h4>Histórico de Transações</h4>
            <p class="no-transactions">Nenhuma transação encontrada</p>
        `;
        return;
    }

    const transactionsHTML = transactions.map(transaction => `
        <div class="transaction-item ${transaction.valor < 0 ? 'debit' : 'credit'}">
            <div class="transaction-info">
                <span class="transaction-type">${transaction.tipo}</span>
                <span class="transaction-date">${new Date(transaction.timestamp).toLocaleDateString()}</span>
            </div>
            <span class="transaction-amount">${transaction.valor} coins</span>
        </div>
    `).join('');

    transactionsList.innerHTML = `
        <h4>Histórico de Transações</h4>
        ${transactionsHTML}
    `;
}

// Função de logout
async function logout() {
    try {
        await authService.logout();
        window.location.replace('/index.html'); // Alterado para redirecionar para index
    } catch (error) {
        console.error('Erro ao fazer logout:', error);
    }
}

// Adiciona o event listener no botão de logout
document.querySelector('a[onclick="logout()"]').addEventListener('click', (e) => {
    e.preventDefault();
    logout();
});

document.querySelector('.neon-button').addEventListener('click', async () => {
    // Implementar integração com gateway de pagamento
    // Após confirmação do pagamento, atualizar coins via backend
}); 