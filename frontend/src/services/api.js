import axios from "axios";

export const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000";

const api = axios.create({
  baseURL: API_BASE_URL,
});

export async function analyzeExerciseVideo(exerciseId, videoFile, options = {}, onProgress) {
  const formData = new FormData();
  formData.append("video", videoFile);

  const query = new URLSearchParams({
    include_overlay: String(Boolean(options.include_overlay)),
    generate_report: String(Boolean(options.generate_report)),
    include_ml: String(Boolean(options.include_ml)),
    include_frame_data: String(Boolean(options.include_frame_data)),
  });

  const endpoint = exerciseId === "sit_to_stand" ? "sit-to-stand" : "squat";
  const response = await api.post(`/api/v1/analyze/${endpoint}?${query}`, formData, {
    headers: {
      "Content-Type": "multipart/form-data",
    },
    onUploadProgress: (event) => {
      if (onProgress && event.total) onProgress(Math.round((event.loaded * 100) / event.total));
    },
  });

  return response.data;
}

export function analyzeSquatVideo(videoFile, options = {}, onProgress) {
  return analyzeExerciseVideo("bodyweight_squat", videoFile, options, onProgress);
}

export function analyzeSitToStandVideo(videoFile, options = {}, onProgress) {
  return analyzeExerciseVideo("sit_to_stand", videoFile, options, onProgress);
}

export function artifactUrl(path) {
  return path ? new URL(path, API_BASE_URL).toString() : null;
}

export default api;
