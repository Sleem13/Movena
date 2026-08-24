import { useState } from "react";
import { useLocalSearchParams, useRouter } from "expo-router";

import { resetPassword } from "@/src/api/auth";
import { PasswordInput } from "@/src/components/PasswordInput";
import { Body, Card, ErrorState, PrimaryButton, Screen, Title } from "@/src/components/UI";

export default function ResetPasswordScreen() {
  const router = useRouter();
  const params = useLocalSearchParams<{ token?: string }>();
  const token = typeof params.token === "string" ? params.token : "";
  const [password, setPassword] = useState("");
  const [message, setMessage] = useState("");
  const [error, setError] = useState(token ? "" : "This reset link is missing its token.");
  const [busy, setBusy] = useState(false);
  async function submit() {
    setBusy(true); setError("");
    try { setMessage((await resetPassword(token, password)).message); }
    catch { setError("The reset link is invalid or expired."); }
    finally { setBusy(false); }
  }
  return <Screen><Title>Set a new password</Title><Body muted>This link is single-use and expires automatically.</Body>{message ? <Card tone="blue"><Body>{message}</Body></Card> : <><PasswordInput label="New password" value={password} onChangeText={setPassword} placeholder="At least 12 characters" />{error ? <ErrorState message={error} /> : null}<PrimaryButton title={busy ? "Updating…" : "Update password"} onPress={submit} disabled={busy || !token || password.length < 12} /></>}<PrimaryButton title="Continue to login" onPress={() => router.replace("/login")} secondary /></Screen>;
}
