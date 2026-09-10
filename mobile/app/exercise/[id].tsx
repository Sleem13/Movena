import { ExerciseInstructions } from "@/src/components/ExerciseInstructions";
import { useLocalSearchParams, useRouter } from "expo-router";
import { Body, Card, ErrorState, Heading, Loading, PrimaryButton, SafetyNotice, Screen, StatusBadge, Title } from "@/src/components/UI";
import { useExerciseMetadata } from "@/src/hooks/useExerciseMetadata";

export default function ExerciseDetailScreen() {
  const { id } = useLocalSearchParams<{ id: string }>(); const router = useRouter(); const { exercise, error, loading } = useExerciseMetadata(id);
  if (loading) return <Screen><Loading label="Loading exercise" /></Screen>;
  if (!exercise || error) return <Screen><ErrorState message={error || "Exercise metadata is unavailable."} /></Screen>;
  if (!exercise.supported_in_app) return <Screen>
    <StatusBadge label={exercise.guidance_available ? "Exercise guide · no AI analysis" : "Analysis unavailable"} />
    <Title>{exercise.display_name}</Title><Body muted>{exercise.body_region} · {exercise.exercise_family}</Body>
    <ExerciseInstructions exercise={exercise} />
    <Card tone="warning"><Heading>Precautions</Heading><Body>{exercise.safety_notes}</Body><Body>Stop for sharp pain, dizziness, or new symptoms and seek advice. Follow your care team's restrictions after injury or surgery.</Body></Card>
    <PrimaryButton title="Back to exercise library" onPress={() => router.push("/exercises")} secondary />
  </Screen>;
  return <Screen><StatusBadge label="Supported" tone="success" /><Title>{exercise.display_name}</Title><Body muted>{exercise.body_region} · {exercise.exercise_family}</Body><Card><Heading>Movement</Heading><Body>{exercise.movement_description}</Body><Body>{exercise.expected_movement_pattern}</Body></Card><ExerciseInstructions exercise={exercise} /><Card tone="blue"><Heading>Recommended camera view</Heading><Body>{exercise.recommended_camera_view}</Body><Heading>Keep visible</Heading><Body>{exercise.required_landmarks.join(", ")}</Body></Card><Card tone="warning"><Heading>Safety note</Heading><Body>{exercise.safety_notes}</Body></Card><PrimaryButton title="Start Analysis" onPress={() => router.push({ pathname: "/guidance/[id]", params: { id } })} /><SafetyNotice /></Screen>;
}
