import { ArrowLeft, Mail } from "lucide-react";
import { useState } from "react";

import { Alert, Button, Card } from "../components/common/UI.jsx";
import { requestPasswordReset } from "../services/api.js";

export default function ForgotPassword({ onLogin }) {
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");
  const [submitting, setSubmitting] = useState(false);
  async function submit(event) {
    event.preventDefault(); setSubmitting(true); setError(""); setMessage("");
    const email = new FormData(event.currentTarget).get("email");
    try { setMessage((await requestPasswordReset(email)).message); }
    catch (requestError) { setError(requestError.response?.data?.message || "Password recovery is temporarily unavailable."); }
    finally { setSubmitting(false); }
  }
  return <main className="mx-auto w-full max-w-lg px-6 py-12">
    <button onClick={onLogin} className="mb-6 inline-flex items-center gap-2 text-sm font-semibold text-slate-500 hover:text-clinical-blue"><ArrowLeft size={16} />Back to login</button>
    <Card className="p-6 sm:p-8">
      <p className="text-xs font-bold uppercase tracking-[0.18em] text-clinical-teal">Account recovery</p>
      <h1 className="mt-3 text-3xl font-extrabold text-clinical-ink">Forgot your password?</h1>
      <p className="mt-3 text-sm leading-6 text-slate-600">Enter your verified email. If the account is eligible, we’ll send a single-use reset link.</p>
      {message ? <Alert tone="info" className="mt-5">{message}</Alert> : null}{error ? <Alert className="mt-5">{error}</Alert> : null}
      <form onSubmit={submit} className="mt-6 grid gap-5">
        <label className="grid gap-2 text-sm font-semibold text-slate-700">Email address<span className="relative"><Mail className="absolute left-3.5 top-1/2 -translate-y-1/2 text-slate-400" size={18} /><input name="email" type="email" autoComplete="email" required className="w-full rounded-xl border border-slate-200 bg-slate-50 py-3 pl-11 pr-3 text-sm" /></span></label>
        <Button disabled={submitting}>{submitting ? "Sending…" : "Send reset link"}</Button>
      </form>
    </Card>
  </main>;
}
