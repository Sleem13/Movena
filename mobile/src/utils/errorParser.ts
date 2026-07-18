export type BackendErrorBody = {
  status?: string;
  error_code?: string;
  message?: string;
  detail?: string;
  details?: string[];
};

export type ParsedMobileError = {
  code: string;
  message: string;
  status?: number;
  details: string[];
  shouldClearToken: boolean;
};

const FRIENDLY_MESSAGES: Record<string, string> = {
  FILE_TOO_LARGE: "This video is too large. Choose a shorter recording under 100 MB.",
  UNSUPPORTED_FILE_TYPE: "Choose an MP4, MOV, AVI, MKV, or WEBM video.",
  EMPTY_FILE: "The selected video is empty. Choose another recording.",
  INVALID_FILENAME: "The video filename is invalid. Rename the file and try again.",
  AUTH_REQUIRED: "Log in before saving this session.",
  AUTHENTICATION_REQUIRED: "Log in before continuing.",
  INVALID_TOKEN: "Your session has expired. Log in again.",
  TOKEN_EXPIRED: "Your session has expired. Log in again.",
  INSUFFICIENT_ROLE: "Your account does not have access to this action.",
  NETWORK_ERROR: "Cannot reach PhysioVision AI. Check the backend address and Wi-Fi connection, then retry.",
  TIMEOUT: "The request timed out. Try a shorter recording and check your connection.",
  SERVER_UNAVAILABLE: "PhysioVision AI is temporarily unavailable. Please retry shortly.",
  CANCELLED: "Upload cancelled. Your selected video is still available to retry.",
  ARTIFACT_NOT_FOUND: "This temporary report or annotated video has expired. Run the analysis again to create a new artifact.",
  EXERCISE_NOT_FOUND: "This exercise is not available for analysis.",
  EXERCISE_NOT_SUPPORTED: "This exercise is planned and cannot be analyzed yet.",
  PROCESSING_ERROR: "The analysis could not be completed. Retry with a shorter, clearly recorded video.",
  MISSING_FILE: "Select a video before starting analysis.",
};

export const isTokenError = (code?: string) => code === "INVALID_TOKEN" || code === "TOKEN_EXPIRED";

export function friendlyErrorMessage(code?: string, fallback?: string): string {
  if (code?.startsWith("INVALID_") && code.endsWith("_VIDEO")) {
    return "The recording did not contain enough valid movement. Review the camera guidance and try again.";
  }
  return FRIENDLY_MESSAGES[code || ""] || fallback || "The request could not be completed. Please try again.";
}

export function parseBackendError(body: BackendErrorBody | null, status?: number): ParsedMobileError {
  const fallbackCode = status === 401 ? "INVALID_TOKEN" : status && status >= 500 ? "SERVER_UNAVAILABLE" : "REQUEST_FAILED";
  const code = body?.error_code || fallbackCode;
  return {
    code,
    message: friendlyErrorMessage(code, body?.message || body?.detail),
    status,
    details: Array.isArray(body?.details) ? body.details : [],
    shouldClearToken: status === 401 || isTokenError(code),
  };
}
