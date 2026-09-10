import fs from "node:fs";
import path from "node:path";
import { authRequestErrorMessage, validateRegistrationInput } from "@/src/utils/authValidation";
import { MISSING_VIDEO_MESSAGE } from "@/src/utils/uploadValidation";

const registerSource = fs.readFileSync(path.join(process.cwd(), "app/register.tsx"), "utf8");
const uploadSource = fs.readFileSync(path.join(process.cwd(), "app/upload/[id].tsx"), "utf8");

describe("auth and upload warning isolation", () => {
  it("does not render the missing-video warning on patient registration", () => {
    expect(registerSource).not.toContain(MISSING_VIDEO_MESSAGE);
    expect(registerSource).toContain("authError");
    expect(registerSource).not.toContain("uploadError");
  });

  it("shows account-specific display name, email, and password validation", () => {
    expect(validateRegistrationInput("", "person@example.com", "password")).toMatch(/display name/i);
    expect(validateRegistrationInput("Demo", "not-an-email", "password")).toMatch(/valid email/i);
    expect(validateRegistrationInput("Demo", "person@example.com", "short")).toMatch(/at least 12 characters/i);
    expect(validateRegistrationInput("Demo", "person@example.com", "StrongPassword123")).toBeNull();
  });

  it("keeps the missing-video warning on the Upload screen", () => {
    expect(MISSING_VIDEO_MESSAGE).toBe("Select a video before starting analysis.");
    expect(uploadSource).toContain("setUploadError(MISSING_VIDEO_MESSAGE)");
    expect(uploadSource).toContain("uploadError");
  });

  it("does not leak an upload backend error after returning to patient registration", () => {
    const message = authRequestErrorMessage({ code: "MISSING_FILE", message: MISSING_VIDEO_MESSAGE }, "create");
    expect(message).toMatch(/account creation failed/i);
    expect(message).not.toMatch(/video|analysis/i);
  });
});
