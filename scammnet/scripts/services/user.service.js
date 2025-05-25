import { 
    getFirestore, 
    doc, 
    setDoc, 
    getDoc, 
    updateDoc, 
    arrayUnion, 
    collection, 
    getDocs, 
    writeBatch, 
    increment,
    addDoc,
    query,
    orderBy,
    limit,
    serverTimestamp,
    onSnapshot
} from 'https://www.gstatic.com/firebasejs/10.8.0/firebase-firestore.js';
import { auth } from '../firebase-config.js';
import { db } from '../firebase-config.js';

class UserService {
    constructor() {
        this.currentUser = null;
        this.init();
    }

    async init() {
        await this.waitForAuth();
    }

    async waitForAuth() {
        return new Promise((resolve) => {
            const unsubscribe = auth.onAuthStateChanged((user) => {
                this.currentUser = user;
                unsubscribe();
                resolve();
            });
        });
    }

    async createUserProfile(user, additionalData = {}) {
        if (!user) return;

        const userRef = doc(db, 'usuarios', user.uid);
        const snapshot = await getDoc(userRef);

        if (!snapshot.exists()) {
            const { email, displayName } = user;
            
            try {
                // Cria documento inicial do usuário
                await setDoc(userRef, {
                    username: displayName || additionalData.username || 'Usuário',
                    email: email,
                    created_at: serverTimestamp(),
                    coins: 100,
                    emailVerified: user.emailVerified,
                    lastLogin: serverTimestamp(),
                    ultima_consulta: null,
                    preferences: {}
                });

                // Cria a primeira transação
                const transactionRef = doc(collection(db, 'usuarios', user.uid, 'transacoes'));
                await setDoc(transactionRef, {
                    tipo: 'inicial',
                    valor: 100,
                    data: serverTimestamp(),
                    detalhes: {
                        descricao: 'Bônus de boas-vindas'
                    }
                });

                return userRef;
            } catch (error) {
                console.error('Erro ao criar perfil:', error);
                // Não propaga o erro para permitir que auth.service.js faça o tratamento
                return null;
            }
        }

        return userRef;
    }

    async updateProfile(profileData) {
        const user = auth.currentUser;
        if (!user) {
            console.error('Usuário não autenticado');
            window.location.replace('/pages/404.html');
            return null;
        }

        const updateData = {
            username: profileData.username,
            email: user.email, // Mantém o email sincronizado
            updatedAt: serverTimestamp(),
            coins: profileData.coins || 0,
            preferences: profileData.preferences || {}
        };

        await updateDoc(doc(db, 'usuarios', user.uid), updateData);
    }

    async getTransactionHistory(limitCount = 10) {
        const user = auth.currentUser;
        if (!user) throw new Error('Usuário não autenticado');

        try {
            const transactionsRef = collection(db, 'usuarios', user.uid, 'transacoes');
            const q = query(transactionsRef, orderBy('data', 'desc'), limit(limitCount));
            
            const snapshot = await getDocs(q);
            return snapshot.docs.map(doc => ({
                id: doc.id,
                ...doc.data(),
                timestamp: doc.data().data?.toDate() || new Date()
            }));
        } catch (error) {
            console.error('Erro ao buscar histórico de transações:', error);
            return [];
        }
    }

    async addAchievement(achievementId) {
        const user = auth.currentUser;
        if (!user) {
            console.error('Usuário não autenticado');
            window.location.replace('/pages/404.html');
            return null;
        }

        const userRef = doc(db, 'usuarios', user.uid);
        const achievementRef = doc(db, 'achievements', achievementId);
        
        await updateDoc(userRef, {
            achievements: arrayUnion(achievementId),
            updatedAt: new Date().toISOString()
        });
    }

