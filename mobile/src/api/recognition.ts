import { API_BASE_URL, API_TIMEOUT_MS } from "@/src/config/env";
import type { MobileVideo } from "@/src/types/analysis";
import type { RecognitionModelsResponse, RecognitionResult } from "@/src/types/recognition";
import { appendVideoToFormData } from "@/src/utils/mobileVideo";
import { getToken } from "@/src/utils/secureTokenStorage";
import { ApiError, apiRequest, handleAuthenticationFailure, parseApiError } from "./client";

export const getRecognitionModels = () => apiRequest<RecognitionModelsResponse>("/api/v1/recognition/models");

export function selectTemporalModel(models: RecognitionModelsResponse["models"]) {
  return models.find((model) => model.artifact_format === "torchscript_sequence" && model.active && model.integrity_status === "valid") || null;
}

export async function recognizeExerciseVideo(video: MobileVideo, onProgress?: (percent: number) => void, signal?: AbortSignal): Promise<RecognitionResult> {
  const token = await getToken();
  const form = new FormData();
  appendVideoToFormData(form, video);

  return new Promise((resolve, reject) => {
    const request = new XMLHttpRequest();
    request.open("POST", `${API_BASE_URL}/api/v1/recognition/video`);
    request.timeout = API_TIMEOUT_MS;
    request.setRequestHeader("Accept", "application/json");
    if (token) request.setRequestHeader("Authorization", `Bearer ${token}`);
    request.upload.onprogress = (event) => event.lengthComputable && onProgress?.(Math.round((event.loaded / event.total) * 100));
    request.onerror = () => reject(new ApiError("Cannot reach Movena. Confirm the backend URL and Wi-Fi connection.", "NETWORK_ERROR"));
    request.ontimeout = () => reject(new ApiError("Exercise identification timed out. Try a shorter recording.", "TIMEOUT"));
    request.onabort = () => reject(new ApiError("Identification cancelled. Your selected video is still available.", "CANCELLED"));
    signal?.addEventListener("abort", () => request.abort(), { once: true });
    request.onload = () => {
      let body: RecognitionResult | null = null;
      try { body = JSON.parse(request.responseText); } catch { /* handled below */ }
      if (request.status >= 200 && request.status < 300 && body) resolve(body);
      else {
        const error = parseApiError(body || { message: "The backend returned an unreadable response." }, request.status);
        handleAuthenticationFailure(error).finally(() => reject(error));
      }
    };
    request.send(form);
  });
}

export const confirmRecognitionSuggestion = (eventId: string, exerciseId: string) => apiRequest<{ status: string }>(
  "/api/v1/recognition/confirm",
  { method: "POST", body: JSON.stringify({ event_id: eventId, confirmed_exercise_id: exerciseId }) },
  true,
);
