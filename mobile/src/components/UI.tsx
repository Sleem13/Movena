import type { PropsWithChildren, ReactNode } from "react";
import { ActivityIndicator, Pressable, ScrollView, StyleSheet, Text, View } from "react-native";
import { colors, DISCLAIMER } from "@/src/config/theme";

export function Screen({ children, scroll = true }: PropsWithChildren<{ scroll?: boolean }>) {
  const content = <View style={styles.content}>{children}</View>;
  return scroll ? <ScrollView style={styles.screen} contentContainerStyle={styles.scroll}>{content}</ScrollView> : <View style={[styles.screen, styles.content]}>{children}</View>;
}
export const Card = ({ children, tone = "default" }: PropsWithChildren<{ tone?: "default" | "warning" | "blue" }>) => <View style={[styles.card, tone === "warning" && styles.warningCard, tone === "blue" && styles.blueCard]}>{children}</View>;
export const Title = ({ children }: PropsWithChildren) => <Text style={styles.title}>{children}</Text>;
export const Heading = ({ children }: PropsWithChildren) => <Text style={styles.heading}>{children}</Text>;
export const Body = ({ children, muted = false }: PropsWithChildren<{ muted?: boolean }>) => <Text style={[styles.body, muted && styles.muted]}>{children}</Text>;
export function PrimaryButton({ title, onPress, disabled = false, secondary = false }: { title: string; onPress: () => void; disabled?: boolean; secondary?: boolean }) {
  return <Pressable accessibilityRole="button" accessibilityState={{ disabled }} disabled={disabled} onPress={onPress} style={({ pressed }) => [styles.button, secondary && styles.secondaryButton, disabled && styles.disabled, pressed && styles.pressed]}><Text style={[styles.buttonText, secondary && styles.secondaryText]}>{title}</Text></Pressable>;
}
export function StatusBadge({ label, tone = "blue" }: { label: string; tone?: "blue" | "success" | "warning" | "muted" }) {
  const bg = tone === "success" ? "#DCFCE7" : tone === "warning" ? "#FEF3C7" : tone === "muted" ? "#E2E8F0" : "#DBEAFE";
  return <View style={[styles.badge, { backgroundColor: bg }]}><Text style={styles.badgeText}>{label}</Text></View>;
}
export const Loading = ({ label = "Loading" }: { label?: string }) => <View style={styles.row}><ActivityIndicator color={colors.primary} /><Body>{label}</Body></View>;
export const ErrorState = ({ message, action }: { message: string; action?: ReactNode }) => <Card tone="warning"><Heading>Something needs attention</Heading><Body>{message}</Body>{action}</Card>;
export const EmptyState = ({ title, message }: { title: string; message: string }) => <Card><Heading>{title}</Heading><Body muted>{message}</Body></Card>;
export const SafetyNotice = () => <Card tone="warning"><Heading>Safety reminder</Heading><Body>{DISCLAIMER}</Body><Body muted>Stop if you feel pain, dizziness, or unusual symptoms and consider professional review.</Body></Card>;

const styles = StyleSheet.create({
  screen: { flex: 1, backgroundColor: colors.background }, scroll: { paddingBottom: 36 }, content: { padding: 20, gap: 16 },
  card: { backgroundColor: colors.card, borderColor: colors.border, borderWidth: 1, borderRadius: 18, padding: 18, gap: 10 },
  warningCard: { backgroundColor: colors.paleAmber, borderColor: "#FDE68A" }, blueCard: { backgroundColor: colors.paleBlue, borderColor: "#BFDBFE" },
  title: { fontSize: 30, fontWeight: "800", color: colors.text, lineHeight: 36 }, heading: { fontSize: 18, fontWeight: "700", color: colors.text },
  body: { fontSize: 15, lineHeight: 22, color: colors.text }, muted: { color: colors.muted },
  button: { minHeight: 48, borderRadius: 14, backgroundColor: colors.primary, alignItems: "center", justifyContent: "center", paddingHorizontal: 18, marginTop: 4 },
  secondaryButton: { backgroundColor: colors.card, borderWidth: 1, borderColor: colors.border }, buttonText: { color: "white", fontWeight: "700", fontSize: 15 }, secondaryText: { color: colors.text },
  disabled: { opacity: 0.45 }, pressed: { opacity: 0.8 }, badge: { alignSelf: "flex-start", borderRadius: 999, paddingVertical: 5, paddingHorizontal: 10 }, badgeText: { color: colors.text, fontWeight: "700", fontSize: 12 },
  row: { flexDirection: "row", alignItems: "center", gap: 10 },
});
