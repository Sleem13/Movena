import { ArrowRight, Mail } from "lucide-react";
import { useState } from "react";
import { useAuth } from "../context/AuthContext.jsx";
import { Alert, Button, LoadingSpinner } from "../components/common/UI.jsx";
import { useLocale } from "../i18n/LocaleContext.jsx";
import PasswordInput from "../components/auth/PasswordInput.jsx";

export default function Login({ onSuccess, onRegister, onForgotPassword }) {
  const { login } = useAuth();
  const { t } = useLocale();
  const [error, setError] = useState("");
  const [submitting, setSubmitting] = useState(false);

  async function submit(event) {
    event.preventDefault();
    setError("");
    setSubmitting(true);
    const data = new FormData(event.currentTarget);
    try {
      const authenticatedUser = await login(
        data.get("email"),
        data.get("password"),
      );
      onSuccess?.(authenticatedUser);
    } catch (requestError) {
      const errorCode = requestError.response?.data?.error_code;
      if (!requestError.response) setError(t("auth.network"));
      else if (errorCode === "TOKEN_EXPIRED") setError(t("auth.expired"));
      else if (errorCode === "INVALID_CREDENTIALS") setError(t("auth.invalid"));
      else
        setError(requestError.response.data?.message || t("auth.unavailable"));
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <main className="auth-login">
      <section className="auth-form">
        <h1 className="mt-3 text-3xl font-extrabold tracking-tight text-clinical-ink">
          {t("auth.loginTitle")}
        </h1>
        <p className="mt-3 text-sm leading-6 text-slate-600">
          {t("auth.loginDescription")}
        </p>
        {error && (
          <div className="mt-4">
            <Alert>{error}</Alert>
          </div>
        )}
        <form onSubmit={submit} aria-busy={submitting} className="mt-7 grid gap-5">
          <label className="grid gap-2 text-sm font-semibold text-slate-700">
            {t("auth.loginIdentifier")}
            <span className="relative">
              <Mail
                className="pointer-events-none absolute start-3.5 top-1/2 -translate-y-1/2 text-slate-400"
                size={18}
              />
              <input
                name="email"
                type="text"
                autoComplete="username"
                autoCapitalize="none"
                spellCheck={false}
                required
                className="w-full rounded-lg border border-slate-200 bg-white py-3 ps-11 pe-3 text-sm text-clinical-ink placeholder:text-slate-400"
                placeholder={t("auth.loginIdentifier")}
              />
            </span>
          </label>
          <PasswordInput
            label={t("common.password")}
            name="password"
            autoComplete="current-password"
          />
          <div className="-mt-2 flex justify-end">
            <button
              type="button"
              onClick={onForgotPassword}
              className="text-sm font-bold text-clinical-blue hover:text-blue-700 hover:underline"
            >
              {t("auth.forgotPassword")}
            </button>
          </div>
          <Button className="mt-1 w-full" disabled={submitting}>
            {submitting ? <LoadingSpinner label={t("auth.loggingIn")} /> : t("auth.login")}
            {!submitting && <ArrowRight size={17} />}
          </Button>
        </form>
        <p className="mt-5 text-xs leading-5 text-slate-500">{t("auth.warning")}</p>
        <div className="mt-6 border-t border-slate-100 pt-5 text-center text-sm text-slate-500">
          {t("auth.needAccount")}{" "}
          <button
            onClick={onRegister}
            className="font-bold text-clinical-blue hover:text-blue-700"
          >
            {t("auth.createOne")}
          </button>
        </div>
      </section>
    </main>
  );
}
