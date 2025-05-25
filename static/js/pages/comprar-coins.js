document.addEventListener('DOMContentLoaded', async () => {
    console.log('🔵 Verificando autenticação em comprar-coins.html...');
    
    try {
        const token = await authService.getToken();
        console.log('📝 Token encontrado:', !!token);
        
        if (!token) {
            window.location.href = '/pages/login.html';
            return;
        }
        
        console.log('✅ Token válido, carregando página...');
        await initializePage();
    } catch (error) {
        console.error('Erro ao inicializar página:', error);
        showError('Erro ao carregar página. Por favor, tente novamente.');
    }
});

async function initializePage() {
    try {
        await updateCoinsDisplay();
        setupEventListeners();
    } catch (error) {
        console.error('Erro ao inicializar página:', error);
        showError('Erro ao carregar página. Por favor, tente novamente.');
    }
}

async function updateCoinsDisplay() {
    try {
        const saldo = await coinsService.getBalance();
        document.getElementById('saldo-atual').textContent = saldo.toFixed(2);
    } catch (error) {
        console.error('Erro ao atualizar saldo:', error);
        showError('Erro ao carregar saldo. Por favor, tente novamente.');
    }
}

function setupEventListeners() {
    const form = document.getElementById('comprar-coins-form');
    if (form) {
        form.addEventListener('submit', handleSubmit);
    }
}

async function handleSubmit(event) {
    event.preventDefault();
    
    try {
        const valor = parseFloat(document.getElementById('valor').value);
        const descricao = document.getElementById('descricao').value;
        
        if (isNaN(valor) || valor <= 0) {
            showError('Por favor, insira um valor válido.');
            return;
        }
        
        showLoading();
        const novoSaldo = await coinsService.addCredits(valor, descricao);
        hideLoading();
        
        document.getElementById('saldo-atual').textContent = novoSaldo.toFixed(2);
        showSuccess('Créditos adicionados com sucesso!');
        
        // Limpa o formulário
        event.target.reset();
    } catch (error) {
        hideLoading();
        console.error('Erro ao adicionar créditos:', error);
        showError('Erro ao adicionar créditos. Por favor, tente novamente.');
    }
}

function showLoading() {
    const button = document.querySelector('button[type="submit"]');
    if (button) {
        button.disabled = true;
        button.innerHTML = '<span class="spinner"></span> Processando...';
    }
}

function hideLoading() {
    const button = document.querySelector('button[type="submit"]');
    if (button) {
        button.disabled = false;
        button.textContent = 'Adicionar Créditos';
    }
}

function showError(message) {
    const errorDiv = document.getElementById('error-message');
    if (errorDiv) {
        errorDiv.textContent = message;
        errorDiv.style.display = 'block';
        setTimeout(() => {
            errorDiv.style.display = 'none';
        }, 5000);
    }
}

function showSuccess(message) {
    const successDiv = document.getElementById('success-message');
    if (successDiv) {
        successDiv.textContent = message;
        successDiv.style.display = 'block';
        setTimeout(() => {
            successDiv.style.display = 'none';
        }, 5000);
    }
} 