import { errorService } from './error.service.js';

class ValidationService {
    constructor() {
        this.errorTypes = {
            INVALID_CPF: 'INVALID_CPF',
            INVALID_PHONE: 'INVALID_PHONE',
            INVALID_NAME: 'INVALID_NAME',
            INVALID_EMAIL: 'INVALID_EMAIL'
        };
    }

    // Validação robusta de CPF
    validateCPF(cpf) {
        try {
            // Remove caracteres não numéricos
            const cpfLimpo = cpf.replace(/\D/g, '');
            
            // Verifica se tem 11 dígitos
            if (cpfLimpo.length !== 11) {
                throw new Error('CPF deve conter 11 dígitos');
            }

            // Verifica se todos os dígitos são iguais
            if (/^(\d)\1{10}$/.test(cpfLimpo)) {
                throw new Error('CPF inválido: todos os dígitos são iguais');
            }

            // Validação do primeiro dígito verificador
            let soma = 0;
            for (let i = 0; i < 9; i++) {
                soma += parseInt(cpfLimpo.charAt(i)) * (10 - i);
            }
            let resto = 11 - (soma % 11);
            let digitoVerificador1 = resto > 9 ? 0 : resto;
            
            if (digitoVerificador1 !== parseInt(cpfLimpo.charAt(9))) {
                throw new Error('CPF inválido: primeiro dígito verificador incorreto');
            }

            // Validação do segundo dígito verificador
            soma = 0;
            for (let i = 0; i < 10; i++) {
                soma += parseInt(cpfLimpo.charAt(i)) * (11 - i);
            }
            resto = 11 - (soma % 11);
            let digitoVerificador2 = resto > 9 ? 0 : resto;
            
            if (digitoVerificador2 !== parseInt(cpfLimpo.charAt(10))) {
                throw new Error('CPF inválido: segundo dígito verificador incorreto');
            }

            return true;
        } catch (error) {
            errorService.logError(error, { 
                type: this.errorTypes.INVALID_CPF,
                value: cpf 
            });
            throw error;
        }
    }

    // Validação robusta de telefone
    validatePhone(phone) {
        try {
            // Remove caracteres não numéricos
            const phoneLimpo = phone.replace(/\D/g, '');
            
            // Verifica se tem entre 10 e 11 dígitos (com DDD)
            if (phoneLimpo.length < 10 || phoneLimpo.length > 11) {
                throw new Error('Telefone deve conter 10 ou 11 dígitos (com DDD)');
            }

            // Verifica se o DDD é válido (entre 11 e 99)
            const ddd = parseInt(phoneLimpo.substring(0, 2));
            if (ddd < 11 || ddd > 99) {
                throw new Error('DDD inválido');
            }

            // Verifica se o número começa com 9 (celular) ou 2-5 (fixo)
            const numero = phoneLimpo.substring(2);
            if (numero.length === 9) {
                if (!numero.startsWith('9')) {
                    throw new Error('Número de celular deve começar com 9');
                }
            } else if (numero.length === 8) {
                const primeiroDigito = parseInt(numero.charAt(0));
                if (primeiroDigito < 2 || primeiroDigito > 5) {
                    throw new Error('Número de telefone fixo inválido');
                }
            }

            return true;
        } catch (error) {
            errorService.logError(error, { 
                type: this.errorTypes.INVALID_PHONE,
                value: phone 
            });
            throw error;
        }
    }

    // Validação de nome completo
    validateName(name) {
        try {
            if (!name || typeof name !== 'string') {
                throw new Error('Nome é obrigatório');
            }

            const nomeLimpo = name.trim();
            
            // Verifica se tem pelo menos duas palavras
            const palavras = nomeLimpo.split(/\s+/);
            if (palavras.length < 2) {
                throw new Error('Digite o nome completo');
            }

            // Verifica se cada palavra tem pelo menos 2 caracteres
            for (const palavra of palavras) {
                if (palavra.length < 2) {
                    throw new Error('Cada parte do nome deve ter pelo menos 2 caracteres');
                }
            }

            // Verifica se contém apenas letras, espaços e caracteres especiais comuns
            if (!/^[a-zA-ZÀ-ÿ\s'-]+$/.test(nomeLimpo)) {
                throw new Error('Nome contém caracteres inválidos');
            }

            return true;
        } catch (error) {
            errorService.logError(error, { 
                type: this.errorTypes.INVALID_NAME,
                value: name 
            });
            throw error;
        }
    }

    // Validação de email
    validateEmail(email) {
        try {
            if (!email || typeof email !== 'string') {
                throw new Error('Email é obrigatório');
            }

            const emailLimpo = email.trim().toLowerCase();
            
            // Regex para validação de email
            const emailRegex = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;
            if (!emailRegex.test(emailLimpo)) {
                throw new Error('Email inválido');
            }

            // Verifica domínios comuns inválidos
            const dominiosInvalidos = ['example.com', 'test.com', 'mail.com'];
            const dominio = emailLimpo.split('@')[1];
            if (dominiosInvalidos.includes(dominio)) {
                throw new Error('Email com domínio inválido');
            }

            return true;
        } catch (error) {
            errorService.logError(error, { 
                type: this.errorTypes.INVALID_EMAIL,
                value: email 
            });
            throw error;
        }
    }

    // Formata CPF
    formatCPF(cpf) {
        const cpfLimpo = cpf.replace(/\D/g, '');
        return cpfLimpo.replace(/(\d{3})(\d{3})(\d{3})(\d{2})/, '$1.$2.$3-$4');
    }

    // Formata telefone
    formatPhone(phone) {
        const phoneLimpo = phone.replace(/\D/g, '');
        if (phoneLimpo.length === 11) {
            return phoneLimpo.replace(/(\d{2})(\d{5})(\d{4})/, '($1) $2-$3');
        }
        return phoneLimpo.replace(/(\d{2})(\d{4})(\d{4})/, '($1) $2-$3');
    }
}

export const validationService = new ValidationService(); 