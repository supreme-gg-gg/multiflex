/** @type {import('next').NextConfig} */
const nextConfig = {
  output: "export",
  trailingSlash: true,
  images: {
    unoptimized: true,
  },
  env: {
    NEXT_PUBLIC_API_URL:
      process.env.NEXT_PUBLIC_API_URL || process.env.NODE_ENV === "production"
        ? "https://ui-agent-backend-106594148836.us-central1.run.app"
        : "http://localhost:8000",
  },
};

module.exports = nextConfig;
