import { useCallback, useState } from "react";
import { StyleSheet, TextInput } from "react-native";
import { useFocusEffect, useRouter } from "expo-router";
import { register } from "@/src/api/auth";
import { Body, Card, ErrorState, PrimaryButton, SafetyNotice, Screen, Title } from "@/src/components/UI";
import { colors } from "@/src/config/theme";
import { authRequestErrorMessage, validateRegistrationInput } from "@/src/utils/authValidation";

export default function RegisterScreen() {
  const router = useRouter();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [name, setName] = useState("");
  const [authError, setAuthError] = useState("");
  const [busy, setBusy] = useState(false);

  useFocusEffect(useCallback(() => { setAuthError(""); }, []));

  async function submit() {
    const validationError = validateRegistrationInput(name, email, password);
    if (validationError) { setAuthError(validationError); return; }
    setBusy(true); setAuthError("");
    try { await register({ email: email.trim(), password, full_name: name.trim() }); router.replace("/login"); }
    catch (requestError) { setAuthError(authRequestErrorMessage(requestError as Error & { code?: string }, "create")); }
    finally { setBusy(false); }
  }

  return <Screen><Title>Create demo account</Title><Card tone="warning"><Body>Use non-identifying development information only. This app is not a medical record.</Body></Card><TextInput accessibilityLabel="Display name" style={styles.input} value={name} onChangeText={(value) => { setName(value); setAuthError(""); }} placeholder="Demo display name" /><TextInput accessibilityLabel="Email" style={styles.input} autoCapitalize="none" keyboardType="email-address" value={email} onChangeText={(value) => { setEmail(value); setAuthError(""); }} placeholder="email@example.com" /><TextInput accessibilityLabel="Password" style={styles.input} secureTextEntry value={password} onChangeText={(value) => { setPassword(value); setAuthError(""); }} placeholder="At least 8 characters" />{authError ? <ErrorState message={authError} /> : null}<PrimaryButton title={busy ? "Creating…" : "Create account"} onPress={submit} disabled={busy} /><SafetyNotice /></Screen>;
}
const styles = StyleSheet.create({ input: { minHeight: 50, borderWidth: 1, borderColor: colors.border, borderRadius: 14, backgroundColor: colors.card, paddingHorizontal: 14, color: colors.text } });
