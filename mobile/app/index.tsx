import { useRouter } from "expo-router";
import { View } from "react-native";
import { Body, Card, PrimaryButton, SafetyNotice, Screen, StatusBadge, Title } from "@/src/components/UI";

export default function OnboardingScreen() {
  const router = useRouter();
  return <Screen><View style={{ paddingTop: 56, gap: 16 }}><StatusBadge label="Movement monitoring MVP" tone="success" /><Title>See movement more clearly.</Title><Body muted>Choose a supported exercise, follow the recording guide, and upload a short video for backend-side rule-based analysis.</Body><Card tone="blue"><Body>No pose estimation or ML runs on this device. Manual exercise selection remains primary.</Body></Card><SafetyNotice /><PrimaryButton title="Continue" onPress={() => router.replace("/exercises")} /></View></Screen>;
}
