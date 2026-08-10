import type { ReactNode } from "react";
import { Pressable, StyleSheet, Text, View } from "react-native";
import Ionicons from "@expo/vector-icons/Ionicons";

import { colors } from "@/src/config/theme";

export function ActionRow({ title, detail, icon, onPress, primary = false, disabled = false }: { title: string; detail?: string; icon: keyof typeof Ionicons.glyphMap; onPress: () => void; primary?: boolean; disabled?: boolean }) {
  return <Pressable accessibilityRole="button" disabled={disabled} onPress={onPress} style={({ pressed }) => [styles.action, primary && styles.primaryAction, disabled && styles.disabled, pressed && styles.pressed]}>
    <View style={[styles.actionIcon, primary && styles.primaryIcon]}><Ionicons name={icon} size={28} color={primary ? colors.primary : colors.primary} /></View>
    <View style={styles.actionText}><Text style={[styles.actionTitle, primary && styles.primaryText]}>{title}</Text>{detail ? <Text style={[styles.actionDetail, primary && styles.primaryDetail]}>{detail}</Text> : null}</View>
    <Ionicons name="chevron-forward" size={22} color={primary ? "#FFFFFF" : colors.text} />
  </Pressable>;
}

const steps = [
  ["Exercise", "fitness-outline"], ["Video", "videocam-outline"], ["Review", "clipboard-outline"], ["Results", "bar-chart-outline"],
] as const;

export function AnalysisSteps({ active }: { active: 1 | 2 | 3 | 4 }) {
  return <View accessibilityLabel={`Analysis step ${active} of 4`} style={styles.steps}>{steps.map(([label, icon], index) => {
    const step = index + 1; const selected = step === active; const complete = step < active;
    return <View key={label} style={styles.stepWrap}>
      <View style={[styles.stepCircle, (selected || complete) && styles.stepCircleActive]}>{complete ? <Ionicons name="checkmark" size={16} color="#FFFFFF" /> : <Text style={[styles.stepNumber, selected && styles.stepNumberActive]}>{step}</Text>}</View>
      <Ionicons name={icon} size={20} color={selected || complete ? colors.primary : colors.muted} />
      <Text style={[styles.stepLabel, selected && styles.stepLabelActive]}>{label}</Text>
    </View>;
  })}</View>;
}

export function SectionTitle({ children }: { children: ReactNode }) { return <Text style={styles.sectionTitle}>{children}</Text>; }

const styles = StyleSheet.create({
  action: { minHeight: 88, borderWidth: 1, borderColor: colors.border, borderRadius: 18, backgroundColor: colors.card, paddingHorizontal: 16, paddingVertical: 14, flexDirection: "row", alignItems: "center", gap: 14 },
  primaryAction: { minHeight: 104, backgroundColor: colors.primary, borderColor: colors.primary, elevation: 4 },
  actionIcon: { width: 50, height: 50, borderRadius: 16, backgroundColor: colors.paleBlue, alignItems: "center", justifyContent: "center" }, primaryIcon: { backgroundColor: "#FFFFFF" },
  actionText: { flex: 1, gap: 3 }, actionTitle: { color: colors.text, fontSize: 17, fontWeight: "800" }, primaryText: { color: "#FFFFFF", fontSize: 19 }, actionDetail: { color: colors.muted, fontSize: 13, lineHeight: 18 }, primaryDetail: { color: "#DBEAFE" },
  disabled: { opacity: 0.45 }, pressed: { transform: [{ scale: 0.985 }], opacity: 0.9 },
  steps: { flexDirection: "row", justifyContent: "space-between", paddingVertical: 4 }, stepWrap: { flex: 1, alignItems: "center", gap: 5 }, stepCircle: { width: 30, height: 30, borderRadius: 15, borderWidth: 1.5, borderColor: "#CBD5E1", alignItems: "center", justifyContent: "center", backgroundColor: colors.card }, stepCircleActive: { borderColor: colors.primary, backgroundColor: colors.primary },
  stepNumber: { color: colors.muted, fontSize: 13, fontWeight: "800" }, stepNumberActive: { color: "#FFFFFF" }, stepLabel: { color: colors.muted, fontSize: 11, fontWeight: "700" }, stepLabelActive: { color: colors.primary },
  sectionTitle: { color: colors.text, fontSize: 21, lineHeight: 27, fontWeight: "800", letterSpacing: -0.2 },
});
