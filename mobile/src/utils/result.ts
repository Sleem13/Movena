import type { AnalysisResult } from "@/src/types/analysis";

export const shouldShowScore = (result: AnalysisResult) => result.status === "success" && result.movement_score != null;
export const isRejectedResult = (result: AnalysisResult) => result.status === "rejected";
export const isErrorResult = (result: AnalysisResult) => result.status === "error";
export const prettyLabel = (value = "") => value.replace(/_/g, " ").replace(/\b\w/g, (letter) => letter.toUpperCase());
