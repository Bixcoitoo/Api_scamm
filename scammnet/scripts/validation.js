export class FormValidator {
    constructor(formId) {
        this.form = document.getElementById(formId);
        this.toast = new Toast();
        this.setupValidation();
        this.requirements = {
            length: value => value.length >= 8,
            uppercase: value => /[A-Z]/.test(value),
            lowercase: value => /[a-z]/.test(value),
            number: value => /\d/.test(value),
            special: value => /[@$!%*?&]/.test(value)
        };
    }

    setupValidation() {
        // Validação em tempo real dos campos
        this.form.querySelectorAll('input').forEach(input => {
            input.addEventListener('input', () => this.validateField(input));
            input.addEventListener('blur', () => this.validateField(input));
        });

        // Validação especial para senha
        const passwordInput = this.form.querySelector('#password');
        if (passwordInput) {
            passwordInput.addEventListener('input', () => this.validatePassword(passwordInput));
        }

        // Validação do formulário no envio
        this.form.addEventListener('submit', (e) => this.handleSubmit(e));
    }

    validateField(input) {
        const requirements = input.nextElementSibling;
        let isValid = true;

        switch (input.type) {
            case 'email':
                isValid = this.validateEmail(input.value);
                break;
            case 'password':
                if (input.id === 'confirmPassword') {
                    const password = this.form.querySelector('#password').value;
                    isValid = input.value === password;
                }
                break;
            default:
                isValid = input.checkValidity();
        }

        this.updateFieldStatus(input, isValid);
        return isValid;
    }

    validateEmail(email) {
        const regex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return regex.test(email);
    }

    validatePassword(input) {
        if (!input) return false;
        
        const value = input.value;
        const requirementElements = document.querySelectorAll('.requirement');
        
        if (!requirementElements || requirementElements.length === 0) return false;
        
        let allValid = true;
        
        requirementElements.forEach(element => {
            const requirement = element.dataset.requirement;
            if (requirement && this.requirements[requirement]) {
                const isValid = this.requirements[requirement](value);
                element.classList.toggle('met', isValid);
                const icon = element.querySelector('i');
                if (icon) {
                    icon.className = isValid ? 'fas fa-check-circle' : 'far fa-circle';
                }
                if (!isValid) allValid = false;
            }
        });

        return allValid;
    }

    updateFieldStatus(input, isValid) {
        input.classList.toggle('valid', isValid);
        input.classList.toggle('invalid', !isValid);
    }

    async handleSubmit(e) {
        e.preventDefault();
        
        const isValid = Array.from(this.form.elements)
            .filter(el => el.tagName === 'INPUT')
            .every(input => this.validateField(input));

        if (!isValid) {
            this.toast.show('Por favor, corrija os erros no formulário', 'error');
            return false;
        }

        return true;
    }
}

class Toast {
    show(message, type = 'info') {
        const toast = document.createElement('div');
        toast.className = `toast toast-${type}`;
        toast.textContent = message;

        const container = document.querySelector('.toast-container');
        container.appendChild(toast);

        setTimeout(() => {
            toast.classList.add('show');
            setTimeout(() => {
                toast.classList.remove('show');
                setTimeout(() => toast.remove(), 300);
            }, 3000);
        }, 100);
    }
}
