// Importa configurações do arquivo de configuração
import { firebaseConfig as firebaseConfigFile } from './config.firebase.js';

// Configuração do Firebase
export const firebaseConfig = firebaseConfigFile;

// Configurações públicas da API
const API_BASE_URL = 'https://api.magalha.space/api';

// Configurações padrão (fallback)
const defaultConfig = {
    api: {
        status: 'unknown',
        maintenance: false,
        features: {
            cpf: { enabled: true, price: 25 },
            telefone: { enabled: true, price: 25 },
            nome: { enabled: true, price: 25 }
        }
    }
};

// Endpoints da API
const API_ENDPOINTS = {
    AUTH: '/auth',
    CONSULTA: '/consulta',
    USER: '/user',
    COINS: '/coins',
    CONFIG: '/config',
    STATUS: '/status',
    HEALTH: '/status/health'
};

// Função para carregar configurações da API
async function loadApiConfig() {
    try {
        const response = await fetch(`${API_BASE_URL}${API_ENDPOINTS.CONFIG}`);
        if (!response.ok) throw new Error('Falha ao carregar configurações');
        return await response.json();
    } catch (error) {
        console.error('Erro ao carregar configurações:', error);
        return defaultConfig;
    }
}

// Função para verificar status da API
async function checkApiStatus() {
    try {
        const response = await fetch(`${API_BASE_URL}${API_ENDPOINTS.HEALTH}`);
        if (!response.ok) throw new Error('Falha ao verificar status');
        return await response.json();
    } catch (error) {
        console.error('Erro ao verificar status:', error);
        return {
            status: 'offline',
            services: {
                database: false,
                firebase: false,
                elasticsearch: false
            }
        };
    }
}

// Exporta as configurações e funções
export {
    API_BASE_URL,
    API_ENDPOINTS,
    defaultConfig,
    loadApiConfig,
    checkApiStatus
};

// Configuração da API
export const apiConfig = {
    baseUrl: 'https://api.magalha.space/api',
    endpoints: {
        auth: '/auth',
        consulta: '/consulta',
        user: '/user',
        coins: '/coins',
        config: '/config',
        health: '/status/health'
    }
};

const API_CONFIG = {
    BASE_URL: 'https://api.magalha.space/api',
    API_KEY: 'scammnet-api-key-2024', // Chave da API para autenticação
    ENDPOINTS: {
        AUTH: '/auth',
        CONSULTA: '/consulta',
        USER: '/user',
        COINS: '/coins',
        HEALTH: '/status/health'
    }
};

export default API_CONFIG; 