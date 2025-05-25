import { CoinsService } from '../scripts/services/coins.service.js';
import { userService } from '../scripts/services/user.service.js';

// Define API_URL global
global.API_URL = 'http://localhost:3000';

// Mock do fetch global
global.fetch = jest.fn(() => 
    Promise.resolve({
        ok: true,
        json: () => Promise.resolve({
            dados_basicos: {
                nome: 'João da Silva',
                cpf: '12345678900',
                nascimento: '1990-01-01'
            }
        })
    })
);

// Mock do userService
jest.mock('../scripts/services/user.service.js', () => ({
    userService: {
        getUserProfile: jest.fn().mockResolvedValue({ coins: 100 }),
        createTransaction: jest.fn(),
        getTransactionHistory: jest.fn()
    }
}));

// Mock do firebase-config
jest.mock('../scripts/firebase-config.js', () => {
    const originalModule = jest.requireActual('../__mocks__/firebase-config.js');
    return {
        __esModule: true,
        ...originalModule
    };
});

describe('CoinsService - Testes de Integração', () => {
    let coinsService;

    beforeEach(() => {
        coinsService = new CoinsService();
        jest.clearAllMocks();
    });

    test('deve consultar CPF em tempo real', async () => {
        const result = await coinsService.processConsultaRequest('/consulta/cpf/12345678900', {
            cpf: '12345678900'
        });

        expect(result.dados_basicos).toBeDefined();
        expect(result.dados_basicos.nome).toBeDefined();
        expect(result.dados_basicos.cpf).toBeDefined();
    }, 30000);
}); 