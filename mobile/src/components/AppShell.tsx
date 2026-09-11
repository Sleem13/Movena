import type { PropsWithChildren } from "react";
import { Pressable, ScrollView, StyleSheet, Text, View } from "react-native";
import Ionicons from "@expo/vector-icons/Ionicons";
import { useRouter } from "expo-router";
import { SafeAreaView } from "react-native-safe-area-context";

import { colors } from "@/src/config/theme";
import { BrandLockup } from "@/src/components/UI";
import { useAuth } from "@/src/context/AuthContext";
import { initials, isTherapist } from "@/src/utils/care";

export type MainTab = "today" | "coach" | "progress" | "appointments" | "more" | "team" | "patients" | "review";

type Tab = { key: MainTab; label: string; icon: keyof typeof Ionicons.glyphMap; route: string };
const patientTabs: Tab[] = [
  { key: "today", label: "Today", icon: "home-outline", route: "/today" },
  { key: "progress", label: "Progress", icon: "trending-up-outline", route: "/history" },
  { key: "team", label: "Care team", icon: "people-outline", route: "/care-team" },
  { key: "more", label: "Account", icon: "person-outline", route: "/more" },
];
const therapistTabs: Tab[] = [
  { key: "patients", label: "Patients", icon: "people-outline", route: "/patients" },
  { key: "review", label: "Review", icon: "document-text-outline", route: "/review" },
  { key: "appointments", label: "Schedule", icon: "calendar-outline", route: "/appointments" },
  { key: "more", label: "Account", icon: "person-outline", route: "/more" },
];

export function AppShell({ children, active, scroll = true }: PropsWithChildren<{ active: MainTab; scroll?: boolean }>) {
  const content = <View style={styles.content}>{children}</View>;
  return <SafeAreaView style={styles.shell} edges={["top", "left", "right", "bottom"]}>
    {scroll ? <ScrollView style={styles.scroll} keyboardShouldPersistTaps="handled" contentContainerStyle={styles.scrollContent} showsVerticalScrollIndicator={false}>{content}</ScrollView> : content}
    <BottomNavigation active={active} />
  </SafeAreaView>;
}

export function BrandHeader({ title, subtitle }: { title?: string; subtitle?: string }) {
  const router = useRouter();
  const { user } = useAuth();
  return <View style={styles.header}>
    <View style={styles.brandRow}>
      <View style={styles.brand}><BrandLockup compact /></View>
      <Pressable accessibilityRole="button" accessibilityLabel="Open profile" onPress={() => router.push("/profile")} style={({ pressed }) => [styles.profile, pressed && styles.pressed]}>
        {user?.full_name ? <Text style={styles.initials}>{initials(user.full_name)}</Text> : <Ionicons name="person-outline" size={22} color={colors.text} />}
      </Pressable>
    </View>
    {title ? <Text style={styles.pageTitle}>{title}</Text> : null}
    {subtitle ? <Text style={styles.subtitle}>{subtitle}</Text> : null}
  </View>;
}

export function BottomNavigation({ active }: { active: MainTab }) {
  const router = useRouter();
  const { user } = useAuth();
  const therapist = isTherapist(user?.role);
  const tabs = therapist ? therapistTabs : patientTabs;
  const selectedTab = active === "coach" ? (therapist ? "patients" : "today") : !therapist && active === "appointments" ? "team" : therapist && active === "team" ? "patients" : active;
  return <View style={styles.nav}>{tabs.map((tab) => {
    const selected = selectedTab === tab.key;
    return <Pressable key={tab.key} accessibilityRole="button" accessibilityState={{ selected }} accessibilityLabel={tab.label} onPress={() => router.replace(tab.route as never)} style={({ pressed }) => [styles.navItem, pressed && styles.pressed]}>
      <View style={[styles.navIcon, selected && styles.navIconSelected]}><Ionicons name={tab.icon} size={23} color={selected ? colors.primary : "#475569"} /></View>
      <Text style={[styles.navLabel, selected && styles.navLabelSelected]}>{tab.label}</Text>
    </Pressable>;
  })}</View>;
}

const styles = StyleSheet.create({
  shell: { flex: 1, backgroundColor: colors.background }, scroll: { flex: 1 }, scrollContent: { paddingBottom: 26 },
  content: { flexGrow: 1, paddingHorizontal: 20, paddingTop: 20, gap: 22, width: "100%", maxWidth: 720, alignSelf: "center" },
  header: { gap: 8 }, brandRow: { flexDirection: "row", alignItems: "center", justifyContent: "space-between", marginBottom: 20 },
  brand: { flex: 1, alignItems: "flex-start", justifyContent: "center" }, initials: { fontSize: 15, color: colors.text, fontWeight: "700" },
  profile: { width: 44, height: 44, borderRadius: 22, borderWidth: 1, borderColor: colors.border, alignItems: "center", justifyContent: "center", backgroundColor: colors.card },
  pageTitle: { color: colors.text, fontSize: 30, lineHeight: 37, fontWeight: "800", letterSpacing: -0.7 }, subtitle: { color: colors.muted, fontSize: 16, lineHeight: 24, maxWidth: 540 },
  nav: { minHeight: 76, paddingBottom: 8, paddingTop: 7, paddingHorizontal: 6, borderTopWidth: 1, borderTopColor: colors.border, backgroundColor: colors.card, flexDirection: "row", alignItems: "center", justifyContent: "space-around" },
  navItem: { flex: 1, minHeight: 58, alignItems: "center", justifyContent: "center", gap: 3 }, navIcon: { width: 40, height: 32, borderRadius: 16, alignItems: "center", justifyContent: "center" }, navIconSelected: { backgroundColor: colors.paleBlue },
  navLabel: { color: "#475569", fontSize: 11, fontWeight: "600" }, navLabelSelected: { color: colors.primary, fontWeight: "800" }, pressed: { opacity: 0.68 },
});
