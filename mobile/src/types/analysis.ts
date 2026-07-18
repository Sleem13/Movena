export type Confidence = { score?: number; level?: string; warnings?: string[] };
export type PoseQuality = Confidence & { pose_detection_rate?: number; average_visibility?: number };
export type MLPrediction = { enabled?: boolean; predicted_label?: string | null; confidence?: number | null; warning?: string; model_version?: string };

export type AnalysisResult = {
  exercise: string;
  exercise_id?: string | null;
  exercise_name?: string | null;
  status: "success" | "rejected" | "error" | "not_available" | string;
  error_code?: string | null;
  message?: string | null;
  total_reps?: number;
  movement_score?: number | null;
  analysis_confidence?: Confidence | null;
  pose_quality?: PoseQuality | null;
  rep_count_confidence?: number | null;
  detected_issues?: string[];
  feedback?: string[];
  limitations?: string[];
  validation_warnings?: string[];
  score_breakdown?: Record<string, number | null> | null;
  report_download_url?: string | null;
  overlay_preview_url?: string | null;
  overlay_download_url?: string | null;
  ml_prediction?: MLPrediction | null;
  session_id?: string | null;
  [key: string]: unknown;
};

export type MobileVideo = { uri: string; name: string; type: string; size?: number; duration?: number };
export type AnalysisOptions = { saveSession?: boolean; patientId?: string; includeOverlay?: boolean; generateReport?: boolean; signal?: AbortSignal };
