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
    const form = document.getElementById('resetPasswordForm');
    const emailInput = document.getElementById('email');

    // Validação em tempo real do email
    emailInput.addEventListener('input', () => {
        const emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        if (!emailPattern.test(emailInput.value) && emailInput.value !== '') {
            showNotification('Por favor, insira um email válido', 'error');
        }
    });

    if (form) {
        form.addEventListener('submit', async (event) => {
            event.preventDefault();
            
            const email = emailInput.value;
            
            // Validação do email no envio
            const emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
            if (!emailPattern.test(email)) {
                showNotification('Por favor, insira um email válido', 'error');
                return;
            }
            
            try {
                await authService.resetPassword(email);
                showNotification(
                    'Email de recuperação enviado! Verifique sua caixa de entrada.',
                    'success'
                );
                setTimeout(() => {
                    window.location.href = '/pages/login.html';
                }, 3000);
            } catch (error) {
                console.error('Erro ao enviar email de recuperação:', error);
                let errorMessage;

                switch (error.code) {
                    case 'auth/user-not-found':
                        errorMessage = 'Este email não está cadastrado no sistema';
                        break;
                    case 'auth/invalid-email':
                        errorMessage = 'Formato de email inválido';
                        break;
                    case 'auth/too-many-requests':
                        errorMessage = 'Muitas tentativas. Tente novamente mais tarde';
                        break;
                    default:
                        errorMessage = 'Erro ao enviar email de recuperação';
                }
                
                showNotification(errorMessage, 'error');
            }
        });
    }
});

function showNotification(message, type) {
    const existingNotification = document.querySelector('.notification');
    if (existingNotification) {
        existingNotification.remove();
    }

    const notification = document.createElement('div');
    notification.className = `notification ${type}`;
    notification.textContent = message;
    
    document.body.appendChild(notification);
    
    setTimeout(() => {
        notification.style.animation = 'slideOut 0.3s ease-in-out forwards';
        setTimeout(() => notification.remove(), 300);
    }, 3000);
} 