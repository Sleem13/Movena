"use client";
import { useEffect, useRef, useState, type FormEvent } from "react";
import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { usePreferences } from "../Preferences";
import { api, ApiError } from "../../lib/api";
import { accountToken, validPassword } from "../../lib/account.mjs";

type Mode =
  | "register"
  | "verify-email"
  | "resend-verification"
  | "forgot-password"
  | "reset-password";
const titles = {
  register: "createAccount",
  "verify-email": "verifyEmail",
  "resend-verification": "resendVerification",
  "forgot-password": "recover",
  "reset-password": "resetPassword",
} as const;
export function AccountFlow({ mode }: { mode: Mode }) {
  const { t, locale, setLocale } = usePreferences();
  const router = useRouter(),
    pathname = usePathname();
  const [token, setToken] = useState(""),
    [ready, setReady] = useState(false),
    [busy, setBusy] = useState(false),
    [error, setError] = useState(""),
    [notice, setNotice] = useState("");
  const requiresToken = mode === "verify-email" || mode === "reset-password";
  const capturedToken = useRef(false);
  useEffect(() => {
    if (requiresToken && !capturedToken.current) {
      capturedToken.current = true;
      setToken(accountToken(window.location.search, window.location.hash));
      router.replace(pathname, { scroll: false });
    }
    setReady(true);
  }, [requiresToken, router, pathname]);
  const passwordMode = mode === "register" || mode === "reset-password";
  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (busy) return;
    const form = event.currentTarget,
      data = new FormData(form),
      password = String(data.get("password") ?? "");
    if (
      passwordMode &&
      (!validPassword(password) || password !== data.get("confirm"))
    ) {
      setError(
        t(
          password !== data.get("confirm")
            ? "passwordMismatch"
            : "passwordRules",
        ),
      );
      return;
    }
    const body =
      mode === "register"
        ? {
            username: String(data.get("username")).trim(),
            full_name: String(data.get("full_name")).trim(),
            email: String(data.get("email")).trim(),
            password,
            role: "patient",
            accepted_terms: data.get("terms") === "on",
            accepted_privacy: data.get("privacy") === "on",
          }
        : mode === "reset-password"
          ? { token, new_password: password }
          : mode === "verify-email"
            ? { token }
            : { email: String(data.get("email")).trim() };
    setBusy(true);
    setError("");
    try {
      const result = await api<{ is_verified?: boolean }>(`auth/${mode}`, {
        method: "POST",
        body: JSON.stringify(body),
      });
      setNotice(
        t(
          mode === "register"
            ? result.is_verified
              ? "accountCreated"
              : "checkEmail"
            : mode === "reset-password"
              ? "passwordResetDone"
              : mode === "verify-email"
                ? "emailVerified"
                : "sent",
        ),
      );
      setToken("");
      form.reset();
    } catch (e) {
      setError(
        e instanceof ApiError && e.code === "INVALID_OR_EXPIRED_TOKEN"
          ? t("invalidAccountLink")
          : e instanceof ApiError && e.code === "EMAIL_ALREADY_REGISTERED"
            ? t("emailExists")
            : e instanceof ApiError && e.code === "USERNAME_ALREADY_REGISTERED"
              ? t("usernameExists")
              : e instanceof ApiError &&
                  e.code === "EMAIL_DELIVERY_FAILED" &&
                  mode === "register"
                ? t("accountDeliveryFailed")
                : t("accountError"),
      );
    } finally {
      setBusy(false);
    }
  }
  return (
    <main className="login-layout">
      <section className="login-story">
        <Link href="/" className="wordmark">
          Movena
          <span className="brand-dot" />
        </Link>
        <div>
          <h1>{t("welcome")}</h1>
          <p>{t("todayIntro")}</p>
        </div>
      </section>
      <section className="login-form">
        <button
          className="language-toggle"
          onClick={() => setLocale(locale === "en" ? "ar" : "en")}
        >
          {locale === "en" ? "العربية" : "English"}
        </button>
        <div className="form-wrap">
          <h1>{t(titles[mode])}</h1>
          {notice ? (
            <p role="status">{notice}</p>
          ) : !ready ? (
            <p role="status">{t("loading")}</p>
          ) : requiresToken && !token ? (
            <p role="alert">{t("invalidAccountLink")}</p>
          ) : (
            <form onSubmit={submit}>
              <fieldset disabled={busy}>
                {mode === "register" && (
                  <>
                    <label>
                      {t("fullName")}
                      <input
                        name="full_name"
                        autoComplete="name"
                        required
                        maxLength={120}
                      />
                    </label>
                    <label>
                      {t("username")}
                      <input
                        name="username"
                        autoComplete="username"
                        required
                        minLength={3}
                        maxLength={64}
                        pattern="[\p{L}\p{N}._\-]+"
                      />
                    </label>
                  </>
                )}
                {!requiresToken && (
                  <label>
                    {t("emailAddress")}
                    <input
                      name="email"
                      type="email"
                      autoComplete="email"
                      required
                      maxLength={254}
                    />
                  </label>
                )}
                {passwordMode && (
                  <>
                    <p className="fine-print">{t("passwordRules")}</p>
                    <label>
                      {t("newPassword")}
                      <input
                        name="password"
                        type="password"
                        autoComplete="new-password"
                        required
                        minLength={8}
                        maxLength={128}
                      />
                    </label>
                    <label>
                      {t("confirmPassword")}
                      <input
                        name="confirm"
                        type="password"
                        autoComplete="new-password"
                        required
                        minLength={8}
                        maxLength={128}
                      />
                    </label>
                  </>
                )}
                {mode === "register" && (
                  <>
                    <label className="check-label">
                      <input type="checkbox" name="terms" required />
                      {t("acceptTerms")}
                    </label>
                    <label className="check-label">
                      <input type="checkbox" name="privacy" required />
                      {t("acceptPrivacy")}
                    </label>
                  </>
                )}
                {error && (
                  <p role="alert" className="error">
                    {error}
                  </p>
                )}
                <button className="primary" disabled={busy}>
                  {t(busy ? "loading" : titles[mode])}
                </button>
              </fieldset>
            </form>
          )}
          <nav className="account-links" aria-label={t("account")}>
            <Link href="/login">{t("returnLogin")}</Link>
            {mode !== "resend-verification" && (
              <Link href="/resend-verification">{t("resendVerification")}</Link>
            )}
            {mode === "reset-password" && (
              <Link href="/forgot-password">{t("sendRecovery")}</Link>
            )}
          </nav>
        </div>
      </section>
    </main>
  );
}
