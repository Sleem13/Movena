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
    continue_on_subject_warning: String(Boolean(options.continue_on_subject_warning)),
    save_session: String(Boolean(options.save_session)),
  });

  if (options.patient_id) query.set("patient_id", options.patient_id);

  const delay = (milliseconds) => new Promise((resolve, reject) => {
    const finish = () => {
      options.signal?.removeEventListener("abort", abort);
      resolve();
    };
    const timeout = setTimeout(finish, milliseconds);
    const abort = () => {
      clearTimeout(timeout);
      options.signal?.removeEventListener("abort", abort);
      const error = new Error("Analysis cancelled.");
      error.name = "CanceledError";
      error.code = "ERR_CANCELED";
      reject(error);
    };
    if (options.signal?.aborted) abort();
    else options.signal?.addEventListener("abort", abort, { once: true });
  });
  let jobId;
  try {
    const submitted = await api.post(`/api/v1/analysis-jobs/${encodeURIComponent(exerciseId)}?${query}`, formData, {
      headers: { "Content-Type": "multipart/form-data" },
      onUploadProgress: (event) => {
        if (onProgress && event.total) onProgress(Math.round((event.loaded * 20) / event.total));
      },
      signal: options.signal,
    });
    jobId = submitted.data.job_id;
    onProgress?.(Math.max(20, submitted.data.progress || 0));

    let pollFailures = 0;
    for (let attempt = 0; attempt < 1200; attempt += 1) {
      let job;
      try {
        ({ data: job } = await api.get(`/api/v1/analysis-jobs/${jobId}`, { signal: options.signal }));
        pollFailures = 0;
      } catch (error) {
        if (options.signal?.aborted || error?.code === "ERR_CANCELED") throw error;
        const transient = !error?.response || error.response.status >= 500;
        if (!transient || pollFailures >= 4) throw error;
        pollFailures += 1;
        await delay(750 * pollFailures);
        continue;
      }
      onProgress?.(Math.max(20, Math.min(100, 20 + Math.round((job.progress || 0) * 0.8))));
      if (job.status === "completed") return job.result;
      if (job.status === "failed") {
        const error = new Error(job.message || "Analysis failed.");
        error.response = {
          status: job.http_status || 500,
          data: job.result || { error_code: job.error_code, message: job.message },
        };
        throw error;
      }
      if (job.status === "cancelled") {
        const error = new Error("Analysis cancelled.");
        error.name = "CanceledError";
        error.code = "ERR_CANCELED";
        throw error;
      }
      await delay(750);
    }
    throw new Error("Analysis is taking longer than expected. You can safely return to this page later.");
  } catch (error) {
    if (jobId && (options.signal?.aborted || error?.code === "ERR_CANCELED")) {
      await api.post(`/api/v1/analysis-jobs/${jobId}/cancel`).catch(() => undefined);
    }
    throw error;
  }
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

export function analyzeShoulderFlexionVideo(videoFile, options = {}, onProgress) {
  return analyzeExerciseVideo("shoulder_flexion", videoFile, options, onProgress);
}

export function analyzeHipAbductionVideo(videoFile, options = {}, onProgress) {
  return analyzeExerciseVideo("hip_abduction", videoFile, options, onProgress);
}

export function analyzeGaitVideo(videoFile, options = {}, onProgress) {
  return analyzeExerciseVideo("walking_gait_screen", videoFile, options, onProgress);
}

export function analyzeBalanceVideo(videoFile, options = {}, onProgress) {
  return analyzeExerciseVideo("balance", videoFile, options, onProgress);
}

export function artifactUrl(path) {
  return path ? new URL(path, API_BASE_URL).toString() : null;
}

export async function getExercises() {
  return (await api.get("/api/v1/exercises")).data;
}

export async function getRehabRlOverview() {
  return (await api.get("/api/v1/rehab-rl/overview")).data;
}

export async function createRehabRlAssessment(payload) {
  return (await api.post("/api/v1/rehab-rl/assessment", payload)).data;
}

export async function simulateRehabRlTrajectory(payload) {
  return (await api.post("/api/v1/rehab-rl/simulate", payload)).data;
}

export async function getRehabRlExercises() {
  return (await api.get("/api/v1/rehab-rl/exercises")).data;
}

export async function getRehabRlInspector() {
  return (await api.get("/api/v1/rehab-rl/inspector")).data;
}

export async function getRehabRlTrainingStatus() {
  return (await api.get("/api/v1/rehab-rl/training")).data;
}

export async function startRehabRlTraining(payload) {
  return (await api.post("/api/v1/rehab-rl/training", payload)).data;
}

export async function restoreRehabRlCheckpoint() {
  return (await api.post("/api/v1/rehab-rl/checkpoints/restore")).data;
}

export async function getExercise(exerciseId) {
  return (await api.get(`/api/v1/exercises/${exerciseId}`)).data;
}

export async function getRecognitionModels() {
  return (await api.get("/api/v1/recognition/models")).data;
}

export async function getCoachingReadiness() {
  return (await api.get("/api/v1/coaching/readiness")).data;
}

