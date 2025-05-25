import { tokenService } from './token.service.js';
import API_CONFIG from '../config.js';

class ApiService {
    constructor() {
        this.baseUrl = API_CONFIG.BASE_URL;
        this.initialized = false;
    }

    async initialize() {
        if (this.initialized) return;
        
        try {
            const response = await fetch(`${this.baseUrl}/health`);
            if (!response.ok) {
                throw new Error('API não está respondendo');
            }
            this.initialized = true;
            console.log('API Service inicializado com sucesso');
        } catch (error) {
            console.error('Erro ao inicializar API Service:', error);
            throw error;
        }
    }

    async request(endpoint, options = {}) {
        await this.initialize();

        const token = tokenService.getToken();
        const headers = {
            'Content-Type': 'application/json',
            ...(token && { 'Authorization': `Bearer ${token}` }),
            ...options.headers
        };

        try {
            const response = await fetch(`${this.baseUrl}${endpoint}`, {
                ...options,
                headers
            });

            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.message || 'Erro na requisição');
            }

            return await response.json();
        } catch (error) {
            console.error('Erro na requisição:', error);
            throw error;
        }
    }

    async get(endpoint) {
        return this.request(endpoint);
    }

    async post(endpoint, data) {
        return this.request(endpoint, {
            method: 'POST',
            body: JSON.stringify(data)
        });
    }

    async put(endpoint, data) {
        return this.request(endpoint, {
            method: 'PUT',
            body: JSON.stringify(data)
        });
    }

    async delete(endpoint) {
        return this.request(endpoint, {
            method: 'DELETE'
        });
    }
}

export const apiService = new ApiService(); 