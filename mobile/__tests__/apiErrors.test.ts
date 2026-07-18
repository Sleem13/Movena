import { friendlyErrorMessage, parseApiError } from "@/src/api/client";
import { parseBackendError } from "@/src/utils/errorParser";

describe("mobile API errors", () => {
  it("translates upload errors", () => expect(friendlyErrorMessage("FILE_TOO_LARGE")).toMatch(/too large/i));
  it("translates invalid movement without a clinical claim", () => expect(friendlyErrorMessage("INVALID_SQUAT_VIDEO")).toMatch(/valid movement/i));
  it("preserves a structured error code", () => expect(parseApiError({ error_code: "EMPTY_FILE", message: "Empty" }, 400).code).toBe("EMPTY_FILE"));
  it.each(["FILE_TOO_LARGE", "UNSUPPORTED_FILE_TYPE", "EMPTY_FILE", "INVALID_FILENAME", "MISSING_FILE", "AUTH_REQUIRED", "INVALID_TOKEN", "TOKEN_EXPIRED", "INSUFFICIENT_ROLE", "NETWORK_ERROR", "TIMEOUT", "SERVER_UNAVAILABLE", "ARTIFACT_NOT_FOUND", "EXERCISE_NOT_FOUND", "EXERCISE_NOT_SUPPORTED", "PROCESSING_ERROR"])("maps %s to a friendly message", (code) => expect(friendlyErrorMessage(code)).not.toMatch(/request could not/i));
  it("explains expired artifacts without exposing a path", () => {
    const message = friendlyErrorMessage("ARTIFACT_NOT_FOUND");
    expect(message).toMatch(/temporary|expired/i);
    expect(message).not.toMatch(/[A-Z]:\\|backend\/artifacts/i);
  });
  it("marks expired tokens for secure removal", () => expect(parseBackendError({ error_code: "TOKEN_EXPIRED" }, 401).shouldClearToken).toBe(true));
  it("treats backend failures as unavailable", () => expect(parseBackendError({ message: "Internal" }, 500).code).toBe("SERVER_UNAVAILABLE"));
});
