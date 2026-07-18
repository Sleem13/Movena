import { apiRequest } from "./client";
import type { ExerciseMetadata } from "@/src/types/exercise";

export const getExercises = () => apiRequest<ExerciseMetadata[]>("/api/v1/exercises");
export const getExerciseById = (exerciseId: string) => apiRequest<ExerciseMetadata>(`/api/v1/exercises/${encodeURIComponent(exerciseId)}`);
