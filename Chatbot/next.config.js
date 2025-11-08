/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  env: {
    NEXT_PUBLIC_DRONE_API_URL: (process.env.DRONE_API_URL || 'http://localhost:8000').replace(/^["']|["']$/g, ''),
  },
}

module.exports = nextConfig

