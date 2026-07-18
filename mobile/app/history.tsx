import { useCallback, useEffect, useState } from "react";
import { Pressable, StyleSheet, Text, View } from "react-native";
import { useRouter } from "expo-router";
import { getSessionById, getSessions, SessionSummary } from "@/src/api/sessions";
import { Body, Card, EmptyState, ErrorState, Heading, Loading, PrimaryButton, Screen, StatusBadge, Title } from "@/src/components/UI";
import { useAuth } from "@/src/context/AuthContext";
import { colors } from "@/src/config/theme";

const filters = [["", "All"], ["bodyweight_squat", "Squat"], ["sit_to_stand", "Sit-to-Stand"], ["knee_extension", "Knee Extension"], ["shoulder_abduction", "Shoulder"], ["hip_abduction", "Hip"]];
export default function SessionHistoryScreen() {
  const router = useRouter(); const { user, loading: authLoading } = useAuth(); const [exercise, setExercise] = useState(""); const [items, setItems] = useState<SessionSummary[]>([]); const [detail, setDetail] = useState<Record<string, unknown> | null>(null); const [loading, setLoading] = useState(false); const [error, setError] = useState("");
  const load = useCallback(() => { if (!user) return; setLoading(true); setError(""); getSessions(exercise || undefined).then((data) => setItems(data.items)).catch((e) => setError(e.message)).finally(() => setLoading(false)); }, [user, exercise]);
  useEffect(load, [load]);
  if (authLoading) return <Screen><Loading label="Checking login" /></Screen>;
  if (!user) return <Screen><Title>Session History</Title><Body muted>Protected history requires a login.</Body><PrimaryButton title="Log in" onPress={() => router.push("/login")} /></Screen>;
  return <Screen><Title>Session History</Title><Body muted>Development analysis metadata only. Do not use as a patient record.</Body><View style={styles.filters}>{filters.map(([id, label]) => <Pressable key={id} onPress={() => setExercise(id)} style={[styles.chip, exercise === id && styles.selected]}><Text style={styles.chipText}>{label}</Text></Pressable>)}</View>{loading ? <Loading label="Loading sessions" /> : error ? <ErrorState message={error} action={<PrimaryButton title="Retry" onPress={load} />} /> : !items.length ? <EmptyState title="No saved sessions" message="Enable Save session when analyzing a video." /> : items.map((item) => <Pressable key={item.session_id} onPress={async () => { try { setDetail(await getSessionById(item.session_id)); } catch (e) { setError((e as Error).message); } }}><Card><View style={styles.row}><Heading>{item.exercise_display_name}</Heading><StatusBadge label={item.status} tone={item.status === "success" ? "success" : "warning"} /></View><Body>{item.total_reps ?? 0} reps · score {item.movement_score ?? "not scored"}</Body><Body muted>{new Date(item.created_at).toLocaleString()} · {item.analysis_confidence_level || "confidence unavailable"}</Body></Card></Pressable>)}{detail && <Card tone="blue"><Heading>Session detail</Heading><Body>{String(detail.summary || detail.message || "No saved summary.")}</Body><PrimaryButton title="Close detail" onPress={() => setDetail(null)} secondary /></Card>}</Screen>;
}
const styles = StyleSheet.create({ filters: { flexDirection: "row", flexWrap: "wrap", gap: 8 }, chip: { borderWidth: 1, borderColor: colors.border, backgroundColor: colors.card, borderRadius: 999, paddingHorizontal: 12, paddingVertical: 8 }, selected: { backgroundColor: "#DBEAFE", borderColor: colors.primary }, chipText: { color: colors.text, fontWeight: "700", fontSize: 12 }, row: { flexDirection: "row", justifyContent: "space-between", alignItems: "flex-start", gap: 8 } });
