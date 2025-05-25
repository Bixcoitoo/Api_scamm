import { authService } from './services/auth.service.js';

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

document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('loginForm');
    const emailInput = document.getElementById('email');
    const passwordInput = document.getElementById('password');

    if (form) {
        form.addEventListener('submit', async (event) => {
            event.preventDefault();
            
            // Desabilita o formulário durante o processo
            const submitButton = form.querySelector('button[type="submit"]');
            submitButton.disabled = true;
            
            try {
                console.log('🔄 Tentando autenticar...');
                const result = await authService.login({
                    email: emailInput.value,
                    password: passwordInput.value
                });
                
                if (result.emailVerified === false) {
                    const errorMessage = 'É necessário verificar seu email antes de fazer login. Por favor, verifique sua caixa de entrada e spam para encontrar o link de verificação.';
                    await showCustomAlert(errorMessage);
                    showNotification(errorMessage, 'error', 8000);
                    emailInput.value = '';
                    passwordInput.value = '';
                    submitButton.disabled = false;
                    return;
                }
                
                console.log('✅ Login bem-sucedido:', result);
                localStorage.setItem('authToken', result.token);
                sessionStorage.setItem('authToken', result.token);
                localStorage.setItem('user', JSON.stringify(result.user));
                sessionStorage.setItem('user', JSON.stringify(result.user));
                
                showNotification('Login realizado com sucesso!', 'success');
                setTimeout(() => {
                    window.location.href = '/pages/main.html';
                }, 1000);
            } catch (error) {
                console.error('❌ Erro no login:', error);
                submitButton.disabled = false;
                
                let errorMessage;
                switch (error.code) {
                    case 'auth/user-not-found':
                        errorMessage = 'Este email não está cadastrado no sistema';
                        break;
                    case 'auth/wrong-password':
                        errorMessage = 'Senha incorreta para o email informado';
                        break;
                    case 'auth/invalid-email':
                        errorMessage = 'Formato de email inválido';
                        break;
                    case 'auth/too-many-requests':
                        errorMessage = 'Muitas tentativas. Tente novamente mais tarde';
                        break;
                    case 'auth/invalid-credential':
                        errorMessage = 'Email ou senha incorretos';
                        break;
                    default:
                        errorMessage = 'Erro ao fazer login. Tente novamente';
                }
                
                showNotification(errorMessage, 'error', 8000);
            }
        });
    }
});

function showNotification(message, type, duration = 3000) {
    // Remove notificações anteriores
    const existingNotifications = document.querySelectorAll('.notification');
    existingNotifications.forEach(notification => notification.remove());

    const notification = document.createElement('div');
    notification.className = `notification ${type}`;
    notification.textContent = message;
    
    document.body.appendChild(notification);
    
    setTimeout(() => {
        notification.style.animation = 'slideOut 0.3s ease-in-out forwards';
        setTimeout(() => notification.remove(), duration);
    }, duration);
}

function showCustomAlert(message) {
    return new Promise((resolve) => {
        const overlay = document.createElement('div');
        overlay.className = 'custom-alert-overlay';
        
        const alertBox = document.createElement('div');
        alertBox.className = 'custom-alert';
        
        const messageDiv = document.createElement('div');
        messageDiv.className = 'custom-alert-message';
        messageDiv.textContent = message;
        
        const button = document.createElement('button');
        button.className = 'custom-alert-button';
        button.textContent = 'OK';
        button.onclick = () => {
            document.body.removeChild(overlay);
            resolve();
        };
        
        alertBox.appendChild(messageDiv);
        alertBox.appendChild(button);
        overlay.appendChild(alertBox);
        document.body.appendChild(overlay);
    });
} 