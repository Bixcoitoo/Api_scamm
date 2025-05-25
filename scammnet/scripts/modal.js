import { auth } from './firebase-config.js';
import { coinsService } from './services/coins.service.js';
import { showNotification } from './utils/notifications.js';
import { maskService } from './services/mask.service.js';
import { errorService } from './services/error.service.js';

document.addEventListener('DOMContentLoaded', function() {
    // Referências das modais
    const modalCPF = document.getElementById('modalCPF');
    const modalTelefone = document.getElementById('modalTelefone');
    const modalNome = document.getElementById('modalNome');

    // Botões de consulta dos cards
    const btnsConsulta = document.querySelectorAll('.consult-btn');
    btnsConsulta.forEach(btn => {
        btn.addEventListener('click', function() {
            const cardTitle = this.parentElement.querySelector('h3').textContent;
            switch(cardTitle) {
                case 'CPF COMPLETO':
                    modalCPF.style.display = 'block';
                    document.body.classList.add('modal-open');
                    break;
                case 'TELEFONE':
                    modalTelefone.style.display = 'block';
                    document.body.classList.add('modal-open');
                    break;
                case 'NOME COMPLETO':
                    modalNome.style.display = 'block';
                    document.body.classList.add('modal-open');
                    break;
            }
        });
    });

    // Fechar modais
    const closeButtons = document.querySelectorAll('.close-modal');
    closeButtons.forEach(btn => {
        btn.addEventListener('click', function() {
            this.closest('.modal').style.display = 'none';
            document.body.classList.remove('modal-open');
        });
    });

    // Fechar modal ao clicar fora
    window.addEventListener('click', function(event) {
        if (event.target.classList.contains('modal')) {
            event.target.style.display = 'none';
            document.body.classList.remove('modal-open');
        }
    });

    // Ajustar posição do modal ao rolar a página
    window.addEventListener('scroll', function() {
        const modals = [modalCPF, modalTelefone, modalNome];
        modals.forEach(modal => {
            if (modal && modal.style.display === 'block') {
                const modalContent = modal.querySelector('.modal-content');
                if (modalContent) {
                    const rect = modalContent.getBoundingClientRect();
                    if (rect.top < 0) {
                        modalContent.style.position = 'relative';
                        modalContent.style.top = window.scrollY + 'px';
                    }
                }
            }
        });
    });

    // Handlers para os botões de pesquisa
    document.getElementById('cpfInput').addEventListener('input', function(e) {
        let value = this.value.replace(/\D/g, '');
        
        // Aplica máscara de CPF
        if (value.length <= 11) {
            value = value.replace(/(\d{3})(\d{3})(\d{3})(\d{2})/, "$1.$2.$3-$4");
        }
        
        this.value = value;
        
        const inputGroup = this.closest('.input-group');
        if (value.replace(/\D/g, '').length > 0 && value.replace(/\D/g, '').length !== 11) {
            inputGroup.classList.add('error');
            this.setCustomValidity('CPF deve conter 11 dígitos');
        } else {
            inputGroup.classList.remove('error');
            this.setCustomValidity('');
        }
    });

    document.getElementById('searchCPF').addEventListener('click', async function() {
        const input = document.getElementById('cpfInput');
        const cpf = input.value.replace(/\D/g, '');
        const inputGroup = input.closest('.input-group');
        const button = this;
        
        if (cpf.length !== 11) {
            inputGroup.classList.add('error');
            showNotification('CPF deve conter 11 dígitos', 'error');
            input.focus();
            return;
        }
        
        try {
            button.disabled = true;
            button.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Consultando...';
            
            await consultarCPF(cpf);
        } catch (error) {
            displayTerminalResult('cpfResult', `> [ERRO] ${error.message}\n> Tente novamente em alguns instantes`);
        } finally {
            button.disabled = false;
            button.innerHTML = '<i class="fas fa-search"></i> Consultar';
        }
    });

    // Máscara para telefone
    document.getElementById('telefoneInput').addEventListener('input', function(e) {
        let value = this.value.replace(/\D/g, '');
        
        // Aplica máscara de telefone (XX) XXXXX-XXXX
        if (value.length <= 11) {
            value = value.replace(/^(\d{2})(\d{5})(\d{4}).*/, "($1) $2-$3");
        }
        
        this.value = value;
        
        const inputGroup = this.closest('.input-group');
        if (value.replace(/\D/g, '').length > 0 && value.replace(/\D/g, '').length !== 11) {
            inputGroup.classList.add('error');
            this.setCustomValidity('Telefone deve conter 11 dígitos');
        } else {
            inputGroup.classList.remove('error');
            this.setCustomValidity('');
        }
    });

    // Validação para nome
    document.getElementById('nomeInput').addEventListener('input', function(e) {
        this.value = this.value.toUpperCase();
        const value = this.value.trim();
        const inputGroup = this.closest('.input-group');
        
        // Validação básica de nome (pelo menos nome e sobrenome)
        if (value && value.split(' ').length < 2) {
            inputGroup.classList.add('error');
            this.setCustomValidity('Digite o nome completo');
        } else {
            inputGroup.classList.remove('error');
            this.setCustomValidity('');
        }
    });

    // Atualizar handler do botão de telefone
    document.getElementById('searchTelefone').addEventListener('click', async function() {
        const input = document.getElementById('telefoneInput');
        const telefone = input.value.replace(/\D/g, '');
        const inputGroup = input.closest('.input-group');
        const button = this;
        
        if (telefone.length !== 11) {
            inputGroup.classList.add('error');
            showNotification('Telefone deve conter 11 dígitos', 'error');
            input.focus();
            return;
        }
        
        try {
            button.disabled = true;
            button.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Consultando...';
            
            const terminal = document.getElementById('telefoneResult');
            if (terminal) {
                typewriterEffect(terminal, '$ > Iniciando consulta...\n$ > Aguarde...', 50);
            }
            
            const response = await coinsService.processConsultaRequest('/consulta/telefone', { telefone });
            const formattedResult = formatConsultaResult(response);
            
            if (terminal) {
                typewriterEffect(terminal, formattedResult, 10);
            }
        } catch (error) {
            const terminal = document.getElementById('telefoneResult');
            if (terminal) {
                let errorMessage;
                if (error.message && error.message.includes('404')) {
                    errorMessage = `$ > [INFO] Telefone não encontrado na base de dados\n$ > Verifique se o número está correto e tente novamente`;
                } else if (error.message && error.message.includes('autenticado')) {
                    errorMessage = `$ > [ERRO] Sessão expirada\n$ > Por favor, faça login novamente`;
                    window.location.href = '/pages/login.html';
                } else if (error.message && error.message.includes('500')) {
                    errorMessage = `$ > [INFO] Sistema em manutenção\n$ > Por favor, tente novamente em alguns minutos`;
                } else if (error.message && error.message.includes('timeout')) {
                    errorMessage = `$ > [INFO] Tempo de resposta excedido\n$ > Por favor, tente novamente em alguns instantes`;
                } else if (error.message && error.message.includes('network')) {
                    errorMessage = `$ > [INFO] Problema de conexão\n$ > Verifique sua internet e tente novamente`;
                } else {
                    errorMessage = `$ > [INFO] Sistema temporariamente indisponível\n$ > Por favor, tente novamente em alguns minutos`;
                }
                typewriterEffect(terminal, errorMessage, 50);
            }
        } finally {
            button.disabled = false;
            button.innerHTML = '<i class="fas fa-search"></i> Consultar';
        }
    });

    // Atualizar handler do botão de nome
    document.getElementById('searchNome').addEventListener('click', async function() {
        const input = document.getElementById('nomeInput');
        const nome = input.value.trim();
        const inputGroup = input.closest('.input-group');
        const button = this;
        
        if (nome.split(' ').length < 2) {
            inputGroup.classList.add('error');
            showNotification('Digite o nome completo', 'error');
            input.focus();
            return;
        }
        
        try {
            button.disabled = true;
            button.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Consultando...';
            
            const terminal = document.getElementById('nomeResult');
            if (terminal) {
                typewriterEffect(terminal, '$ > Iniciando consulta...\n$ > Aguarde...', 50);
            }
            
            const response = await coinsService.processConsultaRequest('/consulta/nome', { nome });
            const formattedResult = formatConsultaResult(response);
            
            if (terminal) {
                typewriterEffect(terminal, formattedResult, 10);
            }
        } catch (error) {
            const terminal = document.getElementById('nomeResult');
            if (terminal) {
                let errorMessage;
                if (error.message && error.message.includes('404')) {
                    errorMessage = `$ > [INFO] Nome não encontrado na base de dados\n$ > Verifique se o nome está correto e tente novamente`;
                } else if (error.message && error.message.includes('autenticado')) {
                    errorMessage = `$ > [ERRO] Sessão expirada\n$ > Por favor, faça login novamente`;
                    window.location.href = '/pages/login.html';
                } else if (error.message && error.message.includes('500')) {
                    errorMessage = `$ > [INFO] Sistema em manutenção\n$ > Por favor, tente novamente em alguns minutos`;
                } else if (error.message && error.message.includes('timeout')) {
                    errorMessage = `$ > [INFO] Tempo de resposta excedido\n$ > Por favor, tente novamente em alguns instantes`;
                } else if (error.message && error.message.includes('network')) {
                    errorMessage = `$ > [INFO] Problema de conexão\n$ > Verifique sua internet e tente novamente`;
                } else {
                    errorMessage = `$ > [INFO] Sistema temporariamente indisponível\n$ > Por favor, tente novamente em alguns minutos`;
                }
                typewriterEffect(terminal, errorMessage, 50);
            }
        } finally {
            button.disabled = false;
            button.innerHTML = '<i class="fas fa-search"></i> Consultar';
        }
    });

    // Adicionar handlers para os botões de cópia
    const copyButtons = document.querySelectorAll('.copy-button');
    
    copyButtons.forEach(button => {
        button.addEventListener('click', async function() {
            const terminal = this.closest('.terminal').querySelector('.terminal-text');
            const textToCopy = terminal.textContent;
            
            try {
                await navigator.clipboard.writeText(textToCopy);
                
                // Feedback visual
                this.classList.add('copied');
                const icon = this.querySelector('i');
                icon.classList.remove('fa-copy');
                icon.classList.add('fa-check');
                
                setTimeout(() => {
                    this.classList.remove('copied');
                    icon.classList.remove('fa-check');
                    icon.classList.add('fa-copy');
                }, 2000);
                
                showNotification('Texto copiado com sucesso!', 'success');
            } catch (err) {
                showNotification('Erro ao copiar texto', 'error');
            }
        });
    });
});

