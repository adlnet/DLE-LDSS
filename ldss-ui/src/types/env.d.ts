declare namespace NodeJS {
  interface ProcessEnv {
    CCV_BASE_URL: string
    NODE_ENV: 'development' | 'production' | 'test'
  }
}