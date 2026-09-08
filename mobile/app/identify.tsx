import { useEffect, useMemo, useRef, useState } from "react";
import { Pressable, StyleSheet, Text, View } from "react-native";
import Ionicons from "@expo/vector-icons/Ionicons";
import * as ImagePicker from "expo-image-picker";
import { useRouter } from "expo-router";

import { confirmRecognitionSuggestion, getRecognitionModels, recognizeExerciseVideo, selectTemporalModel } from "@/src/api/recognition";
import { getExerciseById } from "@/src/api/exercises";
import { AppShell, BrandHeader } from "@/src/components/AppShell";
import { ActionRow, AnalysisSteps, SectionTitle } from "@/src/components/GuidedUI";
import { Body, Card, ErrorState, Heading, Loading, PrimaryButton } from "@/src/components/UI";
import { PermissionState, VideoPreviewCard } from "@/src/components/UploadStates";
import { UploadProgress } from "@/src/components/UploadProgress";
import { colors } from "@/src/config/theme";
import { useAnalysis } from "@/src/context/AnalysisContext";
import type { MobileVideo } from "@/src/types/analysis";
import { toMobileVideo } from "@/src/utils/mobileVideo";
import type { RecognitionModelsResponse, RecognitionResult } from "@/src/types/recognition";
import { validateSelectedVideo } from "@/src/utils/uploadValidation";
import { buildRecognitionHandoff } from "@/src/utils/recognitionHandoff";

const percent = (value?: number) => `${Math.round((value || 0) * 100)}%`;

