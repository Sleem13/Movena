export type AuthRequestError = { code?: string; message?: string };

export const MIN_AUTH_PASSWORD_LENGTH = 12;

const EMAIL_PATTERN = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

export function validateRegistrationInput(name: string, email: string, password: string): string | null {
  if (!name.trim()) return "Enter a display name.";
  if (!EMAIL_PATTERN.test(email.trim())) return "Enter a valid email address.";
  if (password.length < MIN_AUTH_PASSWORD_LENGTH) return `Password must be at least ${MIN_AUTH_PASSWORD_LENGTH} characters.`;
  return null;
}

export function validateLoginInput(email: string, password: string): string | null {
  if (!email.trim()) return "Enter your username or email address.";
  if (!password) return "Enter your password.";
  return null;
}

export function authRequestErrorMessage(error: AuthRequestError, action: "create" | "login"): string {
  switch (error.code) {
    case "NETWORK_ERROR":
      return "Cannot reach PhysioVision AI. Check the backend address and Wi-Fi connection, then retry.";
    case "TIMEOUT":
      return "The account request timed out. Check your connection and try again.";
    case "SERVER_UNAVAILABLE":
      return "Account services are temporarily unavailable. Please retry shortly.";
    case "INVALID_EMAIL":
      return "Enter a valid email address.";
    case "INVALID_PASSWORD":
    case "PASSWORD_TOO_SHORT":
      return `Password must be at least ${MIN_AUTH_PASSWORD_LENGTH} characters.`;
    case "EMAIL_ALREADY_REGISTERED":
    case "ACCOUNT_EXISTS":
      return "An account with this email already exists.";
    case "INVALID_CREDENTIALS":
      return "The username/email or password is incorrect.";
    case "EMAIL_NOT_VERIFIED":
      return "Verify your email before logging in. You can request a new verification link below.";
    default:
      return action === "create" ? "Account creation failed. Please try again." : "Login failed. Check your account details and try again.";
  }
}
