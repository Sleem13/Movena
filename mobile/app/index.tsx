import { Pressable, StyleSheet, Text, View } from "react-native";
import Ionicons from "@expo/vector-icons/Ionicons";
import { useRouter } from "expo-router";

import { AppShell, BrandHeader } from "@/src/components/AppShell";
import { ActionRow, SectionTitle } from "@/src/components/GuidedUI";
import { colors } from "@/src/config/theme";
import { useAnalysis } from "@/src/context/AnalysisContext";

export default function HomeScreen() {
  const router = useRouter();
  const { exercise } = useAnalysis();
  return <AppShell active="home">
    <BrandHeader />
    <Text style={styles.hero}>Ready to move?</Text>
    <ActionRow title="Start an analysis" detail="Record or choose a video" icon="videocam" primary onPress={() => router.push("/identify")} />
    <View style={styles.quickRow}>
      <QuickAction icon="scan-outline" label="Identify video" onPress={() => router.push("/identify")} />
      <QuickAction icon="fitness-outline" label="Choose exercise" onPress={() => router.push("/exercises")} />
    </View>
    {exercise ? <View style={styles.section}>
      <SectionTitle>Continue where you left off</SectionTitle>
      <Pressable onPress={() => router.push({ pathname: "/exercise/[id]", params: { id: exercise.exercise_id } })} style={({ pressed }) => [styles.continueRow, pressed && styles.pressed]}>
        <View style={styles.roundIcon}><Ionicons name="play" size={20} color={colors.primary} /></View>
        <View style={styles.flex}><Text style={styles.itemTitle}>{exercise.display_name}</Text><Text style={styles.itemDetail}>Resume your selected exercise</Text></View>
        <Ionicons name="chevron-forward" size={20} color={colors.text} />
      </Pressable>
    </View> : null}
    <View style={styles.section}>
      <SectionTitle>Recommended today</SectionTitle>
      <View style={styles.recommended}>
        <View style={styles.exerciseIcon}><Ionicons name="body-outline" size={44} color={colors.teal} /></View>
        <View style={styles.flex}><Text style={styles.itemTitle}>Bodyweight Squat</Text><Text style={styles.itemDetail}>Build lower-body control with a guided video check.</Text>
          <Pressable accessibilityRole="button" onPress={() => router.push({ pathname: "/exercise/[id]", params: { id: "bodyweight_squat" } })} style={({ pressed }) => [styles.smallButton, pressed && styles.pressed]}><Text style={styles.smallButtonText}>Start exercise</Text><Ionicons name="arrow-forward" size={17} color={colors.teal} /></Pressable>
        </View>
      </View>
    </View>
    <Pressable accessibilityRole="link" onPress={() => router.push("/limitations")} style={({ pressed }) => [styles.betaLink, pressed && styles.pressed]}><Ionicons name="information-circle-outline" size={17} color={colors.muted} /><Text style={styles.betaText}>Invite-only beta launch candidate · not public</Text><Text style={styles.betaAction}>Read Known Limitations</Text></Pressable>
  </AppShell>;
}

function QuickAction({ icon, label, onPress }: { icon: keyof typeof Ionicons.glyphMap; label: string; onPress: () => void }) {
  return <Pressable accessibilityRole="button" onPress={onPress} style={({ pressed }) => [styles.quick, pressed && styles.pressed]}><View style={styles.quickIcon}><Ionicons name={icon} size={24} color={colors.teal} /></View><Text style={styles.quickLabel}>{label}</Text><Ionicons name="chevron-forward" size={17} color={colors.text} /></Pressable>;
}

const styles = StyleSheet.create({
  hero: { color: colors.text, fontSize: 38, lineHeight: 44, letterSpacing: -1, fontWeight: "800", marginTop: 4 },
  quickRow: { flexDirection: "row", gap: 10 }, quick: { flex: 1, minHeight: 82, padding: 12, borderRadius: 17, borderWidth: 1, borderColor: colors.border, flexDirection: "row", alignItems: "center", gap: 8 }, quickIcon: { width: 38, height: 38, borderRadius: 13, backgroundColor: colors.paleTeal, alignItems: "center", justifyContent: "center" }, quickLabel: { flex: 1, color: colors.text, fontSize: 13, fontWeight: "800" },
  section: { gap: 11, marginTop: 4 }, continueRow: { borderRadius: 18, borderWidth: 1, borderColor: colors.border, padding: 15, flexDirection: "row", alignItems: "center", gap: 12 }, roundIcon: { width: 44, height: 44, borderRadius: 22, backgroundColor: colors.paleBlue, alignItems: "center", justifyContent: "center" },
  recommended: { flexDirection: "row", gap: 14, padding: 16, borderRadius: 20, borderWidth: 1, borderColor: colors.border, alignItems: "center" }, exerciseIcon: { width: 82, height: 108, borderRadius: 20, backgroundColor: colors.paleTeal, alignItems: "center", justifyContent: "center" },
  flex: { flex: 1, gap: 4 }, itemTitle: { color: colors.text, fontSize: 17, fontWeight: "800" }, itemDetail: { color: colors.muted, fontSize: 13, lineHeight: 18 },
  smallButton: { alignSelf: "flex-start", minHeight: 40, marginTop: 7, paddingHorizontal: 14, borderRadius: 20, borderWidth: 1, borderColor: "#99E6DD", backgroundColor: colors.paleTeal, flexDirection: "row", alignItems: "center", gap: 7 }, smallButtonText: { color: colors.teal, fontWeight: "800", fontSize: 13 },
  betaLink: { flexDirection: "row", alignItems: "center", flexWrap: "wrap", justifyContent: "center", gap: 5, paddingVertical: 8 }, betaText: { color: colors.muted, fontSize: 10 }, betaAction: { color: colors.primary, fontSize: 10, fontWeight: "800" }, pressed: { opacity: 0.68 },
});
