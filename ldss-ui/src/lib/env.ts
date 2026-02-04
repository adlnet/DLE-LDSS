interface Env {
    CCV_BASE_URL: string;
    NODE_ENV: 'development' | 'production' | 'test';
}

export const ENV: Env = {
    CCV_BASE_URL: process.env.CCV_BASE_URL ?? 'https://ccv.ldss.tla.adlnet.gov',
    NODE_ENV: process.env.NODE_ENV ?? 'development',
};
