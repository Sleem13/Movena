import { useState } from "react";
import { StyleSheet, TextInput } from "react-native";
import { useRouter } from "expo-router";

import { requestPasswordReset } from "@/src/api/auth";
import { Body, Card, ErrorState, PrimaryButton, Screen, Title } from "@/src/components/UI";
import { colors } from "@/src/config/theme";

export default function ForgotPasswordScreen() {
  const router = useRouter();
  const [email, setEmail] = useState("");
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);
  async function submit() {
    setBusy(true); setError("");
    try { setMessage((await requestPasswordReset(email.trim())).message); }
    catch { setError("Password recovery is temporarily unavailable."); }
    finally { setBusy(false); }
  }
  return <Screen><Title>Forgot password?</Title><Body muted>Enter your verified email to receive a single-use reset link.</Body>{message ? <Card tone="blue"><Body>{message}</Body></Card> : null}<TextInput accessibilityLabel="Email" style={styles.input} autoCapitalize="none" keyboardType="email-address" value={email} onChangeText={setEmail} placeholder="email@example.com" />{error ? <ErrorState message={error} /> : null}<PrimaryButton title={busy ? "Sending…" : "Send reset link"} onPress={submit} disabled={busy || !email.includes("@")} /><PrimaryButton title="Back to login" onPress={() => router.replace("/login")} secondary /></Screen>;
}

const styles = StyleSheet.create({ input: { minHeight: 50, borderWidth: 1, borderColor: colors.border, borderRadius: 14, backgroundColor: colors.card, paddingHorizontal: 14, color: colors.text } });
