import { API_BASE_URL, API_TIMEOUT_MS } from "@/src/config/env";
import { clearToken, getToken } from "@/src/utils/secureTokenStorage";
import { friendlyErrorMessage, parseBackendError, type BackendErrorBody } from "@/src/utils/errorParser";
import { publishSessionExpiry } from "@/src/utils/sessionEvents";

export type ApiErrorBody = BackendErrorBody;

export class ApiError extends Error {
  constructor(message: string, public code = "REQUEST_FAILED", public status?: number, public details: string[] = []) {
    super(message);
    this.name = "ApiError";
  }
}

export function parseApiError(body: ApiErrorBody | null, status?: number): ApiError {
  const parsed = parseBackendError(body, status);
  return new ApiError(parsed.message, parsed.code, parsed.status, parsed.details);
}

export { friendlyErrorMessage } from "@/src/utils/errorParser";

export async function handleAuthenticationFailure(error: ApiError): Promise<void> {
  if (error.status !== 401 && error.code !== "INVALID_TOKEN" && error.code !== "TOKEN_EXPIRED") return;
  await clearToken();
  publishSessionExpiry(error.message);
}

export async function apiRequest<T>(path: string, init: RequestInit = {}, authenticated = false): Promise<T> {
  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(), API_TIMEOUT_MS);
  try {
    const token = authenticated ? await getToken() : null;
    const response = await fetch(`${API_BASE_URL}${path}`, {
      ...init,
      signal: controller.signal,
      headers: { Accept: "application/json", ...(init.body ? { "Content-Type": "application/json" } : {}), ...(token ? { Authorization: `Bearer ${token}` } : {}), ...init.headers },
    });
    const body = await response.json().catch(() => null);
    if (!response.ok) {
      const parsed = parseApiError(body, response.status);
      await handleAuthenticationFailure(parsed);
      throw parsed;
    }
    return body as T;
  } catch (error) {
    if (error instanceof ApiError) throw error;
    if ((error as Error).name === "AbortError") throw new ApiError("The request timed out. Check the backend connection and try again.", "TIMEOUT");
    throw new ApiError("Cannot reach Movena. Confirm the backend URL and Wi-Fi connection.", "NETWORK_ERROR");
  } finally {
    clearTimeout(timeout);
  }
}

export function absoluteApiUrl(path?: string | null): string | null {
  if (!path) return null;
  if (/^https?:\/\//i.test(path)) return path;
  return `${API_BASE_URL}${path.startsWith("/") ? path : `/${path}`}`;
}
