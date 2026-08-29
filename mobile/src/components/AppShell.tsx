import type { PropsWithChildren } from "react";
import { Image, Pressable, ScrollView, StyleSheet, Text, View } from "react-native";
import Ionicons from "@expo/vector-icons/Ionicons";
import { useRouter } from "expo-router";
import { SafeAreaView } from "react-native-safe-area-context";

import { colors } from "@/src/config/theme";

export type MainTab = "today" | "coach" | "progress" | "appointments" | "more";

const tabs: { key: MainTab; label: string; icon: keyof typeof Ionicons.glyphMap; route: "/today" | "/identify" | "/history" | "/appointments" | "/more" }[] = [
  { key: "today", label: "Today", icon: "calendar-outline", route: "/today" },
  { key: "coach", label: "Coach", icon: "scan-outline", route: "/identify" },
  { key: "progress", label: "Progress", icon: "trending-up-outline", route: "/history" },
  { key: "appointments", label: "Appointments", icon: "videocam-outline", route: "/appointments" },
  { key: "more", label: "More", icon: "ellipsis-horizontal-circle-outline", route: "/more" },
];

export function AppShell({ children, active, scroll = true }: PropsWithChildren<{ active: MainTab; scroll?: boolean }>) {
  const content = <View style={styles.content}>{children}</View>;
  return <SafeAreaView style={styles.shell} edges={["top", "left", "right", "bottom"]}>
    {scroll ? <ScrollView style={styles.scroll} contentContainerStyle={styles.scrollContent} showsVerticalScrollIndicator={false}>{content}</ScrollView> : content}
    <BottomNavigation active={active} />
  </SafeAreaView>;
}

export function BrandHeader({ title, subtitle }: { title?: string; subtitle?: string }) {
  const router = useRouter();
  return <View style={styles.header}>
    <View style={styles.brandRow}>
      <View style={styles.brand} accessibilityRole="image" accessibilityLabel="PhysioVision AI, AI-Assisted Rehabilitation Platform"><Image source={require("../../assets/images/brand-wordmark.png")} style={styles.wordmark} resizeMode="contain" /></View>
      <Pressable accessibilityRole="button" accessibilityLabel="Open profile" onPress={() => router.push("/profile")} style={({ pressed }) => [styles.profile, pressed && styles.pressed]}>
        <Ionicons name="person-outline" size={22} color={colors.text} />
      </Pressable>
    </View>
    {title ? <Text style={styles.pageTitle}>{title}</Text> : null}
    {subtitle ? <Text style={styles.subtitle}>{subtitle}</Text> : null}
  </View>;
}

export function BottomNavigation({ active }: { active: MainTab }) {
  const router = useRouter();
  return <View style={styles.nav}>{tabs.map((tab) => {
    const selected = active === tab.key;
    return <Pressable key={tab.key} accessibilityRole="button" accessibilityState={{ selected }} accessibilityLabel={tab.label} onPress={() => router.replace(tab.route as never)} style={({ pressed }) => [styles.navItem, pressed && styles.pressed]}>
      <View style={[styles.navIcon, selected && styles.navIconSelected]}><Ionicons name={tab.icon} size={23} color={selected ? colors.primary : "#475569"} /></View>
      <Text style={[styles.navLabel, selected && styles.navLabelSelected]}>{tab.label}</Text>
    </Pressable>;
  })}</View>;
}

const styles = StyleSheet.create({
  shell: { flex: 1, backgroundColor: colors.background }, scroll: { flex: 1 }, scrollContent: { paddingBottom: 26 },
  content: { flexGrow: 1, paddingHorizontal: 20, paddingTop: 14, gap: 18 },
  header: { gap: 8 }, brandRow: { flexDirection: "row", alignItems: "center", justifyContent: "space-between", marginBottom: 8 },
  brand: { flex: 1, alignItems: "flex-start", justifyContent: "center" }, wordmark: { width: 230, height: 77 },
  profile: { width: 44, height: 44, borderRadius: 22, borderWidth: 1, borderColor: colors.border, alignItems: "center", justifyContent: "center", backgroundColor: colors.card },
  pageTitle: { color: colors.text, fontSize: 32, lineHeight: 38, fontWeight: "800", letterSpacing: -0.6 }, subtitle: { color: colors.muted, fontSize: 15, lineHeight: 22, maxWidth: 520 },
  nav: { minHeight: 76, paddingBottom: 8, paddingTop: 7, paddingHorizontal: 6, borderTopWidth: 1, borderTopColor: colors.border, backgroundColor: colors.card, flexDirection: "row", alignItems: "center", justifyContent: "space-around" },
  navItem: { flex: 1, minHeight: 58, alignItems: "center", justifyContent: "center", gap: 3 }, navIcon: { width: 40, height: 32, borderRadius: 16, alignItems: "center", justifyContent: "center" }, navIconSelected: { backgroundColor: colors.paleBlue },
  navLabel: { color: "#475569", fontSize: 11, fontWeight: "600" }, navLabelSelected: { color: colors.primary, fontWeight: "800" }, pressed: { opacity: 0.68 },
});
