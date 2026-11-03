module.exports = {
  testEnvironment: 'node',
  transform: {
    '^.+\\.tsx?$': ['ts-jest', { tsconfig: { module: 'CommonJS', moduleResolution: 'Node', noEmit: false } }],
  },
  testMatch: ['**/tests/**/*.test.ts'],
  collectCoverageFrom: ['src/utils/**/*.ts'],
  coverageThreshold: {
    global: { branches: 80, functions: 100, lines: 90, statements: 90 },
  },
}
