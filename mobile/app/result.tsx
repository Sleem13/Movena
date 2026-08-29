import { Linking, StyleSheet, Text, View } from "react-native";
import { useLocalSearchParams, useRouter } from "expo-router";
import { absoluteApiUrl } from "@/src/api/client";
import { Body, Card, EmptyState, Heading, PrimaryButton, SafetyNotice, Screen, StatusBadge, Title } from "@/src/components/UI";
import { ResultSection } from "@/src/components/ResultSection";
import { useAnalysis } from "@/src/context/AnalysisContext";
import {
  isErrorResult,
  isRejectedResult,
  mlStatusMessage,
  movementScoreLabel,
  prettyLabel,
  rejectedRecordingTip,
  totalRepsLabel,
} from "@/src/utils/result";
import { colors } from "@/src/config/theme";

const percent = (value?: number | null) => value == null ? "Not available" : `${Math.round(value * 100)}%`;

export default function ResultScreen() {
  const router = useRouter();
  const { planItemId, scheduledDate } = useLocalSearchParams<{ planItemId?: string; scheduledDate?: string }>();
  const { result, exercise, setResult, setVideo } = useAnalysis();
  if (!result) return <Screen><EmptyState title="No analysis result" message="Choose a supported exercise and upload a video first." /><PrimaryButton title="Exercise Library" onPress={() => router.replace("/exercises")} /></Screen>;

  const reportUrl = absoluteApiUrl(result.report_download_url);
  const overlayUrl = absoluteApiUrl(result.overlay_preview_url || result.overlay_download_url);
  const retry = () => {
    setResult(null);
    const id = exercise?.exercise_id || result.exercise_id || result.exercise;
    router.replace({ pathname: "/upload/[id]", params: { id, ...(planItemId ? { planItemId, scheduledDate: scheduledDate || "" } : {}) } });
  };
  const restart = () => { setResult(null); setVideo(null); router.replace("/exercises"); };

  if (isRejectedResult(result)) {
    const exerciseId = exercise?.exercise_id || result.exercise_id || result.exercise;
    return <Screen>
      <StatusBadge label="Rejected — not scored" tone="warning" />
      <Title>No valid {exercise?.display_name?.toLowerCase() || "movement"} detected</Title>
      <Card tone="warning"><Heading>{result.message || "The recording could not be scored."}</Heading><Body>No movement score is shown because the input was invalid or insufficient.</Body></Card>
      <ResultSection title="Why this was rejected" items={result.validation_warnings} />
      <Card tone="blue"><Heading>Try recording again</Heading><Body>{rejectedRecordingTip(exerciseId)}</Body></Card>
      <ResultSection title="Feedback" items={result.feedback} />
      <ResultSection title="Limitations" items={result.limitations} />
      <PrimaryButton title="Try Again" onPress={retry} />
      <PrimaryButton title="Known Limitations" onPress={() => router.push("/limitations")} secondary />
      <PrimaryButton title="Exercise Library" onPress={restart} secondary />
      <SafetyNotice />
    </Screen>;
  }

  if (isErrorResult(result)) return <Screen><StatusBadge label="Analysis error" tone="warning" /><Title>Analysis did not complete</Title><Card tone="warning"><Heading>{result.message || "The recording could not be processed."}</Heading><Body>No movement score is shown. Your exercise and selected video are still available to retry.</Body></Card><PrimaryButton title="Try Again" onPress={retry} /><PrimaryButton title="Exercise Library" onPress={restart} secondary /><SafetyNotice /></Screen>;

  return <Screen>
    <StatusBadge label={prettyLabel(result.status)} tone="success" />
    <Title>{exercise?.display_name || result.exercise_name || prettyLabel(result.exercise)} result</Title>
    <View style={styles.metrics}>
      <Metric label="Reps" value={totalRepsLabel(result)} />
      <Metric label="Movement score" value={movementScoreLabel(result)} />
      <Metric label="Analysis confidence" value={result.analysis_confidence?.level ? `${prettyLabel(result.analysis_confidence.level)} · ${percent(result.analysis_confidence.score)}` : "Not available"} />
      <Metric label="Pose quality" value={result.pose_quality?.level ? `${prettyLabel(result.pose_quality.level)} · ${percent(result.pose_quality.score)}` : "Not available"} />
      <Metric label="Rep confidence" value={percent(result.rep_count_confidence)} />
    </View>
    <ResultSection title="Observed movement patterns" items={result.detected_issues?.map(prettyLabel)} />
    <ResultSection title="Feedback" items={result.feedback} />
    <ResultSection title="Limitations" items={result.limitations} />
    {result.ml_prediction && <Card tone="warning"><Heading>Experimental ML status</Heading><Body>{mlStatusMessage(result.ml_prediction)}</Body></Card>}
    {reportUrl && <PrimaryButton title="Open PDF report" onPress={() => Linking.openURL(reportUrl)} secondary />}
    {overlayUrl && <PrimaryButton title="Open annotated video" onPress={() => Linking.openURL(overlayUrl)} secondary />}
    {planItemId && result.session_id ? <PrimaryButton title="Continue exercise check-in" onPress={() => router.replace({ pathname: "/today", params: { planItemId, scheduledDate: scheduledDate || "", analysisSessionId: result.session_id || "" } } as never)} /> : null}
    <PrimaryButton title="Known Limitations" onPress={() => router.push("/limitations")} secondary />
    <PrimaryButton title="Analyze another exercise" onPress={restart} />
    <SafetyNotice />
  </Screen>;
}

function Metric({ label, value }: { label: string; value: string }) {
  return <Card><Text style={styles.label}>{label}</Text><Text style={styles.value}>{value}</Text></Card>;
}

const styles = StyleSheet.create({
  metrics: { gap: 10 },
  label: { color: colors.muted, fontSize: 12, fontWeight: "700", textTransform: "uppercase" },
  value: { color: colors.text, fontWeight: "800", fontSize: 22 },
});
