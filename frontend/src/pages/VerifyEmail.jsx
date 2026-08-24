import { ArrowLeft, Mail, ShieldCheck } from "lucide-react";
import { useEffect, useState } from "react";

import { Alert, Button, Card, LoadingSpinner } from "../components/common/UI.jsx";
import { resendVerificationEmail, verifyEmailToken } from "../services/api.js";

export default function VerifyEmail({ onLogin }) {
  const token = new URLSearchParams(window.location.search).get("token") || "";
  const [status, setStatus] = useState(token ? "verifying" : "resend");
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");
  useEffect(() => {
    if (!token) return;
    verifyEmailToken(token).then((result) => { setMessage(result.message); setStatus("verified"); }).catch((requestError) => { setError(requestError.response?.data?.message || "The verification link is invalid or expired."); setStatus("resend"); });
  }, [token]);
  async function resend(event) {
    event.preventDefault(); setError("");
    const email = new FormData(event.currentTarget).get("email");
    try { setMessage((await resendVerificationEmail(email)).message); }
    catch (requestError) { setError(requestError.response?.data?.message || "Verification email could not be sent."); }
  }
  return <main className="mx-auto w-full max-w-lg px-6 py-12"><button onClick={onLogin} className="mb-6 inline-flex items-center gap-2 text-sm font-semibold text-slate-500 hover:text-clinical-blue"><ArrowLeft size={16} />Back to login</button><Card className="p-6 sm:p-8"><ShieldCheck className="text-clinical-teal" size={30} /><h1 className="mt-4 text-3xl font-extrabold text-clinical-ink">Verify your email</h1>
    {status === "verifying" ? <div className="mt-6"><LoadingSpinner label="Verifying secure link" /></div> : null}
    {message ? <Alert tone="info" className="mt-5">{message}</Alert> : null}{error ? <Alert className="mt-5">{error}</Alert> : null}
    {status === "verified" ? <Button className="mt-6 w-full" onClick={onLogin}>Continue to login</Button> : status === "resend" ? <form onSubmit={resend} className="mt-6 grid gap-4"><p className="text-sm leading-6 text-slate-600">Enter your email to receive a fresh verification link.</p><label className="relative"><span className="sr-only">Email address</span><Mail className="absolute left-3.5 top-1/2 -translate-y-1/2 text-slate-400" size={18} /><input name="email" type="email" required autoComplete="email" className="w-full rounded-xl border border-slate-200 bg-slate-50 py-3 pl-11 pr-3 text-sm" placeholder="you@example.com" /></label><Button>Resend verification email</Button></form> : null}
  </Card></main>;
}
