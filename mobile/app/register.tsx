import { useCallback, useState } from "react";
import { StyleSheet, TextInput } from "react-native";
import { useFocusEffect, useRouter } from "expo-router";

import { register } from "@/src/api/auth";
import { PasswordInput } from "@/src/components/PasswordInput";
import { Body, BrandLockup, Card, ErrorState, PrimaryButton, SafetyNotice, Screen, Title } from "@/src/components/UI";
import { colors } from "@/src/config/theme";
import { authRequestErrorMessage, validateRegistrationInput } from "@/src/utils/authValidation";
import { Check } from "@/src/components/CareUI";

export default function RegisterScreen() {
  const router = useRouter();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [name, setName] = useState("");
  const [username, setUsername] = useState("");
  const [terms, setTerms] = useState(false);
  const [privacy, setPrivacy] = useState(false);
  const [authError, setAuthError] = useState("");
  const [success, setSuccess] = useState("");
  const [busy, setBusy] = useState(false);
  useFocusEffect(useCallback(() => { setAuthError(""); }, []));

  async function submit() {
    const validationError = validateRegistrationInput(name, email, password);
    if (validationError) { setAuthError(validationError); return; }
    if (!/^[a-zA-Z0-9._-]{3,64}$/.test(username.trim())) { setAuthError("Username may use letters, numbers, dots, hyphens, and underscores."); return; }
    if (!terms || !privacy) { setAuthError("Accept the terms and privacy policy to create a patient account."); return; }
    setBusy(true); setAuthError("");
    try { await register({ username: username.trim(), email: email.trim(), password, full_name: name.trim(), accepted_terms: terms, accepted_privacy: privacy }); setSuccess("Account created. Check your email to verify it before logging in."); }
    catch (requestError) { setAuthError(authRequestErrorMessage(requestError as Error & { code?: string }, "create")); }
    finally { setBusy(false); }
  }

  return <Screen><BrandLockup /><Title>Create patient account</Title><Body muted>Use this account for your prescribed plan, check-ins, and care team.</Body><Card tone="warning"><Body>Use non-identifying development information during the invite-only beta. This app is not a medical record.</Body></Card>{success ? <Card tone="blue"><Body>{success}</Body><PrimaryButton title="Continue to login" onPress={() => router.replace("/login")} /></Card> : <><TextInput accessibilityLabel="Full name" style={styles.input} value={name} onChangeText={(value) => { setName(value); setAuthError(""); }} placeholder="Full name" /><TextInput accessibilityLabel="Username" style={styles.input} autoCapitalize="none" value={username} onChangeText={(value) => { setUsername(value); setAuthError(""); }} placeholder="Username" /><TextInput accessibilityLabel="Email" style={styles.input} autoCapitalize="none" keyboardType="email-address" value={email} onChangeText={(value) => { setEmail(value); setAuthError(""); }} placeholder="email@example.com" /><PasswordInput value={password} onChangeText={(value) => { setPassword(value); setAuthError(""); }} placeholder="At least 12 characters" /><Check label="I accept the Terms of Service" checked={terms} onChange={setTerms} /><Check label="I accept the Privacy Policy" checked={privacy} onChange={setPrivacy} />{authError ? <ErrorState message={authError} /> : null}<PrimaryButton title={busy ? "Creating…" : "Create account"} onPress={submit} disabled={busy} /></>}<SafetyNotice /></Screen>;
}

const styles = StyleSheet.create({ input: { minHeight: 50, borderWidth: 1, borderColor: colors.border, borderRadius: 14, backgroundColor: colors.card, paddingHorizontal: 14, color: colors.text } });
