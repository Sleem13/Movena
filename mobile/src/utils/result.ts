import type { AnalysisResult } from "@/src/types/analysis";

export const shouldShowScore = (result: AnalysisResult) => result.status === "success" && result.movement_score != null;
export const isRejectedResult = (result: AnalysisResult) => result.status === "rejected";
export const isErrorResult = (result: AnalysisResult) => result.status === "error";
export const prettyLabel = (value = "") => value.replace(/_/g, " ").replace(/\b\w/g, (letter) => letter.toUpperCase());
export const movementScoreLabel = (result: AnalysisResult) => shouldShowScore(result) ? `${result.movement_score}/100` : "Not scored";
export const totalRepsLabel = (result: AnalysisResult) => String(result.total_reps ?? 0);

const REJECTED_TIPS: Record<string, string> = {
  bodyweight_squat: "Show the full body from a stable side or front diagonal view for 3–5 controlled repetitions.",
  sit_to_stand: "Use a stable side view with the chair and full body visible through each stand and sit cycle.",
  knee_extension: "Use a stable side view while seated, keeping the hip, knee, ankle, and lower limb visible.",
  shoulder_abduction: "Use a stable front view with the shoulder, elbow, wrist, and trunk visible; avoid trunk leaning.",
  hip_abduction: "Use a stable front view with the pelvis, hip, knee, and ankle visible; avoid trunk leaning.",
};

export const rejectedRecordingTip = (exerciseId?: string | null) => REJECTED_TIPS[exerciseId || ""] || "Keep required body parts visible, use a stable camera and good lighting, and perform controlled repetitions where appropriate.";

export function mlStatusMessage(prediction: AnalysisResult["ml_prediction"]): string | null {
  if (!prediction) return null;
  return prediction.enabled
    ? "An experimental second opinion was returned; rule-based analysis remains primary."
    : prediction.warning || "ML is not applicable for this exercise.";
}
