import { useCallback, useEffect, useState } from "react";
import { Pressable, StyleSheet, Text, View } from "react-native";
import { useFocusEffect, useRouter } from "expo-router";
import { getExercises } from "@/src/api/exercises";
import { ExerciseCard } from "@/src/components/ExerciseCard";
import { Body, ErrorState, Loading, PrimaryButton, SafetyNotice, Screen, Title } from "@/src/components/UI";
import type { ExerciseMetadata } from "@/src/types/exercise";
import { useAnalysis } from "@/src/context/AnalysisContext";
import { useAuth } from "@/src/context/AuthContext";
import { colors } from "@/src/config/theme";

export default function ExerciseLibraryScreen() {
  const router = useRouter();
  const analysis = useAnalysis();
  const { sessionMessage, clearSessionMessage } = useAuth();
  const [items, setItems] = useState<ExerciseMetadata[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const load = useCallback(() => {
    setLoading(true);
    setError("");
    getExercises().then(setItems).catch((requestError) => setError(requestError.message)).finally(() => setLoading(false));
  }, []);

  useEffect(load, []);
  useFocusEffect(useCallback(() => {
    analysis.setVideo(null);
    analysis.setResult(null);
  }, []));

  const open = (item: ExerciseMetadata) => {
    if (!item.supported_in_app) return;
    analysis.setExercise(item);
    router.push({ pathname: "/exercise/[id]", params: { id: item.exercise_id } });
  };

  return (
    <Screen>
      <Title>Exercise Library</Title>
      <Body muted>Select the movement shown in your recording. Planned exercises are visible but cannot be analyzed.</Body>
      {sessionMessage ? <ErrorState message={sessionMessage} action={<PrimaryButton title="Dismiss" onPress={clearSessionMessage} secondary />} /> : null}
      <View style={styles.nav}>
        <Pressable onPress={() => router.push("/history")}><Text style={styles.link}>History</Text></Pressable>
        <Pressable onPress={() => router.push("/profile")}><Text style={styles.link}>Profile</Text></Pressable>
        <Pressable onPress={() => router.push("/safety")}><Text style={styles.link}>Safety</Text></Pressable>
      </View>
      {loading ? <Loading label="Loading exercises" /> : error ? (
        <ErrorState message={error} action={<PrimaryButton title="Retry" onPress={load} />} />
      ) : <>
        <Text style={styles.section}>Supported</Text>
        {items.filter((item) => item.supported_in_app).map((item) => <ExerciseCard key={item.exercise_id} exercise={item} onPress={() => open(item)} />)}
        <Text style={styles.section}>Planned</Text>
        {items.filter((item) => !item.supported_in_app).map((item) => <ExerciseCard key={item.exercise_id} exercise={item} onPress={() => {}} />)}
      </>}
      <SafetyNotice />
    </Screen>
  );
}

const styles = StyleSheet.create({
  nav: { flexDirection: "row", gap: 20 },
  link: { color: colors.primary, fontWeight: "700" },
  section: { marginTop: 8, fontSize: 20, fontWeight: "800", color: colors.text },
});
