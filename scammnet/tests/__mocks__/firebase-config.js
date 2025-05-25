import { jest } from '@jest/globals';

const firebaseConfig = {
    apiKey: process.env.TEST_FIREBASE_API_KEY || 'test-api-key',
    authDomain: process.env.TEST_FIREBASE_AUTH_DOMAIN || 'test-domain',
    projectId: process.env.TEST_FIREBASE_PROJECT_ID || 'test-project'
};

const auth = {
    currentUser: {
        uid: 'test-user-id',
        getIdToken: () => Promise.resolve(process.env.TEST_API_KEY || 'test-token')
    }
};

const db = {
    collection: jest.fn(),
    doc: jest.fn(),
    getDoc: jest.fn(),
    updateDoc: jest.fn(),
    writeBatch: jest.fn(() => ({
        commit: jest.fn(),
        update: jest.fn(),
        set: jest.fn()
    }))
};

export { 
    firebaseConfig,
    auth,
    db
};

export const initializeApp = jest.fn(() => ({
    name: '[DEFAULT]',
    options: firebaseConfig
}));

export const getAuth = jest.fn(() => auth);
export const getFirestore = jest.fn(() => db);

// Mock das funções do Firestore
export const collection = jest.fn();
export const doc = jest.fn();
export const getDoc = jest.fn();
export const updateDoc = jest.fn();
export const writeBatch = jest.fn(() => ({
    update: jest.fn(),
    set: jest.fn(),
    commit: jest.fn()
}));
export const increment = jest.fn(amount => amount);
export const serverTimestamp = jest.fn(() => new Date()); 