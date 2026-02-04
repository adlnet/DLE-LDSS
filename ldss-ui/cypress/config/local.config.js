module.exports = {
  e2e: {
    baseUrl: 'http://localhost:3000',
  },
  env: {
    JWT_SECRET: process.env.JWT_SECRET || 'dummy_local_secret',
  },
  defaultCommandTimeout: 9000
};