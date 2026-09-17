import type { NextConfig } from "next";
import path from "node:path";
const root = path.resolve(process.cwd(), "../..");
const config: NextConfig = {
  logging: { incomingRequests: false },
  poweredByHeader: false,
  reactStrictMode: true,
  turbopack: { root },
  outputFileTracingRoot: root,
};
export default config;
