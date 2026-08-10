import { StyleSheet, Text, View } from "react-native";
import type { ExerciseMetadata } from "@/src/types/exercise";
import { colors } from "@/src/config/theme";

const EXERCISE_GUIDANCE: Record<string, string[]> = {
  bodyweight_squat: [
    "Keep the full body visible",
    "Use a side or front diagonal view",
    "Perform 3–5 controlled repetitions",
  ],
  sit_to_stand: [
    "Use a side view when possible",
    "Keep the chair and full body visible",
    "Show a controlled stand and sit cycle",
  ],
  knee_extension: [
    "Use a side view when possible",
    "Keep the hip, knee, and ankle visible",
    "Stay seated and avoid hiding the lower limb",
  ],
  shoulder_abduction: [
    "Use a front view when possible",
    "Keep the shoulder, elbow, wrist, and trunk visible",
    "Raise the arm out to the side and avoid trunk leaning",
  ],
  hip_abduction: [
    "Use a front view when possible",
    "Keep the pelvis, hip, knee, and ankle visible",
    "Move the leg away from the body and avoid trunk leaning",
  ],
  push_up: [
    "Use a stable side view",
    "Keep shoulders, hips, and ankles visible",
    "Show controlled lowering and return phases",
  ],
  shoulder_press: [
    "Use a stable front view",
    "Keep shoulders, elbows, wrists, and trunk visible",
    "Use only an approved load or unloaded practice",
  ],
  bicep_curl: [
    "Use a stable front or slight side view",
    "Keep shoulder, elbow, wrist, and trunk visible",
    "Show the arm extending, flexing, and extending again",
  ],
};

export function buildCameraGuidance(exercise: ExerciseMetadata): string[] {
  return [
    "Keep coaches, spotters, and bystanders outside the frame — analyze one person only",
    ...(EXERCISE_GUIDANCE[exercise.exercise_id] || [`Keep ${exercise.required_landmarks.join(", ")} visible`]),
    "Keep the camera stable",
    "Use good, even lighting",
    "Avoid loose clothing that hides required joints",
    "Stop if pain, dizziness, or unusual symptoms occur",
  ];
}

export function CameraChecklist({ exercise }: { exercise: ExerciseMetadata }) {
  return <View accessibilityLabel="Recording checklist" style={styles.list}>{buildCameraGuidance(exercise).map((item) => <View key={item} style={styles.item}><Text style={styles.check}>✓</Text><Text style={styles.text}>{item}</Text></View>)}</View>;
}

const styles = StyleSheet.create({
  list: { gap: 12 },
  item: { flexDirection: "row", gap: 10, alignItems: "flex-start" },
  check: { color: colors.teal, fontWeight: "900", fontSize: 17 },
  text: { flex: 1, color: colors.text, lineHeight: 21 },
});
