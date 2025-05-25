import { authService } from './services/auth.service.js';
import { FormValidator } from './validation.js';

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
    const form = document.getElementById('registerForm');
    const passwordInput = document.getElementById('password');
    const usernameInput = document.getElementById('username');
    const emailInput = document.getElementById('email');
    const confirmPasswordInput = document.getElementById('confirmPassword');
    const passwordToggle = document.querySelector('.password-toggle');
    
    if (form && passwordInput) {
        const validator = new FormValidator('registerForm');
        
        // Validação do nome de usuário
        usernameInput.addEventListener('input', () => {
            const usernamePattern = /^[a-zA-Z0-9_]{3,20}$/;
            if (!usernamePattern.test(usernameInput.value)) {
                showNotification('Nome de usuário deve ter entre 3 e 20 caracteres e conter apenas letras, números e _', 'error');
            }
        });

        // Validação do email
        emailInput.addEventListener('input', () => {
            const emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
            if (!emailPattern.test(emailInput.value)) {
                showNotification('Por favor, insira um email válido', 'error');
            }
        });

        // Validação da senha em tempo real
        passwordInput.addEventListener('input', () => {
            validator.validatePassword(passwordInput);
        });

        // Validação da confirmação de senha
        confirmPasswordInput.addEventListener('input', () => {
            if (confirmPasswordInput.value !== passwordInput.value) {
                showNotification('As senhas não coincidem', 'error');
            }
        });

        if (passwordToggle) {
            passwordToggle.addEventListener('click', () => {
                const type = passwordInput.type === 'password' ? 'text' : 'password';
                passwordInput.type = type;
                
                // Alterna o ícone
                const icon = passwordToggle.querySelector('i');
                icon.className = type === 'password' ? 'far fa-eye' : 'far fa-eye-slash';
            });
        }

        form.addEventListener('submit', async (event) => {
            event.preventDefault();
            
            // Validações antes do envio
            const emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
            const usernamePattern = /^[a-zA-Z0-9_]{3,20}$/;
            
            if (!usernamePattern.test(usernameInput.value)) {
                showNotification('Nome de usuário inválido', 'error');
                return;
            }
            
            if (!emailPattern.test(emailInput.value)) {
                showNotification('Email inválido', 'error');
                return;
            }
            
            if (confirmPasswordInput.value !== passwordInput.value) {
                showNotification('As senhas não coincidem', 'error');
                return;
            }
            
            const formData = {
                name: usernameInput.value, // Usando username em vez de name
                email: emailInput.value,
                password: passwordInput.value
            };
            
            try {
                const result = await authService.register(formData);
                showNotification(result.message, 'success', 6000); // Aumenta o tempo de exibição para 6 segundos
                setTimeout(() => {
                    window.location.href = '/pages/login.html';
                }, 6000);
            } catch (error) {
                console.error('Erro no registro:', error);
                showNotification(error.message, 'error');
            }
        });
    }
});

function showNotification(message, type) {
    // Remove notificações anteriores
    const existingNotifications = document.querySelectorAll('.notification');
    existingNotifications.forEach(notification => notification.remove());

    const notification = document.createElement('div');
    notification.className = `notification ${type}`;
    notification.textContent = message;
    
    document.body.appendChild(notification);
    setTimeout(() => {
        notification.style.animation = 'slideOut 0.3s ease-in-out forwards';
        setTimeout(() => notification.remove(), 300);
    }, 3000);
} 