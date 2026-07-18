import { StyleSheet, Text, View } from "react-native";
import type { ExerciseMetadata } from "@/src/types/exercise";
import { colors } from "@/src/config/theme";
import { Card, PrimaryButton, StatusBadge } from "./UI";

export function ExerciseCard({ exercise, onPress }: { exercise: ExerciseMetadata; onPress: () => void }) {
  return <Card><View style={styles.top}><Text style={styles.name}>{exercise.display_name}</Text><StatusBadge label={exercise.supported_in_app ? "Supported" : "Planned — not available"} tone={exercise.supported_in_app ? "success" : "muted"} /></View><Text style={styles.meta}>{exercise.body_region} · {exercise.exercise_family}</Text><Text style={styles.description}>{exercise.movement_description}</Text><Text style={styles.view}>Camera: {exercise.recommended_camera_view}</Text><PrimaryButton title={exercise.supported_in_app ? "View exercise" : "Not available"} onPress={onPress} disabled={!exercise.supported_in_app} secondary /></Card>;
}
const styles = StyleSheet.create({ top: { gap: 10 }, name: { fontSize: 20, fontWeight: "800", color: colors.text }, meta: { color: colors.teal, fontWeight: "700", fontSize: 12 }, description: { color: colors.muted, lineHeight: 21 }, view: { color: colors.text, fontWeight: "600" } });
