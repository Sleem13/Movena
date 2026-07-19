import { useRef, useState } from "react";
import { Switch, StyleSheet, Text, View } from "react-native";
import * as ImagePicker from "expo-image-picker";
import { useLocalSearchParams, useRouter } from "expo-router";
import { analyzeExercise } from "@/src/api/analysis";
import { Body, Card, PrimaryButton, SafetyNotice, Screen, Title } from "@/src/components/UI";
import { PermissionState, UploadErrorState, VideoPreviewCard } from "@/src/components/UploadStates";
import { UploadProgress } from "@/src/components/UploadProgress";
import { useAnalysis } from "@/src/context/AnalysisContext";
import { useAuth } from "@/src/context/AuthContext";
import type { MobileVideo } from "@/src/types/analysis";
import { colors } from "@/src/config/theme";
import { APP_ENV } from "@/src/config/env";
import { useExerciseMetadata } from "@/src/hooks/useExerciseMetadata";
import { canSubmitUpload, createUploadSubmissionGuard, MISSING_VIDEO_MESSAGE, STAGING_UPLOAD_AUTH_MESSAGE, validateSelectedVideo } from "@/src/utils/uploadValidation";

function toVideo(asset: ImagePicker.ImagePickerAsset): MobileVideo {
  const extension = asset.fileName?.split(".").pop()?.toLowerCase() || "mp4";
  return { uri: asset.uri, name: asset.fileName || `movement-${Date.now()}.${extension}`, type: asset.mimeType || (extension === "mov" ? "video/quicktime" : "video/mp4"), size: asset.fileSize, duration: asset.duration ?? undefined };
}

export default function UploadScreen() {
  const { id } = useLocalSearchParams<{ id: string }>();
  const router = useRouter();
  const analysis = useAnalysis();
  const { user } = useAuth();
  const { exercise: metadata } = useExerciseMetadata(id);
  const [video, setVideo] = useState<MobileVideo | null>(analysis.video);
  const [saveSession, setSaveSession] = useState(false);
  const [includeOverlay, setIncludeOverlay] = useState(false);
  const [generateReport, setGenerateReport] = useState(false);
  const [progress, setProgress] = useState(0);
  const [busy, setBusy] = useState(false);
  const [uploadError, setUploadError] = useState("");
  const [deniedPermission, setDeniedPermission] = useState<"camera" | "library" | null>(null);
  const abortRef = useRef<AbortController | null>(null);
  const submissionGuard = useRef(createUploadSubmissionGuard()).current;

  function accept(asset?: ImagePicker.ImagePickerAsset) {
    if (!asset) return;
    const selected = toVideo(asset);
    const validationError = validateSelectedVideo(selected);
    if (validationError) { setUploadError(validationError); return; }
    setVideo(selected); analysis.setVideo(selected); setUploadError(""); setDeniedPermission(null);
  }

  async function pickVideo() {
    const permission = await ImagePicker.requestMediaLibraryPermissionsAsync();
    if (!permission.granted) { setDeniedPermission("library"); setUploadError(""); return; }
    const result = await ImagePicker.launchImageLibraryAsync({ mediaTypes: ["videos"], allowsEditing: false, quality: 0.8 });
    if (!result.canceled) accept(result.assets[0]);
  }

  async function recordVideo() {
    const permission = await ImagePicker.requestCameraPermissionsAsync();
    if (!permission.granted) { setDeniedPermission("camera"); setUploadError(""); return; }
    const result = await ImagePicker.launchCameraAsync({ mediaTypes: ["videos"], videoMaxDuration: 60, quality: 0.8 });
    if (!result.canceled) accept(result.assets[0]);
  }

  async function submit() {
    if (!video) { setUploadError(MISSING_VIDEO_MESSAGE); return; }
    if (APP_ENV === "staging" && !user) { setUploadError(STAGING_UPLOAD_AUTH_MESSAGE); return; }
    if (!canSubmitUpload(video, busy) || !id) return;
    if (!submissionGuard.tryStart()) return;
    const controller = new AbortController(); abortRef.current = controller;
    setBusy(true); setProgress(0); setUploadError("");
    try {
      const result = await analyzeExercise(id, video, { saveSession: Boolean(user && saveSession), includeOverlay, generateReport, signal: controller.signal }, setProgress);
      analysis.setResult(result); router.replace("/result");
    } catch (requestError) {
      setUploadError((requestError as Error).message);
      if (APP_ENV === "development") console.warn("Mobile analysis request failed", { exerciseId: id, errorName: (requestError as Error).name });
    } finally { abortRef.current = null; submissionGuard.finish(); setBusy(false); }
  }

  const uploadDescription = `${metadata?.display_name || analysis.exercise?.display_name || id}. Videos are sent temporarily to the configured FastAPI backend.`;
  return <Screen>
    <Title>Upload movement video</Title><Body muted>{uploadDescription}</Body>
    <View style={styles.buttons}><View style={styles.flex}><PrimaryButton title="Pick Existing Video" onPress={pickVideo} secondary disabled={busy} /></View><View style={styles.flex}><PrimaryButton title="Record Video" onPress={recordVideo} secondary disabled={busy} /></View></View>
    {deniedPermission && <PermissionState kind={deniedPermission} onRetry={deniedPermission === "camera" ? recordVideo : pickVideo} />}
    {video && <VideoPreviewCard video={video} />}
    <Card><Option label="Save session" detail={user ? "Save analysis metadata to your protected history." : "Log in to enable protected session history."} value={saveSession} disabled={!user || busy} onChange={setSaveSession} /><Option label="Generate annotated overlay" detail="Temporary experimental 2D visual artifact." value={includeOverlay} disabled={busy} onChange={setIncludeOverlay} /><Option label="Generate PDF report" detail="Temporary educational session report." value={generateReport} disabled={busy} onChange={setGenerateReport} /></Card>
    {uploadError ? <UploadErrorState message={uploadError} onRetry={submit} canRetry={Boolean(video) && !busy} /> : null}
    {busy && <Card><UploadProgress progress={progress} /><PrimaryButton title="Cancel upload" onPress={() => abortRef.current?.abort()} secondary /></Card>}
    <PrimaryButton title={busy ? "Analyzing…" : "Upload and Analyze"} onPress={submit} disabled={busy} /><SafetyNotice />
  </Screen>;
}

function Option({ label, detail, value, disabled, onChange }: { label: string; detail: string; value: boolean; disabled: boolean; onChange: (value: boolean) => void }) { return <View style={styles.option}><View style={styles.optionText}><Text style={styles.label}>{label}</Text><Text style={styles.detail}>{detail}</Text></View><Switch value={value} disabled={disabled} onValueChange={onChange} trackColor={{ true: colors.teal }} /></View>; }
const styles = StyleSheet.create({ buttons: { flexDirection: "row", gap: 10 }, flex: { flex: 1 }, option: { flexDirection: "row", alignItems: "center", justifyContent: "space-between", gap: 12, paddingVertical: 5 }, optionText: { flex: 1 }, label: { color: colors.text, fontWeight: "700" }, detail: { color: colors.muted, fontSize: 12, lineHeight: 17 } });
