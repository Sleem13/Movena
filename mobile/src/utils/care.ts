import type { PlanItem } from "@/src/api/care";

export const isTherapist = (role?: string) => role === "therapist";
export const homeRoute = (role?: string) => isTherapist(role) ? "/patients" : "/today";
export const exerciseName = (id: string) => id.replaceAll("_", " ").replace(/^\w/, (letter) => letter.toUpperCase());
export const initials = (name: string) => name.trim().split(/\s+/).slice(0, 2).map((part) => part[0]).join("").toUpperCase();
export function localDay() {
  const date = new Date();
  return `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, "0")}-${String(date.getDate()).padStart(2, "0")}`;
}
export const calendarDate = (value: string) => new Date(`${value}T12:00:00`);
export const linkedAnalysisForItem = (routeItemId: string | undefined, routeSessionId: string | undefined, item: Pick<PlanItem, "item_id" | "analysis_session_id">) =>
  (routeItemId === item.item_id ? routeSessionId : null) || item.analysis_session_id || null;
export function reviewCountFromResults<T extends Pick<PlanItem, "clinician_review_required" | "reviewed_at">>(results: PromiseSettledResult<T[]>[]) {
  if (results.some((result) => result.status === "rejected")) return null;
  return results.flatMap((result) => result.status === "fulfilled" ? result.value : []).filter(needsReview).length;
}
export function optionalScore(value: string, label: string, min: number, max: number) {
  if (!value.trim()) return null;
  const number = Number(value);
  if (!Number.isInteger(number) || number < min || number > max) throw new Error(`${label} must be a whole number from ${min} to ${max}.`);
  return number;
}
export const needsReview = (item: Pick<PlanItem, "clinician_review_required" | "reviewed_at">) => Boolean(item.clinician_review_required && !item.reviewed_at);
export const completionLabel = (status?: string | null) => ({ completed: "Completed", partial: "Partly completed", not_completed: "Not completed" }[status || ""] || "Not checked in");

export const symptomOptions = [
  ["pain_increase", "Increased pain"], ["dizziness", "Dizziness"], ["faintness", "Feeling faint"],
  ["unusual_shortness_of_breath", "Unusual shortness of breath"], ["chest_discomfort", "Chest discomfort"],
  ["new_numbness_or_weakness", "New numbness or weakness"], ["instability", "Instability"], ["other", "Other symptoms"],
] as const;
