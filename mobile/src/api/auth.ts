import type { LoginResponse, User } from "@/src/types/auth";
import { clearToken, saveToken } from "@/src/utils/secureTokenStorage";
import { apiRequest } from "./client";

export async function login(email: string, password: string): Promise<User> {
  const response = await apiRequest<LoginResponse>("/api/v1/auth/login", { method: "POST", body: JSON.stringify({ email, password }) });
  await saveToken(response.access_token);
  return response.user;
}

export const register = (payload: { email: string; password: string; full_name?: string; role?: string }) => apiRequest<User>("/api/v1/auth/register", { method: "POST", body: JSON.stringify({ ...payload, role: payload.role || "researcher_demo" }) });
export const getCurrentUser = () => apiRequest<User>("/api/v1/auth/me", {}, true);
export const resendVerification = (email: string) => apiRequest<{ status: string; message: string }>("/api/v1/auth/resend-verification", { method: "POST", body: JSON.stringify({ email }) });
export const requestPasswordReset = (email: string) => apiRequest<{ status: string; message: string }>("/api/v1/auth/forgot-password", { method: "POST", body: JSON.stringify({ email }) });
export const verifyEmail = (token: string) => apiRequest<{ status: string; message: string }>("/api/v1/auth/verify-email", { method: "POST", body: JSON.stringify({ token }) });
export const resetPassword = (token: string, newPassword: string) => apiRequest<{ status: string; message: string }>("/api/v1/auth/reset-password", { method: "POST", body: JSON.stringify({ token, new_password: newPassword }) });
export async function logout(): Promise<void> {
  try { await apiRequest("/api/v1/auth/logout", { method: "POST" }, true); } finally { await clearToken(); }
}
