import { useLocalSearchParams, useRouter } from "expo-router";
import { CameraChecklist } from "@/src/components/CameraChecklist";
import { Body, Card, ErrorState, Heading, Loading, PrimaryButton, SafetyNotice, Screen, Title } from "@/src/components/UI";
import { useExerciseMetadata } from "@/src/hooks/useExerciseMetadata";

export default function CameraGuidanceScreen() {
  const { id } = useLocalSearchParams<{ id: string }>(); const router = useRouter(); const { exercise, error, loading } = useExerciseMetadata(id);
  if (loading) return <Screen><Loading label="Loading camera guidance" /></Screen>;
  if (!exercise || error) return <Screen><ErrorState message={error || "Camera guidance is unavailable."} /></Screen>;
  return <Screen><Title>Set up your camera</Title><Body muted>{exercise.display_name} · {exercise.recommended_camera_view}</Body><Card><Heading>Recording checklist</Heading><CameraChecklist exercise={exercise} /></Card><Card tone="blue"><Heading>Expected movement</Heading><Body>{exercise.expected_movement_pattern}</Body></Card><PrimaryButton title="Choose or record video" onPress={() => router.push({ pathname: "/upload/[id]", params: { id } })} /><SafetyNotice /></Screen>;
}
