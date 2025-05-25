class CPFValidator:
    @staticmethod
    def validate(cpf: str) -> bool:
        # Remove caracteres não numéricos
        cpf = ''.join(filter(str.isdigit, cpf))
        
        if len(cpf) != 11:
            return False
            
        # Verifica se todos os dígitos são iguais
        if len(set(cpf)) == 1:
            return False
            
        # Validação do primeiro dígito verificador
        soma = sum(int(cpf[i]) * (10 - i) for i in range(9))
        digito = (soma * 10 % 11) % 10
        if int(cpf[9]) != digito:
            return False
            
        # Validação do segundo dígito verificador
        soma = sum(int(cpf[i]) * (11 - i) for i in range(10))
        digito = (soma * 10 % 11) % 10
        if int(cpf[10]) != digito:
            return False
            
        return True 