function displayTerminalResult(elementId, data) {
    console.log('Display Terminal Result - Element ID:', elementId);
    console.log('Display Terminal Result - Data:', data);

    const element = document.getElementById(elementId);
    if (!element) {
        console.error('Elemento não encontrado:', elementId);
        return;
    }

    // Limpa o conteúdo anterior
    element.innerHTML = '';

    // Se for uma string, exibe diretamente
    if (typeof data === 'string') {
        element.textContent = data;
        return;
    }

    // Se for um objeto, formata o resultado
    const formattedData = formatConsultaResult(data);
    console.log('Dados formatados:', formattedData);
    element.textContent = formattedData;
}

function typewriterEffect(element, text, speed = 10) {
    let index = 0;
    element.textContent = '';
    
    function type() {
        if (index < text.length) {
            // Se for uma quebra de linha, adiciona um <br>
            if (text[index] === '\n') {
                element.innerHTML += '<br>';
            } else {
                element.innerHTML += text[index];
            }
            index++;
            setTimeout(type, speed);
        }
    }
    
    type();
}

async function consultarCPF(cpf) {
    try {
        const button = document.getElementById('searchCPF');
        button.disabled = true;
        button.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Consultando...';
        
        // Mostra mensagem de carregamento
        const terminal = document.getElementById('cpfResult');
        if (terminal) {
            typewriterEffect(terminal, '$ > Iniciando consulta...\n$ > Aguarde...', 50);
        }
        
        // Limpa o CPF de caracteres especiais
        const cpfLimpo = cpf.replace(/\D/g, '');
        
        if (cpfLimpo.length !== 11) {
            throw new Error('CPF deve conter 11 dígitos');
        }
        
        console.log('Enviando CPF:', cpfLimpo);
        const resultado = await coinsService.processConsultaRequest('/consulta/cpf', { cpf: cpfLimpo });
        
        console.log('Resultado recebido:', resultado);
        
        if (!resultado) {
            throw new Error('Nenhum resultado encontrado');
        }
        
        // Formata e exibe o resultado com efeito de digitação
        const formattedResult = formatConsultaResult(resultado);
        if (terminal) {
            typewriterEffect(terminal, formattedResult, 10);
        }
        
    } catch (error) {
        console.error('Erro na consulta:', error);
        const terminal = document.getElementById('cpfResult');
        if (terminal) {
            let errorMessage;
            if (error.message && error.message.includes('404')) {
                errorMessage = `$ > [INFO] CPF não encontrado na base de dados\n$ > Verifique se o CPF está correto e tente novamente`;
            } else if (error.message && error.message.includes('autenticado')) {
                errorMessage = `$ > [ERRO] Sessão expirada\n$ > Por favor, faça login novamente`;
                window.location.href = '/pages/login.html';
            } else if (error.message && error.message.includes('500')) {
                errorMessage = `$ > [INFO] Sistema em manutenção\n$ > Por favor, tente novamente em alguns minutos`;
            } else if (error.message && error.message.includes('timeout')) {
                errorMessage = `$ > [INFO] Tempo de resposta excedido\n$ > Por favor, tente novamente em alguns instantes`;
            } else if (error.message && error.message.includes('network')) {
                errorMessage = `$ > [INFO] Problema de conexão\n$ > Verifique sua internet e tente novamente`;
            } else {
                errorMessage = `$ > [INFO] Sistema temporariamente indisponível\n$ > Por favor, tente novamente em alguns minutos`;
            }
            typewriterEffect(terminal, errorMessage, 50);
        }
    } finally {
        const button = document.getElementById('searchCPF');
        button.disabled = false;
        button.innerHTML = '<i class="fas fa-search"></i> Consultar';
    }
}

