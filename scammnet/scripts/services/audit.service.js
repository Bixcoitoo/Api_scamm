import { collection, addDoc, serverTimestamp } from 'firebase/firestore';
import { db, auth } from '../firebase-config.js';

class AuditService {
    async logAction(action, details) {
        try {
            const user = auth.currentUser;
            if (!user) return;

            const logEntry = {
                userId: user.uid,
                action,
                details,
                timestamp: serverTimestamp(),
                userAgent: navigator.userAgent,
                ip: await this.getClientIP()
            };

            await addDoc(collection(db, 'audit_logs'), logEntry);
        } catch (error) {
            console.error('Erro ao registrar log:', error);
        }
    }

    async getClientIP() {
        try {
            const response = await fetch('https://api.ipify.org?format=json');
            const data = await response.json();
            return data.ip;
        } catch {
            return 'unknown';
        }
    }
}

export const auditService = new AuditService(); 