import { Ionicons } from "@expo/vector-icons";
import { useState } from "react";
import { Pressable, StyleSheet, TextInput, View } from "react-native";

import { colors } from "@/src/config/theme";

export function PasswordInput({ value, onChangeText, label = "Password", placeholder = "Password" }: { value: string; onChangeText: (value: string) => void; label?: string; placeholder?: string }) {
  const [visible, setVisible] = useState(false);
  return <View style={styles.container}><TextInput accessibilityLabel={label} style={styles.input} secureTextEntry={!visible} autoCapitalize="none" value={value} onChangeText={onChangeText} placeholder={placeholder} /><Pressable accessibilityRole="button" accessibilityLabel={visible ? `Hide ${label.toLowerCase()}` : `Show ${label.toLowerCase()}`} accessibilityState={{ expanded: visible }} onPress={() => setVisible((current) => !current)} style={styles.toggle}><Ionicons name={visible ? "eye-off-outline" : "eye-outline"} size={21} color={colors.muted} /></Pressable></View>;
}

const styles = StyleSheet.create({
  container: { position: "relative", justifyContent: "center" },
  input: { minHeight: 50, borderWidth: 1, borderColor: colors.border, borderRadius: 14, backgroundColor: colors.card, paddingLeft: 14, paddingRight: 52, color: colors.text },
  toggle: { position: "absolute", right: 6, width: 42, height: 42, alignItems: "center", justifyContent: "center", borderRadius: 12 },
});
