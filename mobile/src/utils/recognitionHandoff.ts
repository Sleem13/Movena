import type { MobileVideo } from "@/src/types/analysis";
import type { ExerciseMetadata } from "@/src/types/exercise";

export function buildRecognitionHandoff(exercise: ExerciseMetadata, video: MobileVideo) {
  return {
    exercise,
    video,
    route: { pathname: "/upload/[id]" as const, params: { id: exercise.exercise_id, source: "recognition" } },
  };
}