export default function IdentifyExerciseScreen() {
  const router = useRouter(); const analysis = useAnalysis();
  const [models, setModels] = useState<RecognitionModelsResponse | null>(null); const [video, setVideo] = useState<MobileVideo | null>(null); const [result, setResult] = useState<RecognitionResult | null>(null);
  const [loadingModels, setLoadingModels] = useState(true); const [busy, setBusy] = useState(false); const [confirming, setConfirming] = useState(false); const [progress, setProgress] = useState(0); const [error, setError] = useState(""); const [deniedPermission, setDeniedPermission] = useState<"camera" | "library" | null>(null);
  const abortRef = useRef<AbortController | null>(null); const temporalModel = useMemo(() => selectTemporalModel(models?.models || []), [models]);
  const uncertain = result?.status === "uncertain"; const hasSuggestion = Boolean(result?.suggested_exercise_id);
  useEffect(() => { let cancelled = false; getRecognitionModels().then((response) => { if (!cancelled) setModels(response); }).catch((requestError) => { if (!cancelled) setError((requestError as Error).message); }).finally(() => { if (!cancelled) setLoadingModels(false); }); return () => { cancelled = true; abortRef.current?.abort(); }; }, []);
  function accept(asset?: ImagePicker.ImagePickerAsset) { if (!asset) return; const selected = toMobileVideo(asset); const validationError = validateSelectedVideo(selected); if (validationError) { setError(validationError); return; } setVideo(selected); setResult(null); setProgress(0); setError(""); setDeniedPermission(null); }
  async function pickVideo() { const permission = await ImagePicker.requestMediaLibraryPermissionsAsync(); if (!permission.granted) { setDeniedPermission("library"); return; } const selection = await ImagePicker.launchImageLibraryAsync({ mediaTypes: ["videos"], allowsEditing: false, quality: 0.8 }); if (!selection.canceled) accept(selection.assets[0]); }
  async function recordVideo() { const permission = await ImagePicker.requestCameraPermissionsAsync(); if (!permission.granted) { setDeniedPermission("camera"); return; } const selection = await ImagePicker.launchCameraAsync({ mediaTypes: ["videos"], videoMaxDuration: 60, quality: 0.8 }); if (!selection.canceled) accept(selection.assets[0]); }
  async function identify() { if (!video || !temporalModel || busy) return; const controller = new AbortController(); abortRef.current = controller; setBusy(true); setProgress(0); setError(""); setResult(null); try { setResult(await recognizeExerciseVideo(video, setProgress, controller.signal)); } catch (requestError) { setError((requestError as Error).message); } finally { abortRef.current = null; setBusy(false); } }
  async function confirm() { if (!video || !result?.suggested_exercise_id || uncertain || confirming) return; setConfirming(true); setError(""); try { const exercise = await getExerciseById(result.suggested_exercise_id); if (!exercise.supported_in_app) throw new Error("This exercise does not have an available analyzer yet."); if (result.recognition_event_id) await confirmRecognitionSuggestion(result.recognition_event_id, exercise.exercise_id); const handoff = buildRecognitionHandoff(exercise, video); analysis.setExercise(handoff.exercise); analysis.setVideo(handoff.video); analysis.setResult(null); router.replace(handoff.route); } catch (requestError) { setError((requestError as Error).message); } finally { setConfirming(false); } }

  return <AppShell active="coach">
    <BrandHeader title="Movement coach" subtitle="Add a short exercise video for a guided Movena movement check." />
    <AnalysisSteps active={video ? (result ? 3 : 2) : 1} />
    {!video ? <>
      <SectionTitle>How would you like to add your video?</SectionTitle>
      <ActionRow title="Record a video" detail="Use your phone camera" icon="videocam-outline" primary onPress={recordVideo} disabled={busy || loadingModels || !temporalModel} />
      <ActionRow title="Choose from phone" detail="Select an existing clip" icon="images-outline" onPress={pickVideo} disabled={busy || loadingModels || !temporalModel} />
      <Pressable accessibilityRole="button" onPress={() => router.push("/exercises")} style={({ pressed }) => [styles.manual, pressed && styles.pressed]}><View style={styles.manualIcon}><Ionicons name="fitness-outline" size={24} color={colors.teal} /></View><View style={styles.flex}><Text style={styles.manualTitle}>Choose the exercise manually</Text><Text style={styles.manualDetail}>Browse supported movements first</Text></View><Ionicons name="chevron-forward" size={20} color={colors.text} /></Pressable>
      <View style={styles.guidance}><Ionicons name="scan-outline" size={24} color={colors.teal} /><Text style={styles.guidanceText}>Keep one person fully visible</Text></View>
    </> : <>
      <SectionTitle>Your video</SectionTitle><VideoPreviewCard video={video} />
      {!result && !busy ? <ActionRow title="Identify the exercise" detail="We’ll suggest the movement from this clip" icon="scan-outline" primary onPress={identify} disabled={!temporalModel} /> : null}
      {!busy ? <Pressable onPress={() => { setVideo(null); setResult(null); setError(""); }} style={styles.change}><Ionicons name="refresh-outline" size={18} color={colors.primary} /><Text style={styles.changeText}>Choose a different video</Text></Pressable> : null}
    </>}
    {loadingModels ? <Loading label="Preparing video recognition" /> : !temporalModel ? <ErrorState message="Video identification is temporarily unavailable. Choose an exercise manually instead." action={<PrimaryButton title="Choose exercise" onPress={() => router.replace("/exercises")} secondary />} /> : null}
    {deniedPermission ? <PermissionState kind={deniedPermission} onRetry={deniedPermission === "camera" ? recordVideo : pickVideo} /> : null}
    {busy ? <Card><Heading>Identifying your exercise</Heading><UploadProgress progress={progress} /><PrimaryButton title="Cancel" onPress={() => abortRef.current?.abort()} secondary /></Card> : null}
    {error ? <ErrorState message={error} /> : null}
    {result ? <Card tone="blue"><Text style={styles.suggestionLabel}>Suggested exercise</Text><Heading>{result.suggested_exercise_id?.replaceAll("_", " ") || "No confident suggestion"}</Heading><Body muted>Confidence {percent(result.confidence)}</Body>
      {!hasSuggestion || uncertain ? <Body>We’re not confident enough to choose for you. Try a clearer clip or choose manually.</Body> : result.analyzer_available === false ? <Body>This movement does not have an analyzer yet.</Body> : <PrimaryButton title={confirming ? "Confirming…" : "Confirm and continue"} onPress={confirm} disabled={confirming} />}
      <PrimaryButton title="Choose manually" onPress={() => router.replace("/exercises")} secondary disabled={confirming} />
    </Card> : null}
  </AppShell>;
}

const styles = StyleSheet.create({ manual: { minHeight: 76, flexDirection: "row", alignItems: "center", gap: 12, paddingVertical: 8 }, manualIcon: { width: 48, height: 48, borderRadius: 15, backgroundColor: colors.paleTeal, alignItems: "center", justifyContent: "center" }, flex: { flex: 1 }, manualTitle: { color: colors.text, fontSize: 15, fontWeight: "800" }, manualDetail: { color: colors.muted, fontSize: 12, marginTop: 3 }, guidance: { minHeight: 58, paddingHorizontal: 16, borderRadius: 16, backgroundColor: colors.paleTeal, flexDirection: "row", alignItems: "center", gap: 12 }, guidanceText: { color: colors.teal, fontSize: 14, fontWeight: "800" }, change: { minHeight: 44, flexDirection: "row", alignItems: "center", justifyContent: "center", gap: 7 }, changeText: { color: colors.primary, fontWeight: "800", fontSize: 13 }, suggestionLabel: { color: colors.primary, fontSize: 12, fontWeight: "800", textTransform: "uppercase", letterSpacing: 0.7 }, pressed: { opacity: 0.65 } });
