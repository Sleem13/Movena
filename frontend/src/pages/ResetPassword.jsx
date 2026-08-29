import { useState } from "react";

import AuthRecoveryLayout from "../components/auth/AuthRecoveryLayout.jsx";
import PasswordInput from "../components/auth/PasswordInput.jsx";
import { getApiErrorMessage } from "../utils/requestErrors.js";
import { Alert, Button } from "../components/common/UI.jsx";
import { submitPasswordReset } from "../services/api.js";

export default function ResetPassword({ onLogin }) {
  const token = new URLSearchParams(window.location.search).get("token") || "";
  const [message, setMessage] = useState("");
  const [error, setError] = useState(
    token ? "" : "This password reset link is missing its token.",
  );
  const [submitting, setSubmitting] = useState(false);
  async function submit(event) {
    event.preventDefault();
    setSubmitting(true);
    setError("");
    const data = new FormData(event.currentTarget);
    try {
      setMessage(
        (await submitPasswordReset(token, data.get("password"))).message,
      );
    } catch (requestError) {
      setError(
        getApiErrorMessage(
          requestError,
          "The reset link is invalid or expired.",
        ),
      );
    } finally {
      setSubmitting(false);
    }
  }
  return (
    <AuthRecoveryLayout onLogin={onLogin}>
      <p className="text-xs font-bold uppercase tracking-[0.18em] text-clinical-teal">
        Secure recovery
      </p>
      <h1 className="mt-3 text-3xl font-extrabold text-clinical-ink">
        Set a new password
      </h1>
      <p className="mt-3 text-sm text-slate-600">
        This link can be used once and expires automatically.
      </p>
      {message ? (
        <Alert tone="info" className="mt-5">
          {message}
        </Alert>
      ) : null}
      {error ? <Alert className="mt-5">{error}</Alert> : null}
      {!message ? (
        <form onSubmit={submit} className="mt-6 grid gap-5">
          <PasswordInput
            label="New password"
            name="password"
            autoComplete="new-password"
            minLength={8}
          />
          <p className="-mt-3 text-xs text-slate-500">
            Use at least 8 characters.
          </p>
          <Button disabled={submitting || !token}>
            {submitting ? "Updating…" : "Update password"}
          </Button>
        </form>
      ) : (
        <Button className="mt-6 w-full" onClick={onLogin}>
          Continue to login
        </Button>
      )}
    </AuthRecoveryLayout>
  );
}
