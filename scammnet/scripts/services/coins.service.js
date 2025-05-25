import { tokenService } from './token.service.js';
import { userService } from './user.service.js';
import API_CONFIG from '../config.js';

class CoinsService {
    constructor() {
        this.API_URL = API_CONFIG.BASE_URL;
        this.cachedBalance = null;
        this.lastUpdate = null;
        this.cacheTimeout = 5 * 60 * 1000; // 5 minutos
        this.cachedPrices = null;
        this.pricesLastUpdate = null;
    }

    async getBalance(forceUpdate = false) {
        if (forceUpdate || !this.cachedBalance || Date.now() - this.lastUpdate > this.cacheTimeout) {
            const profile = await userService.getUserProfile();
            if (!profile) {
                console.error('Perfil do usuário não encontrado ou usuário não autenticado');
                this.cachedBalance = 0;
                this.lastUpdate = Date.now();
                return 0;
            }
            this.cachedBalance = profile.coins || 0;
            this.lastUpdate = Date.now();
        }
        return this.cachedBalance;
    }

    async canPerformAction(cost) {
        const balance = await this.getBalance(true);
        return balance >= cost;
    }

    async processTransaction(type, amount, details = {}) {
        const transaction = await userService.createTransaction(type, amount, details);
        await this.getBalance(true);
        return transaction;
    }

    async processConsultaRequest(endpoint, data) {
        try {
            const token = localStorage.getItem('authToken') || sessionStorage.getItem('authToken');
            if (!token) {
                throw new Error('Sessão expirada. Por favor, faça login novamente.');
            }

            // Obtém o ID do usuário atual
            const user = await userService.getUserProfile();
            if (!user) {
                throw new Error('Usuário não encontrado. Por favor, faça login novamente.');
            }

            console.log('Dados recebidos:', data);

            // Formata os dados conforme esperado pela API
            let requestData = {};
            
            if (endpoint === '/consulta/cpf') {
                const cpf = data.cpf?.replace(/\D/g, '');
                if (!cpf || cpf.length !== 11) {
                    throw new Error('CPF inválido. Digite um CPF com 11 dígitos.');
                }
                requestData = { cpf };
            } else if (endpoint === '/consulta/telefone') {
                const telefone = data.telefone?.replace(/\D/g, '');
                if (!telefone || telefone.length !== 11) {
                    throw new Error('Telefone inválido. Digite um número com 11 dígitos.');
                }
                requestData = { telefone };
            } else if (endpoint === '/consulta/nome') {
                const nome = data.nome?.trim().toUpperCase();
                if (!nome || nome.split(' ').length < 2) {
                    throw new Error('Nome inválido. Digite o nome completo.');
                }
                requestData = { nome };
            }

            console.log('Dados formatados para envio:', requestData);

            // Adiciona o user_id como parâmetro de query
            const queryParams = new URLSearchParams({
                user_id: user.uid
            });

            const url = `${this.API_URL}${endpoint}?${queryParams}`;
            console.log('URL da requisição:', url);

            const response = await fetch(url, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`,
                    'X-API-Key': API_CONFIG.API_KEY,
                    'Origin': window.location.origin
                },
                body: JSON.stringify(requestData)
            });

            console.log('Resposta da API:', response.status);

            if (!response.ok) {
                let errorMessage = 'Erro ao processar consulta';
                
                try {
                    const errorData = await response.json();
                    console.log('Dados do erro:', errorData);
                    
                    if (response.status === 401) {
                        localStorage.removeItem('authToken');
                        sessionStorage.removeItem('authToken');
                        errorMessage = 'Sessão expirada. Por favor, faça login novamente.';
                    } else if (response.status === 422) {
                        if (errorData.detail && Array.isArray(errorData.detail)) {
                            const errors = errorData.detail.map(err => {
                                if (err.type === 'missing') {
                                    return `Campo obrigatório ausente: ${err.loc[err.loc.length - 1]}`;
                                }
                                return err.msg;
                            });
                            errorMessage = errors.join(', ');
                        } else {
                            errorMessage = 'Dados inválidos. Verifique os campos e tente novamente.';
                        }
                    } else if (response.status === 500) {
                        errorMessage = 'Erro interno do servidor. Por favor, tente novamente mais tarde.';
                    } else {
                        errorMessage = errorData.detail || errorData.message || errorMessage;
                    }
                } catch (e) {
                    console.error('Erro ao processar resposta de erro:', e);
                }
                
                throw new Error(errorMessage);
            }

            const result = await response.json();
            console.log('Resultado da consulta:', result);

            if (!result) {
                throw new Error('Nenhum resultado encontrado para esta consulta.');
            }

            return result;
        } catch (error) {
            console.error('Erro ao processar consulta:', error);
            if (error.message.includes('Failed to fetch')) {
                throw new Error('Não foi possível conectar ao servidor. Verifique sua conexão e tente novamente.');
            }
            throw error;
        }
    }

    async getCoinsList() {
        try {
            const token = tokenService.getToken();
            if (!token) {
                throw new Error('Usuário não autenticado');
            }

            const response = await fetch(`${this.API_URL}/coins`, {
                headers: {
                    'Authorization': `Bearer ${token}`
                }
            });

            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.message || 'Erro ao obter lista de moedas');
            }

            return await response.json();
        } catch (error) {
            console.error('Erro ao obter lista de moedas:', error);
            throw error;
        }
    }

    async getPrices(forceUpdate = false) {
        if (forceUpdate || !this.cachedPrices || Date.now() - this.pricesLastUpdate > this.cacheTimeout) {
            try {
                const response = await fetch(`${this.API_URL}/precos`, {
                    headers: {
                        'Authorization': `Bearer ${await tokenService.getToken()}`
                    }
                });
                
                if (!response.ok) throw new Error('Erro ao buscar preços');
                
                this.cachedPrices = await response.json();
                this.pricesLastUpdate = Date.now();
            } catch (error) {
                console.error('Erro ao buscar preços:', error);
                throw new Error('Não foi possível carregar os preços das consultas');
            }
        }
        return this.cachedPrices;
    }

    async getEndpointCost(endpoint) {
        const prices = await this.getPrices();
        const endpointMap = {
            '/consulta/cpf': 'cpf',
            '/consulta/cnpj': 'cnpj',
            '/consulta/telefone': 'telefone',
            '/consulta/nome': 'nome'
        };
        
        const tipo = endpointMap[endpoint];
        return prices[tipo] || 0;
    }

    async getPrecosConsulta() {
        const prices = await this.getPrices();
        return prices;
    }

    async getPrecoConsulta(tipo) {
        const prices = await this.getPrecosConsulta();
        return prices[tipo] || 0;
    }
}

export const coinsService = new CoinsService(); 