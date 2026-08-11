import { API_BASE_URL, API_TIMEOUT_MS } from "@/src/config/env";
import type { AnalysisOptions, AnalysisResult, MobileVideo } from "@/src/types/analysis";
import { appendVideoToFormData } from "@/src/utils/mobileVideo";
import { getToken } from "@/src/utils/secureTokenStorage";
import { ApiError, handleAuthenticationFailure, parseApiError } from "./client";

export const ANALYSIS_ENDPOINTS: Record<string, string> = {
  bodyweight_squat: "/api/v1/analyze/squat",
  sit_to_stand: "/api/v1/analyze/sit-to-stand",
  knee_extension: "/api/v1/analyze/knee-extension",
  shoulder_abduction: "/api/v1/analyze/shoulder-abduction",
  hip_abduction: "/api/v1/analyze/hip-abduction",
  push_up: "/api/v1/analyze/push-up",
  shoulder_press: "/api/v1/analyze/shoulder-press",
  bicep_curl: "/api/v1/analyze/bicep-curl",
};

export function getAnalysisEndpoint(exerciseId: string): string {
  const endpoint = ANALYSIS_ENDPOINTS[exerciseId];
  if (!endpoint) throw new ApiError("This exercise is planned and cannot be analyzed yet.", "EXERCISE_NOT_SUPPORTED");
  return endpoint;
}

export async function analyzeExercise(exerciseId: string, video: MobileVideo, options: AnalysisOptions = {}, onProgress?: (percent: number) => void): Promise<AnalysisResult> {
  const endpoint = getAnalysisEndpoint(exerciseId);
  const query = new URLSearchParams({
    save_session: String(Boolean(options.saveSession)),
    include_overlay: String(Boolean(options.includeOverlay)),
    generate_report: String(Boolean(options.generateReport)),
    include_ml: "false",
    include_frame_data: "false",
  });
  if (options.patientId) query.set("patient_id", options.patientId);
  const token = await getToken();
  const form = new FormData();
  appendVideoToFormData(form, video);

  return new Promise((resolve, reject) => {
    const request = new XMLHttpRequest();
    request.open("POST", `${API_BASE_URL}${endpoint}?${query.toString()}`);
    request.timeout = API_TIMEOUT_MS;
    request.setRequestHeader("Accept", "application/json");
    if (token) request.setRequestHeader("Authorization", `Bearer ${token}`);
    request.upload.onprogress = (event) => event.lengthComputable && onProgress?.(Math.round((event.loaded / event.total) * 100));
    request.onerror = () => reject(new ApiError("Cannot reach PhysioVision AI. Confirm the backend URL and Wi-Fi connection.", "NETWORK_ERROR"));
    request.ontimeout = () => reject(new ApiError("Video analysis timed out. Try a shorter recording.", "TIMEOUT"));
    request.onabort = () => reject(new ApiError("Upload cancelled. Your selected video is still available to retry.", "CANCELLED"));
    const abort = () => request.abort();
    options.signal?.addEventListener("abort", abort, { once: true });
    request.onload = () => {
      let body: AnalysisResult | null = null;
      try { body = JSON.parse(request.responseText); } catch { /* handled below */ }
      if (request.status >= 200 && request.status < 300 && body) resolve(body);
      else {
        const error = parseApiError(body ? {
        error_code: typeof body.error_code === "string" ? body.error_code : undefined,
        message: typeof body.message === "string" ? body.message : undefined,
        } : { message: "The backend returned an unreadable response." }, request.status);
        handleAuthenticationFailure(error).finally(() => reject(error));
      }
    };
    request.send(form);
  });
}
