/** @type {import('next').NextConfig} */

const nextConfig = {
  reactStrictMode: true,
  poweredByHeader: false,
  productionBrowserSourceMaps: false,

  async headers() {
    if (process.env.NODE_ENV === 'development' && process.env.DEV_JWT) {
      return [
        {
          source: '/:path*',
          headers: [
            {
              key: 'authorization',
              value: `Bearer ${process.env.DEV_JWT}`,
            },
          ],
        },
      ];
    }
    return [];
  },
};

module.exports = nextConfig;