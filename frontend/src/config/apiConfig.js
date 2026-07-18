export function resolveApiBaseUrl(configuredUrl, isDevelopment) {
  const value = configuredUrl?.trim();
  if (value) return value.replace(/\/$/, "");
  if (isDevelopment) return "http://127.0.0.1:8000";
  throw new Error("VITE_API_BASE_URL is required for non-development builds.");
}

export const API_BASE_URL = resolveApiBaseUrl(import.meta.env.VITE_API_BASE_URL, import.meta.env.DEV || import.meta.env.MODE === "test");
