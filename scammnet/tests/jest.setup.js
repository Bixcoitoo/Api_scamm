import '@testing-library/jest-dom';

// Mock do fetch global
global.fetch = jest.fn();

// Mock do CustomEvent
global.CustomEvent = class CustomEvent {
    constructor(event, params) {
        this.event = event;
        this.params = params;
    }
}; 