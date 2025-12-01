/** @type {import('next').NextConfig} */
const nextConfig = {
  webpack: (config, { isServer }) => {
    // Suppress webpack cache warnings
    if (!isServer) {
      config.cache = {
        ...config.cache,
        buildDependencies: {
          config: [__filename],
        },
      }
    }
    return config
  },
}

module.exports = nextConfig
