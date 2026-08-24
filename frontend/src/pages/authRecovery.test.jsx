import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { beforeEach, expect, it, vi } from "vitest";

const api = vi.hoisted(() => ({
  requestPasswordReset: vi.fn(),
  resendVerificationEmail: vi.fn(),
  submitPasswordReset: vi.fn(),
  verifyEmailToken: vi.fn(),
}));
vi.mock("../services/api.js", () => api);

import ForgotPassword from "./ForgotPassword.jsx";
import ResetPassword from "./ResetPassword.jsx";
import VerifyEmail from "./VerifyEmail.jsx";

beforeEach(() => { vi.clearAllMocks(); window.history.replaceState({}, "", "/"); });

it("requests password recovery without exposing account existence", async () => {
  api.requestPasswordReset.mockResolvedValue({ message: "If an eligible account exists, a password reset email has been sent." });
  render(<ForgotPassword />);
  fireEvent.change(screen.getByLabelText("Email address"), { target: { value: "person@example.com" } });
  fireEvent.click(screen.getByRole("button", { name: "Send reset link" }));
  expect(await screen.findByText(/if an eligible account exists/i)).toBeInTheDocument();
  expect(api.requestPasswordReset).toHaveBeenCalledWith("person@example.com");
});

it("shows and hides the new password before submitting a reset token", async () => {
  window.history.replaceState({}, "", "/reset-password?token=secure-reset-token");
  api.submitPasswordReset.mockResolvedValue({ message: "Password updated." });
  render(<ResetPassword />);
  const password = screen.getByLabelText("New password");
  expect(password).toHaveAttribute("type", "password");
  fireEvent.click(screen.getByRole("button", { name: "Show new password" }));
  expect(password).toHaveAttribute("type", "text");
  fireEvent.change(password, { target: { value: "ReplacementPassword123" } });
  fireEvent.click(screen.getByRole("button", { name: "Update password" }));
  expect(await screen.findByText("Password updated.")).toBeInTheDocument();
  expect(api.submitPasswordReset).toHaveBeenCalledWith("secure-reset-token", "ReplacementPassword123");
});

it("consumes an email verification token from the link", async () => {
  window.history.replaceState({}, "", "/verify-email?token=secure-verification-token");
  api.verifyEmailToken.mockResolvedValue({ message: "Email verified." });
  render(<VerifyEmail />);
  await waitFor(() => expect(api.verifyEmailToken).toHaveBeenCalledWith("secure-verification-token"));
  expect(await screen.findByText("Email verified.")).toBeInTheDocument();
});
