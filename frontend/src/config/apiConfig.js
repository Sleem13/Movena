import { resolveApiBaseUrl } from "./resolveApiBaseUrl";
export { resolveApiBaseUrl } from "./resolveApiBaseUrl";

export const API_BASE_URL = resolveApiBaseUrl(import.meta.env.VITE_API_BASE_URL, import.meta.env.DEV || import.meta.env.MODE === "test");
