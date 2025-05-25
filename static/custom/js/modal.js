class ConsultaModal {
    constructor() {
        this.modal = document.getElementById('consultaModal');
        this.form = document.getElementById('consultaForm');
        this.resultado = document.getElementById('resultadoConsulta');
        this.apiKey = localStorage.getItem('api_key');
        
        this.setupEventListeners();
    }
    
    setupEventListeners() {
        this.form.addEventListener('submit', async (e) => {
            e.preventDefault();
            await this.consultarCPF();
        });
    }
    
    async consultarCPF() {
        try {
            const cpf = this.form.querySelector('#cpf').value;
            
            const response = await fetch('/api/consulta', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-API-Key': this.apiKey
                },
                body: JSON.stringify({ cpf })
            });
            
            if (!response.ok) {
                throw new Error('Erro na consulta');
            }
            
            const data = await response.json();
            this.mostrarResultado(data);
            
        } catch (error) {
            console.error('Erro na consulta:', error);
            this.mostrarErro('Erro ao realizar consulta. Tente novamente.');
        }
    }
    
    mostrarResultado(data) {
        this.resultado.innerHTML = `
            <div class="alert alert-success">
                <h4>Dados encontrados:</h4>
                <pre>${JSON.stringify(data, null, 2)}</pre>
            </div>
        `;
    }
    
    mostrarErro(mensagem) {
        this.resultado.innerHTML = `
            <div class="alert alert-danger">
                ${mensagem}
            </div>
        `;
    }
    
    abrir() {
        this.modal.style.display = 'block';
    }
    
    fechar() {
        this.modal.style.display = 'none';
        this.form.reset();
        this.resultado.innerHTML = '';
    }
}

// Inicializa o modal quando o documento estiver pronto
document.addEventListener('DOMContentLoaded', () => {
    window.consultaModal = new ConsultaModal();
}); 