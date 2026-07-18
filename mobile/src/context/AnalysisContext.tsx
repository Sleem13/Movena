import { createContext, PropsWithChildren, useContext, useState } from "react";
import type { AnalysisResult, MobileVideo } from "@/src/types/analysis";
import type { ExerciseMetadata } from "@/src/types/exercise";

type State = { exercise: ExerciseMetadata | null; video: MobileVideo | null; result: AnalysisResult | null; setExercise: (value: ExerciseMetadata | null) => void; setVideo: (value: MobileVideo | null) => void; setResult: (value: AnalysisResult | null) => void };
const Context = createContext<State | null>(null);
export function AnalysisProvider({ children }: PropsWithChildren) {
  const [exercise, setExercise] = useState<ExerciseMetadata | null>(null); const [video, setVideo] = useState<MobileVideo | null>(null); const [result, setResult] = useState<AnalysisResult | null>(null);
  return <Context.Provider value={{ exercise, video, result, setExercise, setVideo, setResult }}>{children}</Context.Provider>;
}
export function useAnalysis() { const value = useContext(Context); if (!value) throw new Error("AnalysisProvider is missing"); return value; }
