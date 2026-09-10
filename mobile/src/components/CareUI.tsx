import { Fragment, type PropsWithChildren } from "react";
import { Pressable, StyleSheet, Text, TextInput, View, type TextInputProps } from "react-native";
import Ionicons from "@expo/vector-icons/Ionicons";
import { useRouter } from "expo-router";
import { useAuth } from "@/src/context/AuthContext";
import { AppShell, BrandHeader, type MainTab } from "./AppShell";
import { Body, Loading, PrimaryButton } from "./UI";
import { colors } from "@/src/config/theme";

export function CareAccess({ children, roles = ["patient", "therapist"], active = "today" }: PropsWithChildren<{ roles?: string[]; active?: MainTab }>) {
  const { user, loading } = useAuth();
  const router = useRouter();
  if (loading) return <AppShell active={active}><Loading label="Opening your workspace" /></AppShell>;
  if (!user) return <AppShell active={active}><BrandHeader title="Your care, in one place" subtitle="Log in for your plan, care team, and progress." /><PrimaryButton title="Log in" onPress={() => router.push("/login")} /><PrimaryButton title="Create account" secondary onPress={() => router.push("/register")} /><NavRow title="Explore movement checks" detail="Learn how to record an exercise" icon="videocam-outline" onPress={() => router.push("/identify")} /></AppShell>;
  if (!roles.includes(user.role)) return <AppShell active="more"><BrandHeader title="Your workspace" /><Body>This page is for {roles.join(" or ")} accounts.</Body><PrimaryButton title="Go to my workspace" onPress={() => router.replace(user.role === "therapist" ? "/patients" : user.role === "patient" ? "/today" : "/more")} /></AppShell>;
  return <Fragment key={user.user_id}>{children}</Fragment>;
}

export function NavRow({ title, detail, icon = "chevron-forward", onPress, initials: letters }: { title: string; detail?: string; icon?: keyof typeof Ionicons.glyphMap; onPress: () => void; initials?: string }) {
  return <Pressable accessibilityRole="button" onPress={onPress} style={({ pressed }) => [careStyles.navRow, pressed && { opacity: 0.7 }]}>
    <View style={careStyles.circle}>{letters ? <Text style={careStyles.initials}>{letters}</Text> : <Ionicons name={icon} size={22} color={colors.primaryDark} />}</View>
    <View style={careStyles.flex}><Text style={careStyles.rowTitle}>{title}</Text>{detail ? <Text style={careStyles.detail}>{detail}</Text> : null}</View>
    <Ionicons name="chevron-forward" size={19} color={colors.muted} />
  </Pressable>;
}

export function Field({ label, ...props }: TextInputProps & { label: string }) {
  return <View style={careStyles.field}><Text style={careStyles.label}>{label}</Text><TextInput accessibilityLabel={label} placeholderTextColor={colors.muted} {...props} style={[careStyles.input, props.multiline && careStyles.multiline, props.style]} /></View>;
}
export function Check({ label, checked, onChange, disabled = false }: { label: string; checked: boolean; onChange: (value: boolean) => void; disabled?: boolean }) {
  return <Pressable accessibilityRole="checkbox" accessibilityLabel={label} accessibilityState={{ checked, disabled }} disabled={disabled} onPress={() => onChange(!checked)} style={careStyles.check}>
    <Ionicons name={checked ? "checkbox" : "square-outline"} size={24} color={checked ? colors.primaryDark : colors.muted} /><Text style={careStyles.checkLabel}>{label}</Text>
  </Pressable>;
}
export function Choice({ options, value, onChange }: { options: readonly (readonly [string, string])[]; value: string; onChange: (value: string) => void }) {
  return <View style={careStyles.choices}>{options.map(([key, label]) => <Pressable key={key} accessibilityRole="radio" accessibilityLabel={label} accessibilityState={{ checked: key === value }} onPress={() => onChange(key)} style={[careStyles.choice, key === value && careStyles.selected]}><Text style={[careStyles.choiceText, key === value && { color: colors.primaryDark }]}>{label}</Text></Pressable>)}</View>;
}
export const careStyles = StyleSheet.create({
  flex: { flex: 1, minWidth: 0, gap: 4 }, section: { gap: 12 }, row: { flexDirection: "row", alignItems: "center", gap: 12 },
  navRow: { flexDirection: "row", alignItems: "center", gap: 14, paddingVertical: 18, borderBottomColor: colors.border, borderBottomWidth: 1, minHeight: 82 },
  circle: { width: 44, height: 44, borderRadius: 22, backgroundColor: colors.paleBlue, alignItems: "center", justifyContent: "center" },
  initials: { color: colors.primaryDark, fontWeight: "700", fontSize: 16 }, rowTitle: { fontSize: 17, lineHeight: 23, fontWeight: "700", color: colors.text }, detail: { color: colors.muted, fontSize: 14, lineHeight: 21 },
  field: { gap: 7 }, label: { fontSize: 14, lineHeight: 20, fontWeight: "600", color: colors.text },
  input: { minHeight: 50, borderWidth: 1, borderColor: colors.border, borderRadius: 12, backgroundColor: colors.surface, paddingHorizontal: 14, color: colors.text, fontSize: 16 },
  multiline: { minHeight: 88, paddingVertical: 12, textAlignVertical: "top" },
  check: { flexDirection: "row", alignItems: "center", gap: 10, minHeight: 48, paddingVertical: 6 }, checkLabel: { flex: 1, fontSize: 15, lineHeight: 22, color: colors.text },
  choices: { flexDirection: "row", flexWrap: "wrap", gap: 8 }, choice: { minHeight: 46, borderWidth: 1, borderColor: colors.border, borderRadius: 12, paddingHorizontal: 13, paddingVertical: 11, justifyContent: "center" },
  selected: { backgroundColor: colors.paleBlue, borderColor: colors.primary }, choiceText: { fontSize: 14, color: colors.text, fontWeight: "600" },
});
