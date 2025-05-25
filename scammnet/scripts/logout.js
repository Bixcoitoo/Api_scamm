import { authService } from './services/auth.service.js';

// Função de logout
async function handleLogout() {
    try {
        await authService.logout();
        window.location.replace('/index.html');
    } catch (error) {
        console.error('Erro ao fazer logout:', error);
    }
}

// Adiciona event listeners nos botões de logout
document.querySelectorAll('.logout-btn').forEach(button => {
    button.addEventListener('click', (e) => {
        e.preventDefault();
        handleLogout();
    });
}); 