import { ArrowLeft, LockKeyhole, Mail, ShieldCheck, UserRound } from "lucide-react";
import { useState } from "react";
import { useAuth } from "../context/AuthContext.jsx";
import { Alert, Badge, Button, Card } from "../components/common/UI.jsx";
import { useLocale } from "../i18n/LocaleContext.jsx";

export default function Register({ onLogin }) {
  const { register } = useAuth();
  const { t } = useLocale();
  const [message, setMessage] = useState("");
  const [success, setSuccess] = useState(false);
  const [submitting, setSubmitting] = useState(false);

  async function submit(event) {
    event.preventDefault();
    setMessage("");
    setSuccess(false);
    setSubmitting(true);
    const data = new FormData(event.currentTarget);
    try {
      await register({
        email: data.get("email"),
        password: data.get("password"),
        full_name: data.get("full_name"),
        role: "researcher_demo",
      });
      setSuccess(true);
      setMessage(t("auth.created"));
    } catch (requestError) {
      setMessage(requestError.response?.data?.message || t("auth.registerFailed"));
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <main className="mx-auto w-full max-w-2xl px-6 py-12">
      <button onClick={onLogin} className="mb-6 inline-flex items-center gap-2 text-sm font-semibold text-slate-500 transition hover:text-clinical-blue">
        <ArrowLeft size={16} />
        {t("auth.backToLogin")}
      </button>
      <Card className="overflow-hidden">
        <div className="border-b border-slate-100 bg-gradient-to-r from-blue-50 to-teal-50 p-6 sm:p-8">
          <Badge tone="teal"><ShieldCheck className="mr-1.5" size={14} />{t("auth.registerBadge")}</Badge>
          <h1 className="mt-4 text-3xl font-extrabold tracking-tight text-clinical-ink">{t("auth.registerTitle")}</h1>
          <p className="mt-3 max-w-xl text-sm leading-6 text-slate-600">{t("auth.registerDescription")}</p>
        </div>
        <div className="p-6 sm:p-8">
          <Alert tone="warning">{t("auth.warning")}</Alert>
          {message && <div className="mt-4"><Alert tone={success ? "info" : "error"}><span role="status">{message}</span></Alert></div>}
          <form onSubmit={submit} className="mt-6 grid gap-5">
            <label className="grid gap-2 text-sm font-semibold text-slate-700">
              {t("common.displayName")}
              <span className="relative">
                <UserRound className="pointer-events-none absolute left-3.5 top-1/2 -translate-y-1/2 text-slate-400" size={18} />
                <input name="full_name" autoComplete="name" className="w-full rounded-xl border border-slate-200 bg-slate-50 py-3 pl-11 pr-3 text-sm text-clinical-ink" placeholder={t("auth.displayPlaceholder")} />
              </span>
            </label>
            <label className="grid gap-2 text-sm font-semibold text-slate-700">
              {t("common.email")}
              <span className="relative">
                <Mail className="pointer-events-none absolute left-3.5 top-1/2 -translate-y-1/2 text-slate-400" size={18} />
                <input name="email" type="email" autoComplete="email" required className="w-full rounded-xl border border-slate-200 bg-slate-50 py-3 pl-11 pr-3 text-sm text-clinical-ink" placeholder="reviewer@example.com" />
              </span>
            </label>
            <label className="grid gap-2 text-sm font-semibold text-slate-700">
              {t("common.password")}
              <span className="relative">
                <LockKeyhole className="pointer-events-none absolute left-3.5 top-1/2 -translate-y-1/2 text-slate-400" size={18} />
                <input name="password" type="password" autoComplete="new-password" minLength="12" required className="w-full rounded-xl border border-slate-200 bg-slate-50 py-3 pl-11 pr-3 text-sm text-clinical-ink" />
              </span>
              <span className="text-xs font-normal text-slate-500">{t("auth.passwordHelp")}</span>
            </label>
            <Button className="mt-1 w-full" disabled={submitting}>{submitting ? t("auth.creating") : t("auth.createAccount")}</Button>
          </form>
        </div>
      </Card>
    </main>
  );
}
