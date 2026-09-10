import { useCallback, useEffect, useState } from "react";
import { Pressable, ScrollView, StyleSheet, Text, View } from "react-native";
import Ionicons from "@expo/vector-icons/Ionicons";
import { useRouter } from "expo-router";

import { getSessionById, getSessions, SessionSummary } from "@/src/api/sessions";
import { AppShell, BrandHeader } from "@/src/components/AppShell";
import { CareAccess, NavRow } from "@/src/components/CareUI";
import { Body, Card, EmptyState, ErrorState, Heading, Loading, PrimaryButton } from "@/src/components/UI";
import { colors } from "@/src/config/theme";
import { useAuth } from "@/src/context/AuthContext";

export const SESSION_FILTERS = [["", "All"], ["bodyweight_squat", "Squat"], ["sit_to_stand", "Sit-to-Stand"], ["knee_extension", "Knee Extension"], ["shoulder_abduction", "Shoulder"], ["hip_abduction", "Hip"], ["push_up", "Push-Up"], ["shoulder_press", "Press"], ["bicep_curl", "Curl"]];

export default function SessionHistoryScreen() {
  return <CareAccess roles={["patient"]} active="progress"><SessionHistoryContent /></CareAccess>;
}
function SessionHistoryContent() {
  const router = useRouter(); const { user, loading: authLoading } = useAuth(); const [exercise, setExercise] = useState(""); const [items, setItems] = useState<SessionSummary[]>([]); const [detail, setDetail] = useState<Record<string, unknown> | null>(null); const [loading, setLoading] = useState(false); const [error, setError] = useState("");
  const load = useCallback(() => { if (!user) return; setLoading(true); setError(""); getSessions(exercise || undefined).then((data) => setItems(data.items)).catch((requestError) => setError(requestError.message)).finally(() => setLoading(false)); }, [user, exercise]);
  useEffect(load, [load]);
  if (authLoading) return <AppShell active="progress"><Loading label="Checking your account" /></AppShell>;
  if (!user) return null;
  return <AppShell active="progress">
    <BrandHeader title="Progress & activity" subtitle="Review completed movement checks and exercise activity." />
    <NavRow title="Recovery goals" detail="Track progress toward what matters to you" icon="flag-outline" onPress={() => router.push("/goals")} />
    <ScrollView horizontal showsHorizontalScrollIndicator={false} contentContainerStyle={styles.filters}>{SESSION_FILTERS.map(([id, label]) => <Pressable key={id} onPress={() => setExercise(id)} style={[styles.chip, exercise === id && styles.selected]}><Text style={[styles.chipText, exercise === id && styles.selectedText]}>{label}</Text></Pressable>)}</ScrollView>
    {loading ? <Loading label="Loading activity" /> : error ? <ErrorState message={error} action={<PrimaryButton title="Retry" onPress={load} />} /> : !items.length ? <EmptyState title="No movement activity yet" message="Complete a movement check from your plan to begin building your progress history." /> : items.map((item) => <Pressable key={item.session_id} onPress={async () => { try { setDetail(await getSessionById(item.session_id)); } catch (requestError) { setError((requestError as Error).message); } }} style={({ pressed }) => pressed && styles.pressed}><Card><View style={styles.row}><View style={styles.sessionIcon}><Ionicons name="fitness-outline" size={22} color={colors.primary} /></View><View style={styles.flex}><Heading>{item.exercise_display_name}</Heading><Body>{item.total_reps ?? 0} reps · {item.movement_score ?? "Not scored"}</Body><Body muted>{new Date(item.created_at).toLocaleDateString()}</Body></View><Ionicons name="chevron-forward" size={20} color={colors.text} /></View></Card></Pressable>)}
    {detail ? <Card tone="blue"><Heading>Session summary</Heading><Body>{String(detail.summary || detail.message || "No saved summary.")}</Body><PrimaryButton title="Close" onPress={() => setDetail(null)} secondary /></Card> : null}
  </AppShell>;
}

const styles = StyleSheet.create({ filters: { gap: 8, paddingRight: 16 }, chip: { minHeight: 40, borderWidth: 1, borderColor: colors.border, backgroundColor: colors.card, borderRadius: 20, paddingHorizontal: 15, alignItems: "center", justifyContent: "center" }, selected: { backgroundColor: colors.primary, borderColor: colors.primary }, chipText: { color: colors.text, fontWeight: "700", fontSize: 12 }, selectedText: { color: "#FFFFFF" }, row: { flexDirection: "row", alignItems: "center", gap: 12 }, sessionIcon: { width: 44, height: 44, borderRadius: 14, backgroundColor: colors.paleBlue, alignItems: "center", justifyContent: "center" }, flex: { flex: 1, gap: 2 }, loginState: { alignItems: "center", paddingVertical: 52, paddingHorizontal: 20, gap: 12 }, largeIcon: { width: 72, height: 72, borderRadius: 36, backgroundColor: colors.paleBlue, alignItems: "center", justifyContent: "center", marginBottom: 6 }, pressed: { opacity: 0.68 } });
