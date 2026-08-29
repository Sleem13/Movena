import { useEffect, useState } from "react";
import { Alert, StyleSheet, Text, TextInput, View } from "react-native";
import { useLocalSearchParams, useRouter } from "expo-router";
import { AppShell, BrandHeader } from "@/src/components/AppShell";
import {
  Body,
  Card,
  EmptyState,
  ErrorState,
  Heading,
  Loading,
  PrimaryButton,
  StatusBadge,
} from "@/src/components/UI";
import {
  getToday,
  logAdherence,
  type PlanItem,
  type Today,
} from "@/src/api/care";
import { colors } from "@/src/config/theme";

export default function TodayScreen() {
  const router = useRouter();
  const { planItemId, analysisSessionId } = useLocalSearchParams<{ planItemId?: string; analysisSessionId?: string }>();
  const [data, setData] = useState<Today | null>(null);
  const [selected, setSelected] = useState<PlanItem | null>(null);
  const [painBefore, setBefore] = useState("0");
  const [painAfter, setAfter] = useState("0");
  const [difficulty, setDifficulty] = useState("1");
  const [fatigue, setFatigue] = useState("1");
  const [comment, setComment] = useState("");
  const [completionStatus, setCompletionStatus] = useState("completed");
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(true);
  const load = async () => {
    setBusy(true);
    setError("");
    try {
      setData(await getToday());
    } catch (e) {
      setError(e instanceof Error ? e.message : "Could not load your care plan.");
    } finally {
      setBusy(false);
    }
  };
  useEffect(() => {
    load();
  }, []);
  useEffect(() => {
    if (!data || !planItemId) return;
    const item = data.plan_items.find((candidate) => candidate.item_id === planItemId);
    if (!item) return;
    setSelected(item);
    setBefore(String(item.pain_before ?? 0));
    setAfter(String(item.pain_after ?? 0));
    setDifficulty(String(item.difficulty ?? 1));
    setFatigue(String(item.fatigue ?? 1));
    setComment(item.patient_comment || "");
  }, [data, planItemId]);
  const save = async () => {
    if (!selected || !data) return;
    try {
      setBusy(true);
      await logAdherence({
        plan_item_id: selected.item_id,
        scheduled_date: data.date,
        completion_status: completionStatus,
        pain_before: Number(painBefore),
        pain_after: Number(painAfter),
        difficulty: Number(difficulty),
        fatigue: Number(fatigue),
        note: comment.trim() || null,
        analysis_session_id: analysisSessionId || selected.analysis_session_id || null,
      });
      setSelected(null);
      await load();
    } catch (e) {
      setBusy(false);
      Alert.alert("Could not save", e instanceof Error ? e.message : "Please try again.");
    }
  };
  return (
    <AppShell active="today">
      <BrandHeader
        title="Today's plan"
        subtitle="Your therapist-prescribed recovery program."
      />
      {busy && !data ? <Loading label="Loading care plan" /> : null}
      {error ? (
        <ErrorState
          message={error}
          action={<PrimaryButton title="Try again" onPress={load} />}
        />
      ) : null}
      {data ? (
        <>
          <View style={styles.stats}>
            <Card tone="blue">
              <Body muted>7-day adherence</Body>
              <Text style={styles.stat}>{data.adherence_percent_7d ?? 0}%</Text>
            </Card>
            <Card>
              <Body muted>Average pain</Body>
              <Text style={styles.stat}>{data.average_pain_7d ?? "—"}/10</Text>
            </Card>
          </View>
          <Heading>{data.plan_title || "Exercises for today"}</Heading>
          {data.plan_items.length ? (
            data.plan_items.map((item) => (
              <Card key={item.item_id}>
                <View style={styles.row}>
                  <View style={styles.flex}>
                    <Heading>{item.exercise_id.replaceAll("_", " ")}</Heading>
                    <Body muted>
                      {item.sets} sets × {item.reps} reps
                      {item.duration_minutes
                        ? ` · ${item.duration_minutes} min`
                        : ""}
                      {item.rest_interval_seconds != null
                        ? ` · ${item.rest_interval_seconds}s rest`
                        : ""}
                      {item.tempo ? ` · ${item.tempo}` : ""}
                      {item.target_rom_degrees != null
                        ? ` · ROM ${item.target_rom_degrees}°`
                        : ""}
                      {item.target_score != null
                        ? ` · target ${item.target_score}/100`
                        : ""}
                    </Body>
                    {item.instructions ? (
                      <Body>{item.instructions}</Body>
                    ) : null}
                  </View>
                  {item.completion_status ? (
                    <StatusBadge
                      label={item.completion_status}
                      tone="success"
                    />
                  ) : null}
                </View>
                {!item.completion_status ? (
                  <><PrimaryButton title="Log exercise" onPress={() => { setSelected(item); setBefore(String(item.pain_before ?? 0)); setAfter(String(item.pain_after ?? 0)); setDifficulty(String(item.difficulty ?? 1)); setFatigue(String(item.fatigue ?? 1)); setComment(item.patient_comment || ""); }} />{item.requires_ai_analysis || item.requested_media_upload ? <PrimaryButton title="Open movement check" secondary onPress={() => router.push({ pathname: "/upload/[id]", params: { id: item.exercise_id, planItemId: item.item_id, scheduledDate: data.date } })} /> : null}</>
                ) : null}
              </Card>
            ))
          ) : (
            <EmptyState
              title="Rest day"
              message="No exercises are scheduled today."
            />
          )}
          <PrimaryButton
            title="Appointments"
            secondary
              onPress={() => router.push("/appointments" as never)}
          />
        </>
      ) : null}
      {selected ? (
        <Card tone="blue">
          <Heading>Exercise check-in</Heading>
          <Body>{selected.exercise_id.replaceAll("_", " ")}</Body>
          {analysisSessionId || selected.analysis_session_id ? <StatusBadge label="Movement analysis linked" tone="success" /> : null}
          <View style={styles.inputs}>
            <Field
              label="Pain before (0–10)"
              value={painBefore}
              setValue={setBefore}
            />
            <Field
              label="Pain after (0–10)"
              value={painAfter}
              setValue={setAfter}
            />
            <Field
              label="Difficulty (1–5)"
              value={difficulty}
              setValue={setDifficulty}
            />
            <Field
              label="Fatigue (1–5)"
              value={fatigue}
              setValue={setFatigue}
            />
          </View>
          <View style={styles.statuses}>{[["completed", "Completed"], ["partial", "Partial"], ["not_completed", "Not completed"]].map(([value, label]) => <PrimaryButton key={value} title={label} secondary={completionStatus !== value} onPress={() => setCompletionStatus(value)} />)}</View>
          <Text style={styles.label}>Comment for therapist</Text>
          <TextInput value={comment} onChangeText={setComment} multiline style={[styles.input, styles.comment]} />
          <PrimaryButton
            title="Save completed exercise"
            disabled={busy}
            onPress={save}
          />
          <PrimaryButton
            title="Cancel"
            secondary
            onPress={() => setSelected(null)}
          />
        </Card>
      ) : null}
    </AppShell>
  );
}
function Field({
  label,
  value,
  setValue,
}: {
  label: string;
  value: string;
  setValue: (v: string) => void;
}) {
  return (
    <View style={styles.field}>
      <Text style={styles.label}>{label}</Text>
      <TextInput
        keyboardType="number-pad"
        value={value}
        onChangeText={setValue}
        style={styles.input}
      />
    </View>
  );
}
const styles = StyleSheet.create({
  stats: { flexDirection: "row", gap: 10 },
  stat: { color: colors.text, fontSize: 25, fontWeight: "800" },
  row: { flexDirection: "row", gap: 10 },
  flex: { flex: 1, gap: 5 },
  inputs: { gap: 10 },
  statuses: { gap: 8 },
  field: { gap: 5 },
  label: { color: colors.text, fontSize: 13, fontWeight: "700" },
  input: {
    minHeight: 46,
    borderWidth: 1,
    borderColor: colors.border,
    borderRadius: 12,
    paddingHorizontal: 12,
    backgroundColor: colors.card,
    color: colors.text,
  },
  comment: { minHeight: 90, paddingVertical: 12, textAlignVertical: "top" },
});
