class CoinsService {
    constructor() {
        this.baseUrl = '/api';
    }

    async getBalance() {
        try {
            const user = await authService.getCurrentUser();
            if (!user) {
                throw new Error('Usuário não autenticado');
            }

            const response = await fetch(`${this.baseUrl}/creditos/saldo/${user.uid}`, {
                method: 'GET',
                headers: {
                    'Authorization': `Bearer ${await authService.getToken()}`
                }
            });

            if (!response.ok) {
                throw new Error('Erro ao buscar saldo');
            }

            const data = await response.json();
            return data.saldo || 0;
        } catch (error) {
            console.error('Erro ao obter saldo:', error);
            return 0;
        }
    }

    async addCredits(amount, description) {
        try {
            const user = await authService.getCurrentUser();
            if (!user) {
                throw new Error('Usuário não autenticado');
            }

            const response = await fetch(`${this.baseUrl}/creditos/adicionar`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${await authService.getToken()}`
                },
                body: JSON.stringify({
                    user_id: user.uid,
                    valor: amount,
                    tipo: 'recarga',
                    descricao: description
                })
            });

            if (!response.ok) {
                throw new Error('Erro ao adicionar créditos');
            }

            const data = await response.json();
            return data.novo_saldo;
        } catch (error) {
            console.error('Erro ao adicionar créditos:', error);
            throw error;
        }
    }

    async getTransactionHistory() {
        try {
            const user = await authService.getCurrentUser();
            if (!user) {
                throw new Error('Usuário não autenticado');
            }

            const response = await fetch(`${this.baseUrl}/creditos/historico/${user.uid}`, {
                method: 'GET',
                headers: {
                    'Authorization': `Bearer ${await authService.getToken()}`
                }
            });

            if (!response.ok) {
                throw new Error('Erro ao buscar histórico');
            }

            return await response.json();
        } catch (error) {
            console.error('Erro ao buscar histórico:', error);
            return [];
        }
    }

    async getPrices() {
        try {
            const response = await fetch(`${this.baseUrl}/admin/precos`, {
                method: 'GET',
                headers: {
                    'Authorization': `Bearer ${await authService.getToken()}`
                }
            });

            if (!response.ok) {
                throw new Error('Erro ao buscar preços');
            }

            return await response.json();
        } catch (error) {
            console.error('Erro ao buscar preços:', error);
            throw new Error('Não foi possível carregar os preços das consultas');
        }
    }

    async getEndpointCost(endpoint) {
        try {
            const prices = await this.getPrices();
            return prices[endpoint] || 0;
        } catch (error) {
            console.error('Erro ao obter custo do endpoint:', error);
            throw error;
        }
    }
}

const coinsService = new CoinsService(); 