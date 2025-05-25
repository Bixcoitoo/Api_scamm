import { authService } from './services/auth.service.js';
import { auth } from './firebase-config.js';

class RouteGuard {
    constructor() {
        this.publicPages = [
            '/pages/login.html',
            '/pages/registro.html',
            '/index.html',
            '/',
            '/pages/404.html'
        ];
        
        this.protectedRoutes = [
            '/pages/main.html',
            '/pages/profile.html'
        ];
        
        this.init();
    }

    async init() {
        const currentPath = window.location.pathname;
        
        if (this.isPublicPage(currentPath)) {
            return;
        }

        try {
            // Aguarda a inicialização do Firebase Auth
            await new Promise(resolve => setTimeout(resolve, 1000));
            
            const user = await new Promise((resolve) => {
                const unsubscribe = auth.onAuthStateChanged((user) => {
                    unsubscribe();
                    resolve(user);
                });
            });

            if (!user) {
                console.error('❌ Usuário não autenticado');
                window.location.replace('/pages/404.html');
                return;
            }

            const token = localStorage.getItem('authToken') || sessionStorage.getItem('authToken');
            if (!token) {
                console.error('❌ Token não encontrado');
                window.location.replace('/pages/404.html');
                return;
            }

            document.documentElement.style.display = 'block';
            console.log('✅ Usuário autenticado com sucesso');

        } catch (error) {
            console.error('Erro na verificação:', error);
            window.location.replace('/pages/404.html');
        }
    }

    isProtectedRoute(path) {
        return this.protectedRoutes.some(route => path.includes(route));
    }

    isPublicPage(path) {
        return this.publicPages.some(page => path.includes(page));
    }

    handleNavigation() {
        window.addEventListener('popstate', () => this.init());
    }
}

// Inicializa o guard
new RouteGuard(); 