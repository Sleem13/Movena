import { useState } from "react";
import { StyleSheet, TextInput } from "react-native";
import { useRouter } from "expo-router";
import { register } from "@/src/api/auth";
import { Body, Card, ErrorState, PrimaryButton, SafetyNotice, Screen, Title } from "@/src/components/UI";
import { colors } from "@/src/config/theme";

export default function RegisterScreen() {
  const router = useRouter();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [name, setName] = useState("");
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);

  async function submit() {
    setBusy(true); setError("");
    try { await register({ email: email.trim(), password, full_name: name.trim() || undefined }); router.replace("/login"); }
    catch (requestError) { setError((requestError as Error).message); }
    finally { setBusy(false); }
  }

  return <Screen><Title>Create demo account</Title><Card tone="warning"><Body>Use non-identifying development information only. This app is not a medical record.</Body></Card><TextInput accessibilityLabel="Display name" style={styles.input} value={name} onChangeText={setName} placeholder="Optional demo name" /><TextInput accessibilityLabel="Email" style={styles.input} autoCapitalize="none" keyboardType="email-address" value={email} onChangeText={setEmail} placeholder="email@example.com" /><TextInput accessibilityLabel="Password" style={styles.input} secureTextEntry value={password} onChangeText={setPassword} placeholder="At least 8 characters" />{error ? <ErrorState message={error} /> : null}<PrimaryButton title={busy ? "Creating…" : "Create account"} onPress={submit} disabled={busy || !email || password.length < 8} /><SafetyNotice /></Screen>;
}
const styles = StyleSheet.create({ input: { minHeight: 50, borderWidth: 1, borderColor: colors.border, borderRadius: 14, backgroundColor: colors.card, paddingHorizontal: 14, color: colors.text } });