export async function recognizeExerciseVideo(videoFile, onProgress, options = {}) {
  const formData = new FormData();
  formData.append("video", videoFile);
  const query = new URLSearchParams({
    continue_on_subject_warning: String(Boolean(options.continue_on_subject_warning)),
  });
  const response = await api.post(`/api/v1/recognition/video?${query}`, formData, {
    headers: { "Content-Type": "multipart/form-data" },
    onUploadProgress: (event) => {
      if (onProgress && event.total) onProgress(Math.round((event.loaded * 100) / event.total));
    },
  });
  return response.data;
}

export async function confirmRecognitionSuggestion(eventId, exerciseId) {
  return (await api.post("/api/v1/recognition/confirm", {
    event_id: eventId,
    confirmed_exercise_id: exerciseId,
  })).data;
}

export async function listSavedSessions(params = {}) {
  const response = await api.get("/api/v1/sessions", { params });
  return response.data;
}

export async function getSavedSession(sessionId) {
  const response = await api.get(`/api/v1/sessions/${sessionId}`);
  return response.data;
}

export async function getArtifactBlob(path) {
  const response = await api.get(path, { responseType: "blob" });
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

export async function getPatientToday(day) {
  return (await api.get("/api/v1/patient/today", { params: day ? { day } : {} })).data;
}

export async function recordPatientAdherence(payload, idempotencyKey = crypto.randomUUID()) {
  return (await api.post("/api/v1/patient/adherence", payload, { headers: { "Idempotency-Key": idempotencyKey } })).data;
}

export async function listPatientAppointments() {
  return (await api.get("/api/v1/patient/appointments")).data;
}

export async function joinAppointment(appointmentId) {
  return (await api.get(`/api/v1/scheduling/appointments/${encodeURIComponent(appointmentId)}/join`)).data;
}

export async function listPatientNotifications() {
  return (await api.get("/api/v1/patient/notifications")).data;
}

export async function markPatientNotificationRead(notificationId) {
  return (await api.post(`/api/v1/patient/notifications/${encodeURIComponent(notificationId)}/read`)).data;
}

export async function listCatalog() {
  const [services, packages] = await Promise.all([
    api.get("/api/v1/catalog/services"), api.get("/api/v1/catalog/packages"),
  ]);
  return { services: services.data, packages: packages.data };
}

export async function startCheckout(payload, idempotencyKey = crypto.randomUUID()) {
  return (await api.post("/api/v1/checkout", payload, { headers: { "Idempotency-Key": idempotencyKey } })).data;
}

export async function listTherapistAppointments() {
  return (await api.get("/api/v1/therapist/appointments")).data;
}

export async function listTherapistAdherenceAlerts() {
  return (await api.get("/api/v1/therapist/adherence-alerts")).data;
}
export async function listPatientAdherence(patientId, params = {}) {
  return (await api.get(`/api/v1/therapist/patients/${patientId}/adherence`, { params })).data;
}

export async function listPatientExercisePlans(patientId) {
  return (await api.get(`/api/v1/therapist/patients/${patientId}/exercise-plans`)).data;
}

export async function createPatientExercisePlan(patientId, payload) {
  return (await api.post(`/api/v1/therapist/patients/${patientId}/exercise-plans`, payload)).data;
}

export async function updatePatientExercisePlanStatus(patientId, planId, status) {
  return (await api.patch(`/api/v1/therapist/patients/${patientId}/exercise-plans/${planId}`, { status })).data;
}

export async function registerUser(payload) { return (await api.post("/api/v1/auth/register", payload)).data; }
export async function loginUser(payload) { return (await api.post("/api/v1/auth/login", payload)).data; }
export async function getCurrentUser() { return (await api.get("/api/v1/auth/me")).data; }
export async function logoutUser() { return (await api.post("/api/v1/auth/logout")).data; }
export async function verifyEmailToken(token) { return (await api.post("/api/v1/auth/verify-email", { token })).data; }
export async function resendVerificationEmail(email) { return (await api.post("/api/v1/auth/resend-verification", { email })).data; }
export async function requestPasswordReset(email) { return (await api.post("/api/v1/auth/forgot-password", { email })).data; }
export async function submitPasswordReset(token, newPassword) { return (await api.post("/api/v1/auth/reset-password", { token, new_password: newPassword })).data; }

export async function listManagedUsers(params = {}) { return (await api.get("/api/v1/admin/users", { params })).data; }
export async function getAdminWorkflow() { return (await api.get("/api/v1/admin/workflow")).data; }
export async function createManagedUser(payload) { return (await api.post("/api/v1/admin/users", payload)).data; }
export async function getManagedUser(userId) { return (await api.get(`/api/v1/admin/users/${userId}`)).data; }
export async function updateManagedUserStatus(userId, status, reason) {
  return (await api.patch(`/api/v1/admin/users/${userId}/status`, { status, reason })).data;
}
export async function updateManagedUserRole(userId, role, reason) {
  return (await api.patch(`/api/v1/admin/users/${userId}/role`, { role, reason })).data;
}
export async function resetManagedUserPassword(userId, newPassword, reason) {
  return (await api.post(`/api/v1/admin/users/${userId}/password`, { new_password: newPassword, reason })).data;
}
export async function deleteManagedUser(userId, reason) {
  return (await api.delete(`/api/v1/admin/users/${userId}`, { params: { reason } })).data;
}

export default api;
