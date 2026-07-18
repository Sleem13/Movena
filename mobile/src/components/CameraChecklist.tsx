import { StyleSheet, Text, View } from "react-native";
import type { ExerciseMetadata } from "@/src/types/exercise";
import { colors } from "@/src/config/theme";

export function buildCameraGuidance(exercise: ExerciseMetadata): string[] {
  return [`Keep ${exercise.required_landmarks.join(", ")} visible`, "Keep the camera stable", "Use good, even lighting", "Perform 3–5 controlled repetitions where appropriate", "Avoid loose clothing that hides required joints", "Stop if pain, dizziness, or unusual symptoms occur"];
}

export function CameraChecklist({ exercise }: { exercise: ExerciseMetadata }) {
  return <View accessibilityLabel="Recording checklist" style={styles.list}>{buildCameraGuidance(exercise).map((item) => <View key={item} style={styles.item}><Text style={styles.check}>✓</Text><Text style={styles.text}>{item}</Text></View>)}</View>;
}
const styles = StyleSheet.create({ list: { gap: 12 }, item: { flexDirection: "row", gap: 10, alignItems: "flex-start" }, check: { color: colors.teal, fontWeight: "900", fontSize: 17 }, text: { flex: 1, color: colors.text, lineHeight: 21 } });
