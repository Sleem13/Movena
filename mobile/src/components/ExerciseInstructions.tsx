import { useState } from "react";
import { Linking, Pressable, Text } from "react-native";
import type { ExerciseMetadata } from "@/src/types/exercise";
import { colors } from "@/src/config/theme";
import { Body, Card, ErrorState, Heading } from "./UI";

export function ExerciseInstructions({ exercise }: { exercise: ExerciseMetadata }) {
  const [linkError, setLinkError] = useState("");
  if (!exercise.instructions?.length) return null;
  return <Card>
    <Heading>Instructions and references</Heading>
    {exercise.instructions.map((step, index) => <Body key={step}>{index + 1}. {step}</Body>)}
    <Body>{exercise.dosage_guidance}</Body>
    {exercise.reference_note ? <Body muted>{exercise.reference_note}</Body> : null}
    {exercise.source_urls?.map((url, index) => <Pressable key={url} accessibilityRole="link" accessibilityLabel={`Open exercise reference ${index + 1}`} style={{ minHeight: 44, justifyContent: "center", paddingVertical: 10 }} onPress={async () => {
      setLinkError("");
      try { await Linking.openURL(url); } catch { setLinkError("Could not open the reference. Please try again."); }
    }}><Text style={{ color: colors.primary, textDecorationLine: "underline" }}>Exercise reference {index + 1}: {new URL(url).hostname}</Text></Pressable>)}
    {linkError ? <ErrorState message={linkError} /> : null}
  </Card>;
}
