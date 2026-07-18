import { useState } from "react";
import { StyleSheet, TextInput } from "react-native";
import { useRouter } from "expo-router";
import { Body, ErrorState, PrimaryButton, SafetyNotice, Screen, Title } from "@/src/components/UI";
import { useAuth } from "@/src/context/AuthContext";
import { colors } from "@/src/config/theme";

export default function LoginScreen() {
  const router = useRouter();
  const { signIn } = useAuth();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);

  async function submit() {
    setBusy(true); setError("");
    try { await signIn(email.trim(), password); router.replace("/profile"); }
    catch (requestError) { setError((requestError as Error).message); }
    finally { setBusy(false); }
  }

  return <Screen><Title>Log in</Title><Body muted>Authentication is optional for analysis but required for protected session history.</Body><TextInput accessibilityLabel="Email" style={styles.input} autoCapitalize="none" keyboardType="email-address" value={email} onChangeText={setEmail} placeholder="email@example.com" /><TextInput accessibilityLabel="Password" style={styles.input} secureTextEntry value={password} onChangeText={setPassword} placeholder="Password" />{error ? <ErrorState message={error} /> : null}<PrimaryButton title={busy ? "Logging in…" : "Log in"} onPress={submit} disabled={busy || !email || !password} /><PrimaryButton title="Create demo account" onPress={() => router.push("/register")} secondary /><SafetyNotice /></Screen>;
}
const styles = StyleSheet.create({ input: { minHeight: 50, borderWidth: 1, borderColor: colors.border, borderRadius: 14, backgroundColor: colors.card, paddingHorizontal: 14, color: colors.text } });
