export default {
    transform: {
        '^.+\\.js$': 'babel-jest'
    },
    testEnvironment: 'jsdom',
    setupFilesAfterEnv: ['<rootDir>/jest.setup.js'],
    moduleNameMapper: {
        '^firebase/(.*)$': '<rootDir>/__mocks__/firebase-$1.js'
    },
    testPathIgnorePatterns: [
        '/node_modules/',
        '/dist/'
    ],
    collectCoverage: true,
    coverageDirectory: 'coverage',
    coverageReporters: ['text', 'lcov'],
    verbose: true
}; 