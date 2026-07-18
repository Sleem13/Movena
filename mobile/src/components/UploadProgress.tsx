import { StyleSheet, Text, View } from "react-native";
import { colors } from "@/src/config/theme";

export function UploadProgress({ progress }: { progress: number }) {
  return <View accessibilityLabel={`Upload progress ${progress} percent`}><View style={styles.track}><View style={[styles.bar, { width: `${Math.max(2, progress)}%` }]} /></View><Text style={styles.text}>{progress < 100 ? `Uploading ${progress}%` : "Upload complete — analyzing movement"}</Text></View>;
}
const styles = StyleSheet.create({ track: { height: 9, borderRadius: 99, overflow: "hidden", backgroundColor: colors.border }, bar: { height: "100%", backgroundColor: colors.teal }, text: { marginTop: 8, color: colors.muted, fontSize: 13 } });