function formatConsultaResult(data) {
    console.log('Formatando resultado:', data);

    if (!data || Object.keys(data).length === 0) {
        return '$ > Nenhum dado encontrado para esta consulta.';
    }

    let formatted = 'Dados encontrados com sucesso!\n\n';
    
    // Dados Básicos
    if (data.dados_basicos) {
        formatted += '$ [+] Informações Pessoais\n';
        formatted += `$ └── Nome: ${data.dados_basicos.nome && data.dados_basicos.nome.trim() !== '' ? data.dados_basicos.nome : 'Não encontrado!'}\n`;
        formatted += `$ └── CPF: ${data.dados_basicos.cpf && data.dados_basicos.cpf.trim() !== '' ? data.dados_basicos.cpf : 'Não encontrado!'}\n`;
        formatted += `$ └── RG: ${data.dados_basicos.rg && data.dados_basicos.rg.trim() !== '' ? data.dados_basicos.rg : 'Não encontrado!'}\n`;
        formatted += `$ └── Nascimento: ${data.dados_basicos.nascimento && data.dados_basicos.nascimento.trim() !== '' ? new Date(data.dados_basicos.nascimento).toLocaleDateString('pt-BR') : 'Não encontrado!'}\n`;
        formatted += `$ └── Sexo: ${data.dados_basicos.sexo && data.dados_basicos.sexo.trim() !== '' ? data.dados_basicos.sexo : 'Não encontrado!'}\n`;
        formatted += `$ └── Situação Cadastral: ${data.dados_basicos.situacao_cadastral && data.dados_basicos.situacao_cadastral.trim() !== '' ? data.dados_basicos.situacao_cadastral : 'Não encontrado!'}\n\n`;
    }

    // Filiação
    if (data.dados_basicos) {
        formatted += '$ [+] Filiação\n';
        formatted += `$ └── Mãe: ${data.dados_basicos.nome_mae && data.dados_basicos.nome_mae.trim() !== '' ? data.dados_basicos.nome_mae : 'Não encontrado!'}\n`;
        formatted += `$ └── Pai: ${data.dados_basicos.nome_pai && data.dados_basicos.nome_pai.trim() !== '' ? data.dados_basicos.nome_pai : 'Não encontrado!'}\n\n`;
    }

    // Contatos
    if (data.contatos) {
        formatted += '$ [+] Contatos\n';
        formatted += `$ └── Emails: ${(Array.isArray(data.contatos.emails) && data.contatos.emails.length > 0) ? data.contatos.emails.join(', ') : 'Não encontrado!'}\n`;
        formatted += `$ └── Telefones: ${(Array.isArray(data.contatos.telefones) && data.contatos.telefones.length > 0) ? data.contatos.telefones.join(', ') : 'Não encontrado!'}\n\n`;
    }

    // Endereços
    if (Array.isArray(data.enderecos) && data.enderecos.length) {
        formatted += '$ [+] Endereços\n';
        data.enderecos.forEach((end, index) => {
            formatted += `$ └── Endereço ${index + 1}:\n`;
            formatted += `$     ├── Logradouro: ${end.logradouro && end.logradouro.trim() !== '' ? end.logradouro : 'Não encontrado!'}\n`;
            formatted += `$     ├── Número: ${end.numero && end.numero.trim() !== '' ? end.numero : 'Não encontrado!'}\n`;
            formatted += `$     ├── Complemento: ${end.complemento && end.complemento.trim() !== '' ? end.complemento : 'Não encontrado!'}\n`;
            formatted += `$     ├── Bairro: ${end.bairro && end.bairro.trim() !== '' ? end.bairro : 'Não encontrado!'}\n`;
            formatted += `$     ├── Cidade: ${end.cidade && end.cidade.trim() !== '' ? end.cidade : 'Não encontrado!'}\n`;
            formatted += `$     ├── UF: ${end.uf && end.uf.trim() !== '' ? end.uf : 'Não encontrado!'}\n`;
            formatted += `$     └── CEP: ${end.cep && end.cep.trim() !== '' ? end.cep : 'Não encontrado!'}\n`;
        });
        formatted += '\n';
    }

    // Financeiro
    if (data.financeiro) {
        formatted += '$ [+] Financeiro\n';
        if (data.financeiro.score) {
            formatted += `$ └── Score CSB8: ${data.financeiro.score.score_csb8 && data.financeiro.score.score_csb8.trim() !== '' ? data.financeiro.score.score_csb8 : 'Não encontrado!'} (Faixa: ${data.financeiro.score.faixa_csb8 && data.financeiro.score.faixa_csb8.trim() !== '' ? data.financeiro.score.faixa_csb8 : 'Não encontrado!'})\n`;
            formatted += `$ └── Score CSBA: ${data.financeiro.score.score_csba && data.financeiro.score.score_csba.trim() !== '' ? data.financeiro.score.score_csba : 'Não encontrado!'} (Faixa: ${data.financeiro.score.faixa_csba && data.financeiro.score.faixa_csba.trim() !== '' ? data.financeiro.score.faixa_csba : 'Não encontrado!'})\n`;
        }
        formatted += `$ └── IRPF: ${data.financeiro.irpf && data.financeiro.irpf.trim() !== '' ? data.financeiro.irpf : 'Não encontrado!'}\n\n`;
    }

    // Profissional
    if (data.profissional) {
        formatted += '$ [+] Profissional\n';
        formatted += `$ └── PIS: ${data.profissional.pis && data.profissional.pis.trim() !== '' ? data.profissional.pis : 'Não encontrado!'}\n`;
        let profissao = 'Não encontrado!';
        if (data.profissional.profissao) {
            if (typeof data.profissional.profissao === 'object') {
                profissao = data.profissional.profissao.descricao && data.profissional.profissao.descricao.trim() !== '' ? data.profissional.profissao.descricao : JSON.stringify(data.profissional.profissao);
            } else if (typeof data.profissional.profissao === 'string' && data.profissional.profissao.trim() !== '') {
                profissao = data.profissional.profissao;
            }
        }
        formatted += `$ └── Profissão: ${profissao}\n`;
        formatted += `$ └── Descrição: ${data.profissional.descricao && data.profissional.descricao.trim() !== '' ? data.profissional.descricao : 'Não encontrado!'}\n`;
        let dataInclusao = 'Não encontrado!';
        if (data.profissional.data_inclusao && data.profissional.data_inclusao.trim() !== '') {
            // Aceitar datas no formato 'YYYY-MM-DD HH:MM:SS'
            let dataStr = data.profissional.data_inclusao.replace(' ', 'T');
            let dataObj = new Date(dataStr);
            if (!isNaN(dataObj.getTime())) {
                dataInclusao = dataObj.toLocaleDateString('pt-BR');
            } else {
                // Se não for possível converter, mostrar o valor bruto
                dataInclusao = data.profissional.data_inclusao;
            }
        }
        formatted += `$ └── Data de Inclusão: ${dataInclusao}\n`;
        formatted += `$ └── Cadastro ID: ${data.profissional.cadastro_id && data.profissional.cadastro_id.trim() !== '' ? data.profissional.cadastro_id : 'Não encontrado!'}\n\n`;
    }

    // Eleitoral
    if (data.eleitoral) {
        formatted += '$ [+] Eleitoral\n';
        formatted += `$ └── Título: ${data.eleitoral.titulo && data.eleitoral.titulo.trim() !== '' ? data.eleitoral.titulo : 'Não encontrado!'}\n`;
        formatted += `$ └── Zona: ${data.eleitoral.zona && data.eleitoral.zona.trim() !== '' ? data.eleitoral.zona : 'Não encontrado!'}\n`;
        formatted += `$ └── Seção: ${data.eleitoral.secao && data.eleitoral.secao.trim() !== '' ? data.eleitoral.secao : 'Não encontrado!'}\n\n`;
    }

    // RGs (caso venha como array)
    if (Array.isArray(data.rgs) && data.rgs.length) {
        formatted += '$ [+] RGs\n';
        data.rgs.forEach((rg, index) => {
            formatted += `$ └── RG ${index + 1}: ${rg && rg.trim() !== '' ? rg : 'Não encontrado!'}\n`;
        });
        formatted += '\n';
    }

    // Outros campos relevantes (adapte conforme o backend)
    if (data.situacao_cadastral) {
        formatted += `$ [+] Situação Cadastral\n$ └── ${data.situacao_cadastral && data.situacao_cadastral.trim() !== '' ? data.situacao_cadastral : 'Não encontrado!'}\n\n`;
    }

    // Remove espaços/quebras de linha extras no início
    formatted = formatted.replace(/^[\s\n]+/g, '');

    // Adiciona o prompt '$ ' no início de cada linha não vazia
    formatted = formatted
        .split('\n')
        .map(line => line.trim() !== '' ? `$ ${line}` : '')
        .join('\n');

    // Se não houver nenhum dado formatado, retorna mensagem de erro
    if (!formatted) {
        console.log('Nenhum dado formatado encontrado no resultado');
        return '$ > Nenhum dado encontrado para esta consulta.';
    }

    // Substituir todas as ocorrências de 'N/A' por 'Não encontrado!'
    formatted = formatted.replace(/N\/A/g, 'Não encontrado!');

    return formatted;
}

