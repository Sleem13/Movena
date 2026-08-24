import { ArrowRight, Mail, ShieldAlert, Sparkles } from "lucide-react";
import { useState } from "react";
import { useAuth } from "../context/AuthContext.jsx";
import { Alert, Button, Card } from "../components/common/UI.jsx";
import { useLocale } from "../i18n/LocaleContext.jsx";
import PasswordInput from "../components/auth/PasswordInput.jsx";

export default function Login({ onSuccess, onRegister, onForgotPassword, onVerifyEmail }) {
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
      await login(data.get("email"), data.get("password"));
      onSuccess?.();
    } catch (requestError) {
      const errorCode = requestError.response?.data?.error_code;
      if (!requestError.response) setError(t("auth.network"));
      else if (errorCode === "TOKEN_EXPIRED") setError(t("auth.expired"));
      else if (errorCode === "INVALID_CREDENTIALS") setError(t("auth.invalid"));
      else setError(requestError.response.data?.message || t("auth.unavailable"));
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <main className="mx-auto grid min-h-[680px] w-full max-w-6xl items-center gap-10 px-6 py-12 lg:grid-cols-[.9fr_1.1fr]">
      <section className="hidden rounded-[2rem] bg-gradient-to-br from-clinical-navy to-[#0b716c] p-9 text-white shadow-lift lg:block">
        <span className="grid h-12 w-12 place-items-center rounded-2xl bg-white/15"><Sparkles size={22} /></span>
        <p className="mt-8 text-xs font-bold uppercase tracking-[0.18em] text-teal-200">{t("auth.sideEyebrow")}</p>
        <h1 className="mt-3 text-4xl font-extrabold tracking-tight">{t("auth.sideTitle")}</h1>
        <p className="mt-5 text-sm leading-7 text-blue-100">{t("auth.sideDescription")}</p>
        <div className="mt-10 rounded-2xl border border-white/10 bg-white/10 p-5">
          <div className="flex gap-3">
            <ShieldAlert className="mt-0.5 shrink-0 text-amber-200" size={19} />
            <p className="text-sm leading-6 text-blue-50">{t("auth.sideWarning")}</p>
          </div>
        </div>
      </section>

      <Card className="mx-auto w-full max-w-lg p-6 sm:p-8">
        <p className="text-xs font-bold uppercase tracking-[0.18em] text-clinical-teal">{t("auth.loginEyebrow")}</p>
        <h1 className="mt-3 text-3xl font-extrabold tracking-tight text-clinical-ink">{t("auth.loginTitle")}</h1>
        <p className="mt-3 text-sm leading-6 text-slate-600">{t("auth.loginDescription")}</p>
        <Alert tone="warning" className="mt-6">{t("auth.warning")}</Alert>
        {error && <div className="mt-4"><Alert>{error}</Alert></div>}
        <form onSubmit={submit} className="mt-6 grid gap-5">
          <label className="grid gap-2 text-sm font-semibold text-slate-700">
            {t("auth.loginIdentifier")}
            <span className="relative">
              <Mail className="pointer-events-none absolute left-3.5 top-1/2 -translate-y-1/2 text-slate-400" size={18} />
              <input name="email" type="text" autoComplete="username" required className="w-full rounded-xl border border-slate-200 bg-slate-50 py-3 pl-11 pr-3 text-sm text-clinical-ink placeholder:text-slate-400" placeholder="Username or email" />
            </span>
          </label>
          <PasswordInput label={t("common.password")} name="password" autoComplete="current-password" />
          <div className="-mt-2 flex justify-between gap-3 text-xs font-semibold">
            <button type="button" onClick={onVerifyEmail} className="text-slate-500 hover:text-clinical-blue">{t("auth.resendVerification")}</button>
            <button type="button" onClick={onForgotPassword} className="text-clinical-blue hover:text-blue-700">{t("auth.forgotPassword")}</button>
          </div>
          <Button className="mt-1 w-full" disabled={submitting}>
            {submitting ? t("auth.loggingIn") : t("auth.login")}
            {!submitting && <ArrowRight size={17} />}
          </Button>
        </form>
        <div className="mt-6 border-t border-slate-100 pt-5 text-center text-sm text-slate-500">
          {t("auth.needAccount")}{" "}
          <button onClick={onRegister} className="font-bold text-clinical-blue hover:text-blue-700">{t("auth.createOne")}</button>
        </div>
      </Card>
    </main>
  );
}
