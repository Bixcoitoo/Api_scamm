import { validationService } from './services/validation.service.js';
import { errorService } from './services/error.service.js';
import { coinsService } from './services/coins.service.js';
import { showNotification } from './utils/notifications.js';
import { auth } from './firebase-config.js';

const API_URL = 'https://api.magalha.space/api';

(async function checarAPI() {
    try {
        const response = await fetch('https://api.magalha.space/', { cache: 'no-store' });
        if (!response.ok) throw new Error('API offline');
        const data = await response.json();
        if (data.status !== 'online') throw new Error('API em manutenção');
    } catch (e) {
        window.location.replace('/pages/manutencao.html');
    }
})();

class ConsultaService {
    constructor() {
        this.initializeEventListeners();
    }

    initializeEventListeners() {
        // Listener para formulário de CPF
        const cpfForm = document.getElementById('cpfForm');
        if (cpfForm) {
            cpfForm.addEventListener('submit', async (e) => {
                e.preventDefault();
                await this.handleCPFConsulta(e.target);
            });
        }

        // Listener para formulário de telefone
        const phoneForm = document.getElementById('phoneForm');
        if (phoneForm) {
            phoneForm.addEventListener('submit', async (e) => {
                e.preventDefault();
                await this.handlePhoneConsulta(e.target);
            });
        }

        // Listener para formulário de nome
        const nameForm = document.getElementById('nameForm');
        if (nameForm) {
            nameForm.addEventListener('submit', async (e) => {
                e.preventDefault();
                await this.handleNameConsulta(e.target);
            });
        }
    }

    async handleCPFConsulta(form) {
        try {
            const cpf = form.querySelector('input[name="cpf"]').value;
            
            // Validação robusta do CPF
            validationService.validateCPF(cpf);
            
            // Formata o CPF para exibição
            const cpfFormatado = validationService.formatCPF(cpf);
            
            // Atualiza o campo com o CPF formatado
            form.querySelector('input[name="cpf"]').value = cpfFormatado;
            
            // Processa a consulta
            const resultado = await coinsService.processConsultaRequest({
                tipo: 'cpf',
                valor: cpf
            });
            
            this.displayResult(resultado);
        } catch (error) {
            errorService.handleError(error, 'Consulta CPF');
            this.displayError(error.message);
        }
    }

    async handlePhoneConsulta(form) {
        try {
            const telefone = form.querySelector('input[name="telefone"]').value;
            
            // Validação robusta do telefone
            validationService.validatePhone(telefone);
            
            // Formata o telefone para exibição
            const telefoneFormatado = validationService.formatPhone(telefone);
            
            // Atualiza o campo com o telefone formatado
            form.querySelector('input[name="telefone"]').value = telefoneFormatado;
            
            // Processa a consulta
            const resultado = await coinsService.processConsultaRequest({
                tipo: 'telefone',
                valor: telefone
            });
            
            this.displayResult(resultado);
        } catch (error) {
            errorService.handleError(error, 'Consulta Telefone');
            this.displayError(error.message);
        }
    }

    async handleNameConsulta(form) {
        try {
            const nome = form.querySelector('input[name="nome"]').value;
            
            // Validação robusta do nome
            validationService.validateName(nome);
            
            // Processa a consulta
            const resultado = await coinsService.processConsultaRequest({
                tipo: 'nome',
                valor: nome
            });
            
            this.displayResult(resultado);
        } catch (error) {
            errorService.handleError(error, 'Consulta Nome');
            this.displayError(error.message);
        }
    }

    displayResult(resultado) {
        const resultContainer = document.getElementById('resultContainer');
        if (!resultContainer) return;

        // Limpa resultados anteriores
        resultContainer.innerHTML = '';

        // Cria elementos para exibir o resultado
        const resultElement = document.createElement('div');
        resultElement.className = 'result-item';
        resultElement.innerHTML = this.formatResult(resultado);
        
        resultContainer.appendChild(resultElement);
    }

    displayError(message) {
        const errorContainer = document.getElementById('errorContainer');
        if (!errorContainer) return;

        errorContainer.textContent = message;
        errorContainer.style.display = 'block';

        // Esconde a mensagem após 5 segundos
        setTimeout(() => {
            errorContainer.style.display = 'none';
        }, 5000);
    }

    formatResult(resultado) {
        // Implementar formatação específica para cada tipo de resultado
        return JSON.stringify(resultado, null, 2);
    }
}

// Inicializa o serviço quando o DOM estiver carregado
document.addEventListener('DOMContentLoaded', () => {
    new ConsultaService();
});

// Função genérica para consultas
async function realizarConsulta(tipo, dados) {
    try {
        // Verifica se tem saldo suficiente
        const custo = CUSTOS_CONSULTA[tipo];
        const saldo = await coinsService.getBalance(true);
        
        if (saldo < custo) {
            showNotification(`Saldo insuficiente. Necessário: ${custo} coins`, 'error');
            return null;
        }

        // Realiza a transação e a consulta
        await coinsService.processTransaction('usage', -custo, {
            tipo: 'consulta',
            dados: tipo
        });

        // Atualiza o display de coins
        document.dispatchEvent(new CustomEvent('updateCoins'));

        // Retorna o resultado da consulta
        return resultado;
    } catch (error) {
        console.error(`Erro na consulta de ${tipo}:`, error);
        showNotification('Erro ao realizar consulta', 'error');
        throw error;
    }
}

// Funções específicas para cada tipo de consulta
export async function consultarCPF(cpf) {
    try {
        const response = await fetch(`${API_URL}/consulta/cpf`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${await auth.currentUser.getIdToken()}`
            },
            body: JSON.stringify({ cpf })
        });

        if (!response.ok) {
            const error = await response.json();
            if (response.status === 402) {
                showNotification('Saldo insuficiente para realizar a consulta', 'error');
                return null;
            }
            throw new Error(error.message);
        }

        const data = await response.json();
        
        // Atualiza o display de coins após consulta bem-sucedida
        await coinsService.getBalance(true);
        document.dispatchEvent(new CustomEvent('updateCoins'));
        
        return data;
    } catch (error) {
        console.error('Erro na consulta de CPF:', error);
        showNotification('Erro ao realizar consulta', 'error');
        throw error;
    }
}

export async function consultarCNPJ(cnpj) {
    try {
        const response = await fetch(`${API_URL}/consulta/cnpj`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${await auth.currentUser.getIdToken()}`
            },
            body: JSON.stringify({ cnpj })
        });

        if (!response.ok) {
            const error = await response.json();
            if (response.status === 402) {
                showNotification('Saldo insuficiente para realizar a consulta', 'error');
                return null;
            }
            throw new Error(error.message);
        }

        const data = await response.json();
        
        // Atualiza o display de coins após consulta bem-sucedida
        await coinsService.getBalance(true);
        document.dispatchEvent(new CustomEvent('updateCoins'));
        
        return data;
    } catch (error) {
        console.error('Erro na consulta de CNPJ:', error);
        showNotification('Erro ao realizar consulta', 'error');
        throw error;
    }
}

export async function consultarTelefone(telefone) {
    return realizarConsulta('telefone', { telefone });
} 
 