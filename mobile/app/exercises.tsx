import { useCallback, useEffect, useMemo, useState } from "react";
import { Pressable, StyleSheet, Text, View } from "react-native";
import Ionicons from "@expo/vector-icons/Ionicons";
import { useFocusEffect, useRouter } from "expo-router";

import { getExercises } from "@/src/api/exercises";
import { AppShell, BrandHeader } from "@/src/components/AppShell";
import { ExerciseCard } from "@/src/components/ExerciseCard";
import { ErrorState, Loading, PrimaryButton } from "@/src/components/UI";
import { colors } from "@/src/config/theme";
import { useAnalysis } from "@/src/context/AnalysisContext";
import { useAuth } from "@/src/context/AuthContext";
import type { ExerciseMetadata } from "@/src/types/exercise";

export default function ExerciseLibraryScreen() {
  const router = useRouter(); const analysis = useAnalysis(); const { sessionMessage, clearSessionMessage } = useAuth();
  const [items, setItems] = useState<ExerciseMetadata[]>([]); const [loading, setLoading] = useState(true); const [error, setError] = useState(""); const [filter, setFilter] = useState<"available" | "all">("available");
  const load = useCallback(() => { setLoading(true); setError(""); getExercises().then(setItems).catch((requestError) => setError(requestError.message)).finally(() => setLoading(false)); }, []);
  useEffect(load, [load]);
  useFocusEffect(useCallback(() => { analysis.setVideo(null); analysis.setResult(null); }, [analysis]));
  const visibleItems = useMemo(() => filter === "available" ? items.filter((item) => item.supported_in_app) : items, [filter, items]);
  const open = (item: ExerciseMetadata) => { analysis.setExercise(item); router.push({ pathname: "/exercise/[id]", params: { id: item.exercise_id } }); };
  return <AppShell active="coach">
    <BrandHeader title="Exercise library" subtitle="Explore supported exercises or open a PhysioVision movement check." />
    <Pressable accessibilityRole="button" onPress={() => router.push("/identify")} style={({ pressed }) => [styles.identify, pressed && styles.pressed]}><View style={styles.identifyIcon}><Ionicons name="scan-outline" size={25} color={colors.primary} /></View><View style={styles.flex}><Text style={styles.identifyTitle}>Not sure which exercise?</Text><Text style={styles.identifyText}>Identify it from a short video</Text></View><Ionicons name="chevron-forward" size={20} color={colors.primary} /></Pressable>
    {sessionMessage ? <ErrorState message={sessionMessage} action={<PrimaryButton title="Dismiss" onPress={clearSessionMessage} secondary />} /> : null}
    <View style={styles.segment}><Pressable onPress={() => setFilter("available")} style={[styles.segmentButton, filter === "available" && styles.segmentSelected]}><Text style={[styles.segmentText, filter === "available" && styles.segmentTextSelected]}>Available</Text></Pressable><Pressable onPress={() => setFilter("all")} style={[styles.segmentButton, filter === "all" && styles.segmentSelected]}><Text style={[styles.segmentText, filter === "all" && styles.segmentTextSelected]}>All exercises</Text></Pressable></View>
    {loading ? <Loading label="Loading exercises" /> : error ? <ErrorState message={error} action={<PrimaryButton title="Retry" onPress={load} />} /> : <View style={styles.list}>{visibleItems.map((item) => <ExerciseCard key={item.exercise_id} exercise={item} onPress={() => open(item)} />)}</View>}
  </AppShell>;
}

const styles = StyleSheet.create({ identify: { minHeight: 78, borderRadius: 18, backgroundColor: colors.paleBlue, padding: 14, flexDirection: "row", alignItems: "center", gap: 12 }, identifyIcon: { width: 44, height: 44, borderRadius: 14, backgroundColor: colors.card, alignItems: "center", justifyContent: "center" }, flex: { flex: 1 }, identifyTitle: { color: colors.text, fontSize: 15, fontWeight: "800" }, identifyText: { color: colors.muted, fontSize: 12, marginTop: 3 }, segment: { flexDirection: "row", padding: 4, borderRadius: 14, backgroundColor: colors.surface }, segmentButton: { flex: 1, minHeight: 40, borderRadius: 11, alignItems: "center", justifyContent: "center" }, segmentSelected: { backgroundColor: colors.card, elevation: 2 }, segmentText: { color: colors.muted, fontSize: 13, fontWeight: "700" }, segmentTextSelected: { color: colors.text }, list: { gap: 10 }, pressed: { opacity: 0.68 } });
