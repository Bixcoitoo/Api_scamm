import API_CONFIG from '../config.js';
import { auth } from '../firebase-config.js';
import { tokenService } from './token.service.js';
import { 
    createUserWithEmailAndPassword,
    signInWithEmailAndPassword,
    signOut,
    sendPasswordResetEmail,
    updateProfile,
    setPersistence,
    browserLocalPersistence,
    browserSessionPersistence,
    sendEmailVerification
} from 'https://www.gstatic.com/firebasejs/10.8.0/firebase-auth.js';
import { doc, setDoc, getDoc, serverTimestamp } from 'https://www.gstatic.com/firebasejs/10.8.0/firebase-firestore.js';
import { db } from '../firebase-config.js';
import { userService } from './user.service.js';

class AuthService {
    constructor() {
        this.currentUser = null;
        this.persistence = localStorage.getItem('authPersistence') || 'local';
        this.protectedRoutes = ['/pages/main.html', '/pages/profile.html'];
        this.initialized = false;
    }

    // Função para gerenciar cookies de forma segura
    setSecureCookie(name, value, options = {}) {
        const defaultOptions = {
            path: '/',
            secure: true,
            sameSite: 'Strict',
            httpOnly: true,
            maxAge: 7 * 24 * 60 * 60 // 7 dias
        };

        const cookieOptions = { ...defaultOptions, ...options };
        let cookie = `${name}=${value}`;
        
        for (const [key, value] of Object.entries(cookieOptions)) {
            cookie += `; ${key}=${value}`;
        }

        document.cookie = cookie;
    }

    getCookie(name) {
        const value = `; ${document.cookie}`;
        const parts = value.split(`; ${name}=`);
        if (parts.length === 2) return parts.pop().split(';').shift();
        return null;
    }

    removeCookie(name) {
        this.setSecureCookie(name, '', { maxAge: -1 });
    }

    async initializeAuth() {
        if (this.initialized) return;
        
        return new Promise((resolve) => {
            const unsubscribe = auth.onAuthStateChanged(async (user) => {
                this.initialized = true;
                this.currentUser = user;
                
                if (user) {
                    try {
                        // Tenta renovar o token do Firebase
                        const token = await user.getIdToken(true);
                        tokenService.setToken(token);
                        
                        // Verifica se precisa renovar o token da API
                        await tokenService.refreshTokenIfNeeded();
                    } catch (error) {
                        console.error('Erro ao renovar token:', error);
                    }
                }
                
                console.log('Firebase Auth inicializado:', { 
                    initialized: this.initialized, 
                    currentUser: !!this.currentUser 
                });
                unsubscribe();
                resolve(user);
            });
        });
    }

    async login(credentials) {
        try {
            await this.initializeAuth();
            const userCredential = await signInWithEmailAndPassword(auth, credentials.email, credentials.password);
            const user = userCredential.user;

            const response = await fetch(`${API_CONFIG.BASE_URL}${API_CONFIG.ENDPOINTS.AUTH}/login`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(credentials)
            });

            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.message);
            }

            const data = await response.json();
            
            // Usando o TokenService para gerenciar tokens
            tokenService.setToken(data.token);
            if (data.refreshToken) {
                tokenService.setRefreshToken(data.refreshToken);
            }
            
            // Armazenando apenas dados não sensíveis
            const safeUserData = {
                uid: user.uid,
                email: user.email,
                displayName: user.displayName,
                emailVerified: user.emailVerified
            };
            
            this.currentUser = user;
            
            return { ...data, user: safeUserData };
        } catch (error) {
            console.error('Erro no login:', error);
            throw new Error('Erro ao fazer login: ' + error.message);
        }
    }

    async register(userData) {
        try {
            const response = await fetch(`${API_CONFIG.BASE_URL}${API_CONFIG.ENDPOINTS.AUTH}/register`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(userData)
            });

            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.message);
            }

            const data = await response.json();
            this.currentUser = data.user;
            localStorage.setItem('token', data.token);
            return data;
        } catch (error) {
            throw new Error('Erro ao registrar: ' + error.message);
        }
    }

    async logout() {
        try {
            await fetch(`${API_CONFIG.BASE_URL}${API_CONFIG.ENDPOINTS.AUTH}/logout`, {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${tokenService.getToken()}`
                }
            });
            
            this.currentUser = null;
            tokenService.clearTokens();
            window.location.href = '/pages/login.html';
        } catch (error) {
            throw new Error('Erro ao fazer logout: ' + error.message);
        }
    }

    async resetPassword(email) {
        try {
            await sendPasswordResetEmail(auth, email);
        } catch (error) {
            console.error('Erro ao enviar email de recuperação:', error);
            throw error;
        }
    }

    isAuthenticated() {
        return tokenService.hasValidToken();
    }

    getCurrentUser() {
        return this.currentUser;
    }

    getToken() {
        return tokenService.getToken();
    }

    handleAuthError(error) {
        const errorMessages = {
            'auth/user-not-found': 'Usuário não encontrado',
            'auth/wrong-password': 'Senha incorreta',
            'auth/invalid-email': 'Email inválido',
            'auth/user-disabled': 'Conta desativada',
            'auth/too-many-requests': 'Muitas tentativas. Tente novamente mais tarde',
            'auth/invalid-credential': 'Credenciais inválidas. Verifique seu email e senha',
            'auth/email-already-in-use': 'Este email já está cadastrado. Por favor, use outro email ou faça login',
            'auth/operation-not-allowed': 'Operação não permitida. Entre em contato com o suporte',
            'auth/weak-password': 'A senha deve ter pelo menos 6 caracteres',
            'auth/unauthorized-continue-uri': 'Erro na configuração do domínio. Por favor, tente novamente mais tarde ou entre em contato com o suporte.',
        };
        
        const message = errorMessages[error.code] || error.message;
        console.log('Código do erro:', error.code);
        console.log('Mensagem traduzida:', message);
        
        return new Error(message);
    }

    // Verifica o estado da sessão
    async checkSession() {
        try {
            // Aguarda a inicialização do Firebase Auth
            await this.initializeAuth();
            
            // Verifica o token usando o TokenService
            const hasValidToken = await tokenService.refreshTokenIfNeeded();
            if (!hasValidToken) {
                console.log('Token inválido ou expirado');
                return null;
            }

            // Verifica o estado atual do Firebase Auth
            const currentUser = auth.currentUser;
            if (!currentUser) {
                console.log('Usuário não encontrado no Firebase Auth');
                return null;
            }

            // Tenta renovar o token do Firebase
            try {
                const token = await currentUser.getIdToken(true);
                tokenService.setToken(token);
            } catch (error) {
                console.error('Erro ao renovar token do Firebase:', error);
            }

            // Obtém o token atualizado
            const token = tokenService.getToken();
            console.log('Sessão válida:', { token: !!token, user: !!currentUser });
            return { token, user: currentUser };
        } catch (error) {
            console.error('Erro ao verificar sessão:', error);
            return null;
        }
    }

    isProtectedRoute(path) {
        return this.protectedRoutes.some(route => path.includes(route));
    }

    async validateAccess() {
        const currentPath = window.location.pathname;
        const user = await this.checkSession();

        if (!user && this.isProtectedRoute(currentPath)) {
            window.location.href = '/pages/login.html';
            return false;
        }
        return true;
    }
}

export const authService = new AuthService(); 