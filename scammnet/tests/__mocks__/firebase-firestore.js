import { jest } from '@jest/globals';

export const collection = jest.fn();
export const doc = jest.fn();
export const getDoc = jest.fn();
export const updateDoc = jest.fn();
export const writeBatch = jest.fn(() => ({
    commit: jest.fn(),
    update: jest.fn(),
    set: jest.fn()
}));
export const increment = jest.fn(amount => amount); 