import { Pressable, StyleSheet, Text, View } from "react-native";
import Ionicons from "@expo/vector-icons/Ionicons";
import type { PlanItem } from "@/src/api/care";
import { colors } from "@/src/config/theme";
import { completionLabel, exerciseName } from "@/src/utils/care";
import { Body, PrimaryButton, StatusBadge } from "./UI";

type Props = {
  item: PlanItem;
  index: number;
  expanded: boolean;
  disabled?: boolean;
  onToggle: () => void;
  onCheckIn: () => void;
  onMovementCheck: () => void;
};

export function CarePlanItem({ item, index, expanded, disabled = false, onToggle, onCheckIn, onMovementCheck }: Props) {
  const checkedIn = Boolean(item.completion_status);
  const movementRequested = Boolean(item.requires_ai_analysis || item.requested_media_upload);
  return <View style={[styles.item, expanded && styles.expanded]}>
    <Pressable accessibilityRole="button" accessibilityState={{ expanded }} accessibilityLabel={`${exerciseName(item.exercise_id)}, ${checkedIn ? completionLabel(item.completion_status) : "not checked in"}`} onPress={onToggle} style={({ pressed }) => [styles.summary, pressed && styles.pressed]}>
      <View style={[styles.number, checkedIn && styles.numberChecked]}>{checkedIn ? <Ionicons name="checkmark" size={20} color="#FFFFFF" /> : <Text style={styles.numberText}>{index + 1}</Text>}</View>
      <View style={styles.copy}>
        <Text style={styles.title}>{exerciseName(item.exercise_id)}</Text>
        <Text style={styles.meta}>{checkedIn ? completionLabel(item.completion_status) : `${item.sets} sets × ${item.reps} reps${item.duration_minutes ? ` · ${item.duration_minutes} min` : ""}`}</Text>
      </View>
      <Ionicons name={expanded ? "chevron-up" : "chevron-down"} size={20} color={colors.muted} />
    </Pressable>
    {expanded ? <View style={styles.details}>
      {item.plan_title || item.created_by_name ? <Body muted>{[item.plan_title, item.created_by_name ? `From ${item.created_by_name}` : null].filter(Boolean).join(" · ")}</Body> : null}
      <View style={styles.factGrid}>
        <Fact label="Dosage" value={`${item.sets} sets × ${item.reps} reps${item.duration_minutes ? ` · ${item.duration_minutes} min` : ""}`} />
        <Fact label="Rest" value={item.rest_interval_seconds == null ? "Not specified" : `${item.rest_interval_seconds} seconds`} />
        <Fact label="Tempo" value={item.tempo || "Not specified"} />
        {item.target_rom_degrees != null ? <Fact label="Target range" value={`${item.target_rom_degrees}°`} /> : null}
      </View>
      {item.instructions ? <View style={styles.guidance}><Text style={styles.label}>Instructions</Text><Body>{item.instructions}</Body></View> : null}
      {item.precautions ? <View style={styles.precaution}><Ionicons name="warning-outline" size={20} color="#9B681C" /><View style={styles.copy}><Text style={styles.label}>Precaution</Text><Body>{item.precautions}</Body></View></View> : null}
      {checkedIn ? <StatusBadge label={item.clinician_review_required && !item.reviewed_at ? "Waiting for therapist review" : completionLabel(item.completion_status)} tone={item.clinician_review_required && !item.reviewed_at ? "warning" : "success"} /> : <PrimaryButton title="Check in" disabled={disabled} onPress={onCheckIn} />}
      {movementRequested && !checkedIn ? <PrimaryButton title="Movement check" secondary disabled={disabled} onPress={onMovementCheck} /> : null}
    </View> : null}
  </View>;
}

function Fact({ label, value }: { label: string; value: string }) {
  return <View style={styles.fact}><Text style={styles.label}>{label}</Text><Text style={styles.factValue}>{value}</Text></View>;
}

const styles = StyleSheet.create({
  item: { backgroundColor: colors.card, borderWidth: 1, borderColor: colors.border, borderRadius: 14, overflow: "hidden" },
  expanded: { borderColor: "#C9D9FA" }, summary: { minHeight: 76, flexDirection: "row", alignItems: "center", gap: 12, paddingHorizontal: 14, paddingVertical: 12 },
  number: { width: 40, height: 40, borderRadius: 20, borderWidth: 1, borderColor: colors.border, alignItems: "center", justifyContent: "center", backgroundColor: colors.card },
  numberChecked: { backgroundColor: colors.teal, borderColor: colors.teal }, numberText: { color: colors.text, fontWeight: "800" },
  copy: { flex: 1, minWidth: 0, gap: 3 }, title: { color: colors.text, fontSize: 16, lineHeight: 22, fontWeight: "800" }, meta: { color: colors.muted, fontSize: 13, lineHeight: 19 },
  details: { gap: 14, paddingHorizontal: 16, paddingBottom: 16, borderTopWidth: 1, borderTopColor: colors.border, paddingTop: 15, backgroundColor: "#FFFEFB" },
  factGrid: { gap: 9 }, fact: { flexDirection: "row", gap: 12 }, label: { width: 92, color: colors.text, fontSize: 13, lineHeight: 20, fontWeight: "800" }, factValue: { flex: 1, color: colors.muted, fontSize: 14, lineHeight: 20 },
  guidance: { gap: 5 }, precaution: { flexDirection: "row", gap: 10, padding: 12, borderRadius: 12, backgroundColor: colors.paleAmber }, pressed: { opacity: 0.7 },
});
