import { apiRequest } from "./client";

export type SessionSummary = { session_id: string; exercise_id: string; exercise_display_name: string; status: string; created_at: string; total_reps?: number | null; movement_score?: number | null; analysis_confidence_level?: string | null };
export type SessionList = { items: SessionSummary[]; total: number; limit: number; offset: number };

export const getSessions = (exerciseId?: string) => apiRequest<SessionList>(`/api/v1/sessions${exerciseId ? `?exercise_id=${encodeURIComponent(exerciseId)}` : ""}`, {}, true);
export const getSessionById = (sessionId: string) => apiRequest<Record<string, unknown>>(`/api/v1/sessions/${encodeURIComponent(sessionId)}`, {}, true);
