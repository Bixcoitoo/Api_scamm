class ErrorService {
    constructor() {
        this.errorTypes = {
            INSUFFICIENT_COINS: 'INSUFFICIENT_COINS',
            INVALID_TRANSACTION: 'INVALID_TRANSACTION',
            AUTH_ERROR: 'AUTH_ERROR',
            NETWORK_ERROR: 'NETWORK_ERROR'
        };
    }

    handleError(error, context = '') {
        console.error(`[${context}] Erro:`, error);

        // Log para sistema de monitoramento
        this.logError(error, context);

        // Determina o tipo de erro
        const errorType = this.determineErrorType(error);
        
        // Retorna mensagem amigável
        return this.getUserFriendlyMessage(errorType);
    }

    determineErrorType(error) {
        if (error.code === 'permission-denied') return this.errorTypes.AUTH_ERROR;
        if (error.message.includes('coins')) return this.errorTypes.INSUFFICIENT_COINS;
        if (!navigator.onLine) return this.errorTypes.NETWORK_ERROR;
        return 'UNKNOWN_ERROR';
    }

    getUserFriendlyMessage(errorType) {
        const messages = {
            [this.errorTypes.INSUFFICIENT_COINS]: 'Saldo insuficiente para realizar esta operação',
            [this.errorTypes.AUTH_ERROR]: 'Erro de autenticação. Por favor, faça login novamente',
            [this.errorTypes.NETWORK_ERROR]: 'Erro de conexão. Verifique sua internet',
            'UNKNOWN_ERROR': 'Ocorreu um erro inesperado. Tente novamente mais tarde'
        };
        return messages[errorType];
    }

    async logError(error, context) {
        // Implementar sistema de logs
        const logData = {
            timestamp: new Date().toISOString(),
            error: error.message,
            context,
            userId: auth.currentUser?.uid,
            stack: error.stack
        };
        
        // Enviar para sistema de logs (exemplo: Firebase Analytics)
        console.log('Log de erro:', logData);
    }
}

export const errorService = new ErrorService(); 