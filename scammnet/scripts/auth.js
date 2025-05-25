import { 
    createUserWithEmailAndPassword,
    signInWithEmailAndPassword,
    signOut,
    sendPasswordResetEmail,
    updateProfile
} from 'https://www.gstatic.com/firebasejs/10.8.0/firebase-auth.js';
import { authService } from './services/auth.service.js';
import { userService } from './services/user.service.js';

// Verifica se o usuário está logado
function checkAuth() {
    const publicPages = ['/pages/login.html', '/pages/registro.html', '/index.html', '/', '/pages/404.html'];
    const currentPage = window.location.pathname;
    
    // Se estiver em uma página pública, não faz nada
    if (publicPages.includes(currentPage)) {
        return;
    }
    
    // Se não estiver autenticado e tentar acessar página protegida
    if (!authService.isAuthenticated() && !publicPages.includes(currentPage)) {
        window.location.href = '/pages/404.html';
        return;
    }
}

// Função para atualizar o nome do usuário na interface
function updateUserDisplay() {
    const user = authService.getCurrentUser();
    if (user) {
        const userDisplays = document.querySelectorAll('.user-display');
        userDisplays.forEach(display => {
            display.textContent = user.displayName || user.email;
        });
    }
}

// Função de registro
async function handleRegister(event) {
    event.preventDefault();
    console.log('Iniciando registro...');
    
    const formData = {
        username: document.getElementById('regUsername').value,
        email: document.getElementById('regEmail').value,
        password: document.getElementById('regPassword').value,
        confirmPassword: document.getElementById('regConfirmPassword').value
    };
    
    console.log('Dados do formulário:', formData);
    
    if (formData.password !== formData.confirmPassword) {
        showNotification('As senhas não coincidem', 'error');
        return;
    }
    
    try {
        const user = await authService.register(formData);
        console.log('Usuário registrado:', user);
        showNotification('Registro realizado com sucesso!', 'success');
        window.location.href = '/pages/main.html';
    } catch (error) {
        console.error('Erro no registro:', error);
        showNotification(error.message, 'error');
    }
}

// Função de login
async function handleLogin(event) {
    event.preventDefault();
    
    const credentials = {
        email: document.getElementById('email').value,
        password: document.getElementById('password').value
    };
    
    try {
        await authService.login(credentials);
        await userService.initializeUserData(authService.getCurrentUser());
        showNotification('Login realizado com sucesso!', 'success');
        window.location.href = '/pages/main.html';
    } catch (error) {
        showNotification(error.message, 'error');
    }
}

// Função de logout
async function logout() {
    try {
        await authService.logout();
        window.location.href = '/pages/login.html';
    } catch (error) {
        showNotification(error.message, 'error');
    }
}

// Função para mostrar notificações
function showNotification(message, type) {
    const notification = document.createElement('div');
    notification.className = `notification ${type}`;
    notification.textContent = message;
    
    document.body.appendChild(notification);
    setTimeout(() => notification.remove(), 3000);
}

// Executa verificação de auth quando a página carrega
document.addEventListener('DOMContentLoaded', function() {
    checkAuth();
    updateUserDisplay();
    const registerForm = document.getElementById('registerForm');
    if (registerForm) {
        registerForm.addEventListener('submit', handleRegister);
    }
}); 