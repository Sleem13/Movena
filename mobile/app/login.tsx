import { useCallback, useState } from "react";
import { StyleSheet, TextInput } from "react-native";
import { useFocusEffect, useRouter } from "expo-router";
import { Body, ErrorState, PrimaryButton, SafetyNotice, Screen, Title } from "@/src/components/UI";
import { useAuth } from "@/src/context/AuthContext";
import { colors } from "@/src/config/theme";
import { authRequestErrorMessage, validateLoginInput } from "@/src/utils/authValidation";

export default function LoginScreen() {
  const router = useRouter();
  const { signIn } = useAuth();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [authError, setAuthError] = useState("");
  const [busy, setBusy] = useState(false);

  useFocusEffect(useCallback(() => { setAuthError(""); }, []));

  async function submit() {
    const validationError = validateLoginInput(email, password);
    if (validationError) { setAuthError(validationError); return; }
    setBusy(true); setAuthError("");
    try { await signIn(email.trim(), password); router.replace("/profile"); }
    catch (requestError) { setAuthError(authRequestErrorMessage(requestError as Error & { code?: string }, "login")); }
    finally { setBusy(false); }
  }

  return <Screen><Title>Log in</Title><Body muted>Authentication is optional for analysis but required for protected session history.</Body><TextInput accessibilityLabel="Username or email" style={styles.input} autoCapitalize="none" value={email} onChangeText={(value) => { setEmail(value); setAuthError(""); }} placeholder="Username or email" /><TextInput accessibilityLabel="Password" style={styles.input} secureTextEntry value={password} onChangeText={(value) => { setPassword(value); setAuthError(""); }} placeholder="Password" />{authError ? <ErrorState message={authError} /> : null}<PrimaryButton title={busy ? "Logging in…" : "Log in"} onPress={submit} disabled={busy} /><PrimaryButton title="Create demo account" onPress={() => router.push("/register")} secondary /><SafetyNotice /></Screen>;
}
const styles = StyleSheet.create({ input: { minHeight: 50, borderWidth: 1, borderColor: colors.border, borderRadius: 14, backgroundColor: colors.card, paddingHorizontal: 14, color: colors.text } });
