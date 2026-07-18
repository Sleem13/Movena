import axios from "axios";
import { API_BASE_URL } from "../config/apiConfig";

export { API_BASE_URL };

const api = axios.create({
  baseURL: API_BASE_URL,
});

api.interceptors?.request.use((config) => {
  const token = typeof localStorage !== "undefined" ? localStorage.getItem("physiovision_access_token") : null;
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

export async function analyzeExerciseVideo(exerciseId, videoFile, options = {}, onProgress) {
  const formData = new FormData();
  formData.append("video", videoFile);

  const query = new URLSearchParams({
    include_overlay: String(Boolean(options.include_overlay)),
    generate_report: String(Boolean(options.generate_report)),
    include_ml: String(Boolean(options.include_ml)),
    include_frame_data: String(Boolean(options.include_frame_data)),
    save_session: String(Boolean(options.save_session)),
  });

  const endpoint = {
    bodyweight_squat: "squat",
    sit_to_stand: "sit-to-stand",
    knee_extension: "knee-extension",
    shoulder_abduction: "shoulder-abduction",
    hip_abduction: "hip-abduction",
  }[exerciseId];
  if (!endpoint) throw new Error(`Unsupported exercise: ${exerciseId}`);
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

export function analyzeKneeExtensionVideo(videoFile, options = {}, onProgress) {
  return analyzeExerciseVideo("knee_extension", videoFile, options, onProgress);
}

export function analyzeShoulderAbductionVideo(videoFile, options = {}, onProgress) {
  return analyzeExerciseVideo("shoulder_abduction", videoFile, options, onProgress);
}

export function analyzeHipAbductionVideo(videoFile, options = {}, onProgress) {
  return analyzeExerciseVideo("hip_abduction", videoFile, options, onProgress);
}

export function artifactUrl(path) {
  return path ? new URL(path, API_BASE_URL).toString() : null;
}

export async function getExercises() {
  return (await api.get("/api/v1/exercises")).data;
}

export async function getExercise(exerciseId) {
  return (await api.get(`/api/v1/exercises/${exerciseId}`)).data;
}

export async function listSavedSessions(params = {}) {
  const response = await api.get("/api/v1/sessions", { params });
  return response.data;
}

export async function getSavedSession(sessionId) {
  const response = await api.get(`/api/v1/sessions/${sessionId}`);
  return response.data;
}

export async function deleteSavedSession(sessionId) {
  const response = await api.delete(`/api/v1/sessions/${sessionId}`);
  return response.data;
}

export async function getTherapistDashboard() {
  return (await api.get("/api/v1/therapist/dashboard")).data;
}

export async function listPatientProfiles() {
  return (await api.get("/api/v1/therapist/patients")).data;
}

export async function createPatientProfile(payload) {
  return (await api.post("/api/v1/therapist/patients", payload)).data;
}

export async function getPatientProfile(patientId) {
  return (await api.get(`/api/v1/therapist/patients/${patientId}`)).data;
}

export async function listPatientSessions(patientId) {
  return (await api.get(`/api/v1/therapist/patients/${patientId}/sessions`)).data;
}

export async function getPatientProgress(patientId) {
  return (await api.get(`/api/v1/therapist/patients/${patientId}/progress`)).data;
}

export async function registerUser(payload) { return (await api.post("/api/v1/auth/register", payload)).data; }
export async function loginUser(payload) { return (await api.post("/api/v1/auth/login", payload)).data; }
export async function getCurrentUser() { return (await api.get("/api/v1/auth/me")).data; }
export async function logoutUser() { return (await api.post("/api/v1/auth/logout")).data; }

export default api;
