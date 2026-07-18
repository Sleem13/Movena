import { StyleSheet, Text, View } from "react-native";
import type { MobileVideo } from "@/src/types/analysis";
import { colors } from "@/src/config/theme";
import { Body, Card, Heading, PrimaryButton } from "./UI";

export function PermissionState({ kind, onRetry }: { kind: "camera" | "library"; onRetry: () => void }) {
  return <Card tone="warning"><Heading>{kind === "camera" ? "Camera" : "Photo library"} permission denied</Heading><Body>Enable access in device settings, then retry. PhysioVision AI only uses the selected recording for the requested analysis.</Body><PrimaryButton title="Retry permission" onPress={onRetry} secondary /></Card>;
}

export function VideoPreviewCard({ video }: { video: MobileVideo }) {
  const size = video.size == null ? "File size unavailable" : `${(video.size / 1024 / 1024).toFixed(1)} MB`;
  const duration = video.duration == null ? "Duration unavailable" : `${Math.max(1, Math.round(video.duration / 1000))} sec`;
  return <Card tone="blue"><Heading>Selected video</Heading><Text numberOfLines={2} style={styles.name}>{video.name}</Text><View style={styles.metadata}><Text style={styles.meta}>{size}</Text><Text style={styles.meta}>{duration}</Text><Text style={styles.meta}>{video.type}</Text></View><Body muted>This file stays selected after an upload failure so you can retry.</Body></Card>;
}

export function UploadRetryButton({ onRetry, disabled = false }: { onRetry: () => void; disabled?: boolean }) {
  return <PrimaryButton title="Retry upload" onPress={onRetry} disabled={disabled} secondary />;
}

export function UploadErrorState({ message, onRetry, canRetry }: { message: string; onRetry: () => void; canRetry: boolean }) {
  return <Card tone="warning"><Heading>Upload did not complete</Heading><Body>{message}</Body>{canRetry && <UploadRetryButton onRetry={onRetry} />}</Card>;
}

const styles = StyleSheet.create({
  name: { color: colors.text, fontSize: 16, fontWeight: "700" },
  metadata: { flexDirection: "row", flexWrap: "wrap", gap: 8 },
  meta: { color: colors.muted, backgroundColor: colors.card, borderRadius: 999, paddingHorizontal: 9, paddingVertical: 4, fontSize: 12 },
});
