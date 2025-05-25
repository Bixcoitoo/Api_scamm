import bcrypt from 'bcrypt';

class Database {
    constructor() {
        this.users = JSON.parse(localStorage.getItem('users') || '[]');
        this.sessions = JSON.parse(localStorage.getItem('sessions') || '[]');
    }

    saveUsers() {
        localStorage.setItem('users', JSON.stringify(this.users));
    }

    saveSessions() {
        localStorage.setItem('sessions', JSON.stringify(this.sessions));
    }

    async createUser(userData) {
        const existingUser = this.users.find(u => u.username === userData.username || u.email === userData.email);
        if (existingUser) {
            throw new Error('Usuário ou email já existe');
        }

        // Hash da senha usando bcrypt
        const hashedPassword = await bcrypt.hash(userData.password, 10);

        const newUser = {
            id: Date.now().toString(),
            username: userData.username,
            email: userData.email,
            password: hashedPassword,
            created_at: new Date().toISOString(),
            last_login: null,
            status: 'active',
            role: 'user'
        };

        this.users.push(newUser);
        this.saveUsers();
        return { ...newUser, password: undefined };
    }

    async validateUser(username, password) {
        const user = this.users.find(u => u.username === username);
        if (!user) {
            throw new Error('Credenciais inválidas');
        }

        // Verifica a senha usando bcrypt
        const isValid = await bcrypt.compare(password, user.password);
        if (!isValid) {
            throw new Error('Credenciais inválidas');
        }

        return { ...user, password: undefined };
    }

    createSession(userId) {
        const session = {
            id: Date.now().toString(),
            userId,
            created_at: new Date().toISOString(),
            expires_at: new Date(Date.now() + 24 * 60 * 60 * 1000).toISOString() // 24 horas
        };

        this.sessions.push(session);
        this.saveSessions();
        return session;
    }
}

const db = new Database();
export default db; 