import { useEffect, useState } from "react";
import { StyleSheet, TextInput } from "react-native";
import { useLocalSearchParams, useRouter } from "expo-router";

import { resendVerification, verifyEmail } from "@/src/api/auth";
import { Body, Card, ErrorState, Loading, PrimaryButton, Screen, Title } from "@/src/components/UI";
import { colors } from "@/src/config/theme";

export default function VerifyEmailScreen() {
  const router = useRouter();
  const params = useLocalSearchParams<{ token?: string }>();
  const token = typeof params.token === "string" ? params.token : "";
  const [email, setEmail] = useState("");
  const [busy, setBusy] = useState(Boolean(token));
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");
  useEffect(() => {
    if (!token) return;
    verifyEmail(token).then((result) => setMessage(result.message)).catch(() => setError("The verification link is invalid or expired.")).finally(() => setBusy(false));
  }, [token]);
  async function resend() {
    setBusy(true); setError("");
    try { setMessage((await resendVerification(email.trim())).message); }
    catch { setError("Verification email could not be sent."); }
    finally { setBusy(false); }
  }
  return <Screen><Title>Verify your email</Title>{busy ? <Loading label="Processing secure link" /> : null}{message ? <Card tone="blue"><Body>{message}</Body></Card> : null}{error ? <ErrorState message={error} /> : null}{!token ? <><Body muted>Enter your email for a fresh verification link.</Body><TextInput accessibilityLabel="Email" style={styles.input} value={email} onChangeText={setEmail} autoCapitalize="none" keyboardType="email-address" /><PrimaryButton title="Resend verification" onPress={resend} disabled={busy || !email.includes("@")} /></> : null}<PrimaryButton title="Continue to login" onPress={() => router.replace("/login")} secondary /></Screen>;
}

const styles = StyleSheet.create({ input: { minHeight: 50, borderWidth: 1, borderColor: colors.border, borderRadius: 14, backgroundColor: colors.card, paddingHorizontal: 14, color: colors.text } });
