"use client";
import { useState, type FormEvent } from "react";
import { ArrowRight, Activity } from "lucide-react";
import { usePreferences } from "../../components/Preferences";
import { api } from "../../lib/api";
import Link from "next/link";
export default function Login() {
  const { t, locale, setLocale } = usePreferences();
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const [recover, setRecover] = useState(false);
  const [sent, setSent] = useState(false);
  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setBusy(true);
    setError("");
    const data = new FormData(event.currentTarget);
    try {
      await api(recover ? "auth/forgot-password" : "auth/login", {
        method: "POST",
        body: JSON.stringify({
          email: data.get("email"),
          ...(!recover ? { password: data.get("password") } : {}),
        }),
      });
      if (recover) setSent(true);
      else window.location.assign("/workspace");
    } catch (e) {
      setError(e instanceof Error ? e.message : t("offline"));
    } finally {
      setBusy(false);
    }
  }
  return (
    <main className="login-layout">
      <section className="login-story">
        <a className="wordmark" href="/">
          Movena
          <span className="brand-dot" />
        </a>
        <div>
          <div className="motion-icon">
            <Activity size={54} />
          </div>
          <h1>{t("welcome")}</h1>
          <p>{t("todayIntro")}</p>
        </div>
        <p className="fine-print">{t("analysisDisclaimer")}</p>
      </section>
      <section className="login-form">
        <button
          className="language-toggle"
          onClick={() => setLocale(locale === "en" ? "ar" : "en")}
        >
          {locale === "en" ? "العربية" : "English"}
        </button>
        <div className="form-wrap">
          <h2>{recover ? t("recover") : t("login")}</h2>
          <p className="muted">{t("noAccount")}</p>
          <form onSubmit={submit}>
            <label>
              {t("email")}
              <input
                name="email"
                required
                autoComplete="username"
                maxLength={254}
              />
            </label>
            {!recover && (
              <label>
                {t("password")}
                <input
                  type="password"
                  name="password"
                  required
                  autoComplete="current-password"
                />
              </label>
            )}
            {error && (
              <p role="alert" className="error">
                {error}
              </p>
            )}
            {sent && <p role="status">{t("sent")}</p>}
            <button className="primary" disabled={busy}>
              {busy ? t("loading") : recover ? t("sendRecovery") : t("login")}
              <ArrowRight size={19} />
            </button>
          </form>
          <button
            className="text-button"
            onClick={() => {
              setRecover(!recover);
              setSent(false);
              setError("");
            }}
          >
            {recover ? t("returnLogin") : t("recover")}
          </button>
          <nav className="account-links">
            <Link href="/register">{t("createAccount")}</Link>
            <Link href="/resend-verification">{t("resendVerification")}</Link>
          </nav>
        </div>
      </section>
    </main>
  );
}
