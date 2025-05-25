class TokenService {
    constructor() {
        this.tokenKey = 'authToken';
        this.refreshTokenKey = 'refreshToken';
        this.tokenExpiryKey = 'tokenExpiry';
    }

    // Armazena o token em ambos storages para persistência
    setToken(token, expiryInMinutes = 60) {
        const expiry = new Date();
        expiry.setMinutes(expiry.getMinutes() + expiryInMinutes);
        
        // Armazena em ambos storages para compatibilidade
        localStorage.setItem(this.tokenKey, token);
        sessionStorage.setItem(this.tokenKey, token);
        localStorage.setItem(this.tokenExpiryKey, expiry.toISOString());
        sessionStorage.setItem(this.tokenExpiryKey, expiry.toISOString());
    }

    // Armazena o refresh token
    setRefreshToken(token) {
        localStorage.setItem(this.refreshTokenKey, token);
        sessionStorage.setItem(this.refreshTokenKey, token);
    }

    // Obtém o token atual, verificando ambos storages
    getToken() {
        return localStorage.getItem(this.tokenKey) || sessionStorage.getItem(this.tokenKey);
    }

    // Obtém o refresh token
    getRefreshToken() {
        return localStorage.getItem(this.refreshTokenKey) || sessionStorage.getItem(this.refreshTokenKey);
    }

    // Verifica se o token está expirado
    isTokenExpired() {
        const expiry = localStorage.getItem(this.tokenExpiryKey) || sessionStorage.getItem(this.tokenExpiryKey);
        if (!expiry) return true;
        
        return new Date(expiry) <= new Date();
    }

    // Remove todos os tokens
    clearTokens() {
        localStorage.removeItem(this.tokenKey);
        localStorage.removeItem(this.refreshTokenKey);
        localStorage.removeItem(this.tokenExpiryKey);
        sessionStorage.removeItem(this.tokenKey);
        sessionStorage.removeItem(this.refreshTokenKey);
        sessionStorage.removeItem(this.tokenExpiryKey);
    }

    // Verifica se existe um token válido
    hasValidToken() {
        const token = this.getToken();
        if (!token) return false;
        
        if (this.isTokenExpired()) {
            this.clearTokens();
            return false;
        }
        
        return true;
    }

    // Renova o token se necessário
    async refreshTokenIfNeeded() {
        if (!this.hasValidToken() && this.getRefreshToken()) {
            try {
                const response = await fetch(`${API_CONFIG.BASE_URL}/auth/refresh`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({
                        refreshToken: this.getRefreshToken()
                    })
                });

                if (response.ok) {
                    const data = await response.json();
                    this.setToken(data.token);
                    this.setRefreshToken(data.refreshToken);
                    return true;
                }
            } catch (error) {
                console.error('Erro ao renovar token:', error);
            }
        }
        return this.hasValidToken();
    }
}

export const tokenService = new TokenService(); 