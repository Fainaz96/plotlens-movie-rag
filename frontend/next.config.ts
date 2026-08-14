import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  poweredByHeader: false,
  async rewrites() {
    return [
      {
        source: "/backend/:path*",
        destination: `${process.env.API_PROXY_TARGET ?? "http://127.0.0.1:8100"}/:path*`,
      },
    ];
  },
};

export default nextConfig;
