class MaskService {
    constructor() {
        this.maskPatterns = {
            cpf: '***.***.***-**',
            cnpj: '**.***.***/****-**',
            telefone: '(**) *****-****',
            email: '***@***.***',
            nome: '*** ***',
            endereco: '***, *** - ***',
            rg: '**.***.***-*',
            dataNascimento: '**/**/****',
            pis: '***.***.***-*',
            tituloEleitor: '**** **** ****',
            score: '***'
        };
    }

    // Mascara CPF mantendo apenas os últimos 4 dígitos
    maskCPF(cpf) {
        if (!cpf) return '';
        const cpfLimpo = cpf.replace(/\D/g, '');
        return `${this.maskPatterns.cpf.slice(0, -4)}${cpfLimpo.slice(-4)}`;
    }

    // Mascara CNPJ mantendo apenas os últimos 4 dígitos
    maskCNPJ(cnpj) {
        if (!cnpj) return '';
        const cnpjLimpo = cnpj.replace(/\D/g, '');
        return `${this.maskPatterns.cnpj.slice(0, -4)}${cnpjLimpo.slice(-4)}`;
    }

    // Mascara telefone mantendo apenas os últimos 4 dígitos
    maskPhone(phone) {
        if (!phone) return '';
        const phoneLimpo = phone.replace(/\D/g, '');
        return `${this.maskPatterns.telefone.slice(0, -4)}${phoneLimpo.slice(-4)}`;
    }

    // Mascara email mantendo apenas o domínio
    maskEmail(email) {
        if (!email) return '';
        const [local, domain] = email.split('@');
        return `${'*'.repeat(local.length)}@${domain}`;
    }

    // Mascara nome mantendo apenas a primeira letra de cada nome
    maskName(name) {
        if (!name) return '';
        return name.split(' ').map(word => 
            word.charAt(0) + '*'.repeat(word.length - 1)
        ).join(' ');
    }

    // Mascara endereço mantendo apenas a primeira letra de cada palavra
    maskAddress(address) {
        if (!address) return '';
        return address.split(' ').map(word => 
            word.charAt(0) + '*'.repeat(word.length - 1)
        ).join(' ');
    }

    // Mascara RG mantendo apenas os últimos 2 dígitos
    maskRG(rg) {
        if (!rg) return '';
        const rgLimpo = rg.replace(/\D/g, '');
        return `${this.maskPatterns.rg.slice(0, -2)}${rgLimpo.slice(-2)}`;
    }

    // Mascara data de nascimento mantendo apenas o ano
    maskBirthDate(date) {
        if (!date) return '';
        const [day, month, year] = date.split('/');
        return `**/**/${year}`;
    }

    // Mascara PIS mantendo apenas os últimos 2 dígitos
    maskPIS(pis) {
        if (!pis) return '';
        const pisLimpo = pis.replace(/\D/g, '');
        return `${this.maskPatterns.pis.slice(0, -2)}${pisLimpo.slice(-2)}`;
    }

    // Mascara título de eleitor mantendo apenas os últimos 4 dígitos
    maskVoterId(voterId) {
        if (!voterId) return '';
        const voterIdLimpo = voterId.replace(/\D/g, '');
        return `${this.maskPatterns.tituloEleitor.slice(0, -4)}${voterIdLimpo.slice(-4)}`;
    }

    // Mascara score mantendo apenas o primeiro dígito
    maskScore(score) {
        if (!score) return '';
        return `${score.toString().charAt(0)}**`;
    }

    // Mascara dados completos de uma pessoa
    maskPersonData(data) {
        if (!data) return {};

        return {
            dados_basicos: {
                nome: this.maskName(data.dados_basicos?.nome),
                cpf: this.maskCPF(data.dados_basicos?.cpf),
                nascimento: this.maskBirthDate(data.dados_basicos?.nascimento),
                sexo: data.dados_basicos?.sexo,
                nome_mae: this.maskName(data.dados_basicos?.nome_mae),
                nome_pai: this.maskName(data.dados_basicos?.nome_pai)
            },
            contatos: {
                telefone: this.maskPhone(data.contatos?.telefone),
                email: this.maskEmail(data.contatos?.email)
            },
            enderecos: data.enderecos?.map(endereco => ({
                ...endereco,
                logradouro: this.maskAddress(endereco.logradouro),
                numero: '***',
                complemento: endereco.complemento ? '***' : null
            })),
            financeiro: {
                score: this.maskScore(data.financeiro?.score),
                irpf: data.financeiro?.irpf ? '***' : null
            },
            profissional: {
                pis: this.maskPIS(data.profissional?.pis),
                profissao: data.profissional?.profissao
            },
            educacao: data.educacao ? '***' : null,
            eleitoral: data.eleitoral ? {
                ...data.eleitoral,
                titulo: this.maskVoterId(data.eleitoral.titulo)
            } : null
        };
    }
}

export const maskService = new MaskService(); 