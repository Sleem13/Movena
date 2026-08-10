import { Pressable, StyleSheet, Text, View } from "react-native";
import Ionicons from "@expo/vector-icons/Ionicons";
import type { ExerciseMetadata } from "@/src/types/exercise";
import { colors } from "@/src/config/theme";

export function ExerciseCard({ exercise, onPress }: { exercise: ExerciseMetadata; onPress: () => void }) {
  return <Pressable accessibilityRole="button" accessibilityState={{ disabled: !exercise.supported_in_app }} disabled={!exercise.supported_in_app} onPress={onPress} style={({ pressed }) => [styles.card, !exercise.supported_in_app && styles.disabled, pressed && styles.pressed]}>
    <View style={styles.icon}><Ionicons name={exercise.supported_in_app ? "fitness-outline" : "lock-closed-outline"} size={25} color={exercise.supported_in_app ? colors.primary : colors.muted} /></View>
    <View style={styles.content}><View style={styles.top}><Text style={styles.name}>{exercise.display_name}</Text><Text style={[styles.status, exercise.supported_in_app && styles.available]}>{exercise.supported_in_app ? "Available" : "Coming later"}</Text></View><Text style={styles.meta}>{exercise.body_region} · {exercise.exercise_family}</Text><Text numberOfLines={2} style={styles.description}>{exercise.movement_description}</Text></View>
    <Ionicons name="chevron-forward" size={20} color={exercise.supported_in_app ? colors.text : colors.muted} />
  </Pressable>;
}
const styles = StyleSheet.create({ card: { minHeight: 112, borderWidth: 1, borderColor: colors.border, borderRadius: 18, padding: 14, flexDirection: "row", alignItems: "center", gap: 12, backgroundColor: colors.card }, icon: { width: 48, height: 48, borderRadius: 15, backgroundColor: colors.paleBlue, alignItems: "center", justifyContent: "center" }, content: { flex: 1, gap: 4 }, top: { gap: 3 }, name: { fontSize: 17, fontWeight: "800", color: colors.text }, status: { color: colors.muted, fontSize: 11, fontWeight: "700" }, available: { color: colors.teal }, meta: { color: colors.teal, fontWeight: "700", fontSize: 11, textTransform: "capitalize" }, description: { color: colors.muted, fontSize: 12, lineHeight: 17 }, disabled: { opacity: 0.62 }, pressed: { opacity: 0.68, transform: [{ scale: 0.99 }] } });