    async updateNotificationPreferences(preferences) {
        const user = auth.currentUser;
        if (!user) {
            console.error('Usuário não autenticado');
            window.location.replace('/pages/404.html');
            return null;
        }

        await updateDoc(doc(db, 'usuarios', user.uid), {
            notificationPreferences: preferences,
            updatedAt: new Date().toISOString()
        });
    }

    async createTransaction(type, amount, details = {}) {
        const user = auth.currentUser;
        if (!user) throw new Error('Usuário não autenticado');

        const batch = writeBatch(db);
        
        try {
            // Atualiza saldo
            const userRef = doc(db, 'usuarios', user.uid);
            const userDoc = await getDoc(userRef);
            
            if (!userDoc.exists()) {
                throw new Error('Usuário não encontrado');
            }
            
            // Atualiza o saldo
            batch.update(userRef, {
                coins: increment(amount)
            });

            // Cria uma nova transação como subdocumento
            const transactionRef = doc(collection(db, 'usuarios', user.uid, 'transacoes'));
            const transacao = {
                tipo: type,
                valor: amount,
                data: serverTimestamp(),
                detalhes: details
            };

            batch.set(transactionRef, transacao);

            await batch.commit();
        } catch (error) {
            console.error('Erro na transação:', error);
            throw new Error('Erro ao processar transação. Por favor, tente novamente.');
        }
    }

    async checkCoinsBalance(requiredAmount) {
        const user = auth.currentUser;
        if (!user) throw new Error('Usuário não autenticado');

        const userDoc = await getDoc(doc(db, 'usuarios', user.uid));
        if (!userDoc.exists()) throw new Error('Usuário não encontrado');

        const userData = userDoc.data();
        return {
            hasEnough: userData.coins >= requiredAmount,
            current: userData.coins,
            required: requiredAmount
        };
    }

    async initializeUserData(user) {
        const userRef = doc(db, 'usuarios', user.uid);
        
        try {
            const userDoc = await getDoc(userRef);
            
            if (!userDoc.exists()) {
                // Cria documento inicial do usuário com a estrutura esperada pela API
                await setDoc(userRef, {
                    coins: 100,
                    created_at: serverTimestamp(),
                    ultima_consulta: null,
                    transacoes: []
                });
            } else {
                // Atualiza última consulta apenas se o documento já existir
                await updateDoc(userRef, {
                    ultima_consulta: serverTimestamp()
                });
            }
        } catch (error) {
            console.error('Erro ao inicializar dados do usuário:', error);
            throw new Error('Erro ao configurar conta de usuário. Por favor, tente novamente.');
        }
    }

    async getUserProfile() {
        try {
            const user = auth.currentUser;
            if (!user) {
                console.error('Usuário não autenticado');
                return null;
            }

            const userRef = doc(db, 'usuarios', user.uid);
            const userDoc = await getDoc(userRef);

            if (!userDoc.exists()) {
                console.log('Criando perfil do usuário...');
                // Cria o perfil do usuário se não existir
                await this.createUserProfile(user);
                // Busca o perfil novamente
                const newUserDoc = await getDoc(userRef);
                if (!newUserDoc.exists()) {
                    console.error('Erro ao criar perfil do usuário');
                    return null;
                }
                return {
                    ...newUserDoc.data(),
                    uid: user.uid,
                    email: user.email,
                    emailVerified: user.emailVerified
                };
            }

            return {
                ...userDoc.data(),
                uid: user.uid,
                email: user.email,
                emailVerified: user.emailVerified
            };
        } catch (error) {
            console.error('Erro ao obter perfil:', error);
            return null;
        }
    }

    listenUserCoins(callback) {
        const user = auth.currentUser;
        if (!user) {
            console.error('Usuário não autenticado');
            return null;
        }
        const userRef = doc(db, 'usuarios', user.uid);
        return onSnapshot(userRef, (docSnap) => {
            if (docSnap.exists()) {
                const data = docSnap.data();
                callback(data.coins);
            }
        });
    }
}

export const userService = new UserService(); 