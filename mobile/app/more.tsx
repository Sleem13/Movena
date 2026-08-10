import { StyleSheet, Text, View } from "react-native";
import { useRouter } from "expo-router";

import { AppShell, BrandHeader } from "@/src/components/AppShell";
import { ActionRow, SectionTitle } from "@/src/components/GuidedUI";
import { colors } from "@/src/config/theme";
import { useAuth } from "@/src/context/AuthContext";

export default function MoreScreen() {
  const router = useRouter(); const { user } = useAuth();
  return <AppShell active="more">
    <BrandHeader title="More" subtitle="Account, support, and app information." />
    <View style={styles.section}><SectionTitle>Account</SectionTitle><ActionRow title={user ? "Profile" : "Log in"} detail={user?.email || "Access protected session history"} icon="person-outline" onPress={() => router.push(user ? "/profile" : "/login")} /></View>
    <View style={styles.section}><SectionTitle>Help and settings</SectionTitle><ActionRow title="Safety & privacy" detail="Recording guidance and data handling" icon="shield-checkmark-outline" onPress={() => router.push("/safety")} /><ActionRow title="Known limitations" detail="Understand what the analysis can and cannot do" icon="information-circle-outline" onPress={() => router.push("/limitations")} /></View>
    <View style={styles.about}><Text style={styles.aboutTitle}>PhysioVision AI</Text><Text style={styles.aboutText}>Movement intelligence for guided exercise review.</Text><Text style={styles.version}>Version 0.28.0</Text></View>
  </AppShell>;
}

const styles = StyleSheet.create({ section: { gap: 10 }, about: { marginTop: 10, paddingVertical: 18, borderTopWidth: 1, borderTopColor: colors.border, gap: 4 }, aboutTitle: { color: colors.text, fontSize: 17, fontWeight: "800" }, aboutText: { color: colors.muted, fontSize: 13 }, version: { color: colors.muted, fontSize: 12, marginTop: 5 } });
