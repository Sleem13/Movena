import { useEffect, useState } from "react";
import { getExerciseById } from "@/src/api/exercises";
import type { ExerciseMetadata } from "@/src/types/exercise";
import { useAnalysis } from "@/src/context/AnalysisContext";

export function useExerciseMetadata(exerciseId?: string) {
  const analysis = useAnalysis();
  const [exercise, setExercise] = useState<ExerciseMetadata | null>(analysis.exercise?.exercise_id === exerciseId ? analysis.exercise : null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(!exercise);
  useEffect(() => {
    if (!exerciseId || exercise?.exercise_id === exerciseId) return;
    setLoading(true); getExerciseById(exerciseId).then((item) => { setExercise(item); analysis.setExercise(item); }).catch((requestError) => setError(requestError.message)).finally(() => setLoading(false));
  }, [exerciseId]);
  return { exercise, error, loading };
}