function showError(message) {
    const errorDiv = document.createElement('div');
    errorDiv.className = 'error-message';
    errorDiv.innerHTML = `
        <div class="error-content">
            <i class="fas fa-exclamation-circle"></i>
            <p>${message}</p>
            <button onclick="this.parentElement.parentElement.remove()">OK</button>
        </div>
    `;
    document.body.appendChild(errorDiv);
}

class ModalService {
    constructor() {
        this.modal = document.getElementById('resultModal');
        this.modalContent = document.getElementById('modalContent');
        this.closeButton = document.getElementById('closeModal');
        this.initializeEventListeners();
    }

    initializeEventListeners() {
        if (this.closeButton) {
            this.closeButton.addEventListener('click', () => this.closeModal());
        }

        // Fecha o modal ao clicar fora dele
        window.addEventListener('click', (e) => {
            if (e.target === this.modal) {
                this.closeModal();
            }
        });

        // Fecha o modal com a tecla ESC
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && this.modal.style.display === 'block') {
                this.closeModal();
            }
        });
    }

    displayTerminalResult(type, data) {
        try {
            if (!this.modalContent) return;

            // Mascara os dados sensíveis
            const maskedData = this.maskSensitiveData(type, data);
            
            // Formata o resultado para exibição
            const formattedResult = this.formatResult(type, maskedData);
            
            // Atualiza o conteúdo do modal
            this.modalContent.innerHTML = formattedResult;
            
            // Exibe o modal
            this.showModal();
        } catch (error) {
            errorService.handleError(error, 'Modal Display');
            this.displayError('Erro ao exibir resultado');
        }
    }

    maskSensitiveData(type, data) {
        switch (type) {
            case 'cpfResult':
            case 'cnpjResult':
            case 'phoneResult':
            case 'nameResult':
                return maskService.maskPersonData(data);
            default:
                return data;
        }
    }

    formatResult(type, data) {
        try {
            let html = '<div class="result-container">';
            
            switch (type) {
                case 'cpfResult':
                case 'cnpjResult':
                case 'phoneResult':
                case 'nameResult':
                    html += this.formatPersonData(data);
                    break;
                default:
                    html += `<pre>${JSON.stringify(data, null, 2)}</pre>`;
            }
            
            html += '</div>';
            return html;
        } catch (error) {
            errorService.handleError(error, 'Result Formatting');
            return '<div class="error">Erro ao formatar resultado</div>';
        }
    }

    formatPersonData(data) {
        if (!data) return '<div class="error">Nenhum dado encontrado</div>';

        let html = '<div class="person-data">';
        
        // Dados Básicos
        if (data.dados_basicos) {
            html += '<div class="section">';
            html += '<h3>Dados Básicos</h3>';
            html += '<ul>';
            for (const [key, value] of Object.entries(data.dados_basicos)) {
                if (value) {
                    html += `<li><strong>${this.formatKey(key)}:</strong> ${value}</li>`;
                }
            }
            html += '</ul>';
            html += '</div>';
        }

        // Contatos
        if (data.contatos) {
            html += '<div class="section">';
            html += '<h3>Contatos</h3>';
            html += '<ul>';
            for (const [key, value] of Object.entries(data.contatos)) {
                if (value) {
                    html += `<li><strong>${this.formatKey(key)}:</strong> ${value}</li>`;
                }
            }
            html += '</ul>';
            html += '</div>';
        }

        // Endereços
        if (data.enderecos && data.enderecos.length > 0) {
            html += '<div class="section">';
            html += '<h3>Endereços</h3>';
            data.enderecos.forEach((endereco, index) => {
                html += `<div class="address-item">`;
                html += `<h4>Endereço ${index + 1}</h4>`;
                html += '<ul>';
                for (const [key, value] of Object.entries(endereco)) {
                    if (value) {
                        html += `<li><strong>${this.formatKey(key)}:</strong> ${value}</li>`;
                    }
                }
                html += '</ul>';
                html += '</div>';
            });
            html += '</div>';
        }

        // Dados Financeiros
        if (data.financeiro) {
            html += '<div class="section">';
            html += '<h3>Dados Financeiros</h3>';
            html += '<ul>';
            for (const [key, value] of Object.entries(data.financeiro)) {
                if (value) {
                    html += `<li><strong>${this.formatKey(key)}:</strong> ${value}</li>`;
                }
            }
            html += '</ul>';
            html += '</div>';
        }

        // Dados Profissionais
        if (data.profissional) {
            html += '<div class="section">';
            html += '<h3>Dados Profissionais</h3>';
            html += '<ul>';
            for (const [key, value] of Object.entries(data.profissional)) {
                if (value) {
                    html += `<li><strong>${this.formatKey(key)}:</strong> ${value}</li>`;
                }
            }
            html += '</ul>';
            html += '</div>';
        }

        html += '</div>';
        return html;
    }

    formatKey(key) {
        const keyMap = {
            nome: 'Nome',
            cpf: 'CPF',
            nascimento: 'Data de Nascimento',
            sexo: 'Sexo',
            nome_mae: 'Nome da Mãe',
            nome_pai: 'Nome do Pai',
            telefone: 'Telefone',
            email: 'E-mail',
            logradouro: 'Logradouro',
            numero: 'Número',
            complemento: 'Complemento',
            bairro: 'Bairro',
            cidade: 'Cidade',
            estado: 'Estado',
            cep: 'CEP',
            score: 'Score',
            irpf: 'IRPF',
            pis: 'PIS',
            profissao: 'Profissão',
            titulo: 'Título de Eleitor'
        };
        return keyMap[key] || key;
    }

    showModal() {
        if (this.modal) {
            this.modal.style.display = 'block';
            document.body.style.overflow = 'hidden';
        }
    }

    closeModal() {
        if (this.modal) {
            this.modal.style.display = 'none';
            document.body.style.overflow = 'auto';
        }
    }

    displayError(message) {
        if (this.modalContent) {
            this.modalContent.innerHTML = `<div class="error">${message}</div>`;
            this.showModal();
        }
    }
}

export const modalService = new ModalService(); 