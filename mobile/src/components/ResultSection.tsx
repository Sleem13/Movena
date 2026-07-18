import { StyleSheet, Text, View } from "react-native";
import { colors } from "@/src/config/theme";
import { Card, Heading } from "./UI";

export function ResultSection({ title, items }: { title: string; items?: string[] }) {
  if (!items?.length) return null;
  return <Card><Heading>{title}</Heading>{items.map((item, index) => <View key={`${item}-${index}`} style={styles.row}><Text style={styles.dot}>•</Text><Text style={styles.text}>{item}</Text></View>)}</Card>;
}
const styles = StyleSheet.create({ row: { flexDirection: "row", gap: 8 }, dot: { color: colors.teal, fontWeight: "900" }, text: { flex: 1, color: colors.text, lineHeight: 21 } });
