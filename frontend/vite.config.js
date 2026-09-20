import { defineConfig, loadEnv } from "vite";
import { fileURLToPath } from "node:url";
import { resolveApiBaseUrl } from "./src/config/resolveApiBaseUrl.js";
import react from "@vitejs/plugin-react";

export default defineConfig(({ command, mode }) => {
  const env = loadEnv(mode, fileURLToPath(new URL(".", import.meta.url)), "VITE_");
  if (command === "build") resolveApiBaseUrl(env.VITE_API_BASE_URL, false);
  return {
    plugins: [react()],
    test: {
      environment: "jsdom",
      setupFiles: "./src/test/setup.js",
    },
  };
});
