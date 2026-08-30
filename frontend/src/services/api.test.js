import { beforeEach, describe, expect, it, vi } from "vitest";

const mocks = vi.hoisted(() => {
  const get = vi.fn();
  const post = vi.fn();
  const patch = vi.fn();
  const put = vi.fn();
  const del = vi.fn();
  const use = vi.fn();
  return {
    get,
    post,
    patch, put,
    use,
    create: vi.fn(() => ({ get, post, patch, put, delete: del, interceptors: { request: { use } } })),
  };
});

vi.mock("axios", () => ({ default: { create: mocks.create } }));

import {
  API_BASE_URL,
  analyzeExerciseVideo,
  artifactUrl,
  getTherapistDashboard,
  getAdminWorkflow,
  getRehabRlGovernance,
  getRecoveryCoachingDashboard,
  getRecoveryCoachingTemplates,
  createRecoveryCoachingCheckIn,
  acknowledgeRecoveryCoachingCheckIn,
  updateRecoveryCoachingReminderPreference,
  listPatientAdherence,
  listSavedSessions,
  recognizeExerciseVideo,
  confirmRecognitionSuggestion,
  verifyEmailToken,
  resendVerificationEmail,
  requestPasswordReset,
  submitPasswordReset,
} from "./api.js";

describe("deployment API configuration", () => {
  beforeEach(() => { mocks.get.mockReset(); mocks.post.mockReset(); });

  it("configures the shared client and artifact URLs from one API base", () => {
    expect(mocks.create).toHaveBeenCalledWith({ baseURL: API_BASE_URL });
    expect(artifactUrl("/api/v1/artifacts/reports/id")).toBe(
      new URL("/api/v1/artifacts/reports/id", API_BASE_URL).toString(),
    );
  });

  it("uses the shared client for session and therapist endpoints", async () => {
    mocks.get.mockResolvedValue({ data: { items: [] } });
    await listSavedSessions();
    await getTherapistDashboard();
    expect(mocks.get).toHaveBeenNthCalledWith(1, "/api/v1/sessions", { params: {} });
    expect(mocks.get).toHaveBeenNthCalledWith(2, "/api/v1/therapist/dashboard");
  });

  it("attaches the development bearer token", () => {
    localStorage.setItem("physiovision_access_token", "token-123");
    const interceptor = mocks.use.mock.calls[0][0];
    expect(interceptor({ headers: {} }).headers.Authorization).toBe("Bearer token-123");
    localStorage.clear();
  });

  it.each([
    "push_up",
    "shoulder_press",
    "bicep_curl",
    "hammer_curl",
    "shoulder_flexion",
    "walking_gait_screen",
    "balance",
  ])("routes %s through its durable analysis job", async (exerciseId) => {
    mocks.post.mockResolvedValue({ data: { job_id: "job-1", status: "queued", progress: 5 } });
    mocks.get.mockResolvedValue({ data: { job_id: "job-1", status: "completed", progress: 100, result: { exercise_id: exerciseId } } });
    await analyzeExerciseVideo(exerciseId, new File(["video"], "movement.mp4", { type: "video/mp4" }));
    expect(mocks.post.mock.calls[0][0]).toContain(`/api/v1/analysis-jobs/${exerciseId}?`);
    expect(mocks.get).toHaveBeenCalledWith("/api/v1/analysis-jobs/job-1", { signal: undefined });
  });

  it("loads the super admin workflow snapshot", async () => {
    mocks.get.mockResolvedValue({ data: { stages: [] } });
    await getAdminWorkflow();
    expect(mocks.get).toHaveBeenCalledWith("/api/v1/admin/workflow");
  });

  it("loads the bounded RehabRL governance window", async () => {
    mocks.get.mockResolvedValue({ data: { decisions: 0 } });
    await getRehabRlGovernance(90);
    expect(mocks.get).toHaveBeenCalledWith("/api/v1/rehab-rl/governance?days=90");
  });

  it("scopes recovery coaching records to the selected patient", async () => {
    mocks.get.mockResolvedValue({ data: { goals: [] } });
    mocks.post.mockResolvedValue({ data: { coaching_state: "ready" } });
    mocks.put.mockResolvedValue({ data: { enabled: true } });
    await getRecoveryCoachingDashboard("patient-1");
    await getRecoveryCoachingTemplates();
    await createRecoveryCoachingCheckIn({ energy: 3 }, "patient-1");
    await acknowledgeRecoveryCoachingCheckIn("check-in-1", { clinician_attestation: true }, "patient-1");
    await updateRecoveryCoachingReminderPreference({ enabled: true }, "patient-1");
    expect(mocks.get).toHaveBeenCalledWith(
      "/api/v1/recovery-coaching/dashboard",
      { params: { patient_id: "patient-1" } },
    );
    expect(mocks.post).toHaveBeenCalledWith(
      "/api/v1/recovery-coaching/check-ins",
      { energy: 3 },
      { params: { patient_id: "patient-1" } },
    );
    expect(mocks.get).toHaveBeenCalledWith("/api/v1/recovery-coaching/templates");
    expect(mocks.post).toHaveBeenCalledWith(
      "/api/v1/recovery-coaching/check-ins/check-in-1/acknowledge",
      { clinician_attestation: true },
      { params: { patient_id: "patient-1" } },
    );
    expect(mocks.put).toHaveBeenCalledWith(
      "/api/v1/recovery-coaching/reminder-preference",
      { enabled: true },
      { params: { patient_id: "patient-1" } },
    );
  });

  it("loads assignment-scoped patient adherence for therapist review", async () => {
    mocks.get.mockResolvedValue({ data: [] });
    await listPatientAdherence("patient-1");
    expect(mocks.get).toHaveBeenCalledWith(
      "/api/v1/therapist/patients/patient-1/adherence",
      { params: {} },
    );
  });

  it("sends the subject-warning override only when requested", async () => {
    mocks.post.mockResolvedValue({ data: { job_id: "job-1", status: "queued", progress: 5 } });
    mocks.get.mockResolvedValue({ data: { status: "completed", progress: 100, result: { exercise_id: "walking_gait_screen" } } });
    await analyzeExerciseVideo("walking_gait_screen", new File(["video"], "gait.mp4", { type: "video/mp4" }), {
      continue_on_subject_warning: true,
    });
    expect(mocks.post.mock.calls[0][0]).toContain("continue_on_subject_warning=true");
  });

  it("forwards an abort signal to the analysis upload", async () => {
    mocks.post.mockResolvedValue({ data: { job_id: "job-1", status: "queued", progress: 5 } });
    mocks.get.mockResolvedValue({ data: { status: "completed", progress: 100, result: { exercise_id: "push_up" } } });
    const controller = new AbortController();
    await analyzeExerciseVideo("push_up", new File(["video"], "push-up.mp4", { type: "video/mp4" }), {
      signal: controller.signal,
    });
    expect(mocks.post.mock.calls[0][2]).toEqual(expect.objectContaining({ signal: controller.signal }));
  });

  it("reports worker progress while polling", async () => {
    mocks.post.mockResolvedValue({ data: { job_id: "job-1", status: "queued", progress: 5 } });
    mocks.get.mockResolvedValue({ data: { status: "completed", progress: 100, result: { exercise_id: "push_up" } } });
    const onProgress = vi.fn();
    await analyzeExerciseVideo("push_up", new File(["video"], "push-up.mp4", { type: "video/mp4" }), {}, onProgress);
    expect(onProgress).toHaveBeenCalledWith(100);
  });

  it("cancels the durable backend job when the client aborts", async () => {
    const controller = new AbortController();
    mocks.post.mockResolvedValue({ data: { job_id: "job-cancel", status: "queued", progress: 5 } });
    mocks.get.mockRejectedValue({ name: "CanceledError", code: "ERR_CANCELED" });
    controller.abort();
    await expect(analyzeExerciseVideo(
      "push_up",
      new File(["video"], "push-up.mp4", { type: "video/mp4" }),
      { signal: controller.signal },
    )).rejects.toEqual(expect.objectContaining({ code: "ERR_CANCELED" }));
    expect(mocks.post).toHaveBeenLastCalledWith("/api/v1/analysis-jobs/job-cancel/cancel");
  });

  it("uploads a video to the temporal recognition endpoint", async () => {
    mocks.post.mockResolvedValue({ data: { suggested_exercise_id: "push_up" } });
    const file = new File(["video"], "movement.mp4", { type: "video/mp4" });
    await recognizeExerciseVideo(file);
    expect(mocks.post).toHaveBeenCalledWith(
      "/api/v1/recognition/video?continue_on_subject_warning=false",
      expect.any(FormData),
      expect.objectContaining({ headers: { "Content-Type": "multipart/form-data" } }),
    );
  });

  it("can send the subject-warning override to video recognition", async () => {
    mocks.post.mockResolvedValue({ data: { suggested_exercise_id: "walking_gait_screen" } });
    const file = new File(["video"], "movement.mp4", { type: "video/mp4" });
    await recognizeExerciseVideo(file, undefined, { continue_on_subject_warning: true });
    expect(mocks.post.mock.calls[0][0]).toContain("continue_on_subject_warning=true");
  });

  it("records a confirmed recognition label", async () => {
    mocks.post.mockResolvedValue({ data: { status: "confirmed" } });
    await confirmRecognitionSuggestion("event-id", "push_up");
    expect(mocks.post).toHaveBeenCalledWith("/api/v1/recognition/confirm", {
      event_id: "event-id", confirmed_exercise_id: "push_up",
    });
  });

  it("uses the auth action endpoints without placing tokens in URLs", async () => {
    mocks.post.mockResolvedValue({ data: { status: "success" } });
    await verifyEmailToken("verification-token");
    await resendVerificationEmail("person@example.com");
    await requestPasswordReset("person@example.com");
    await submitPasswordReset("reset-token", "ReplacementPassword123");
    expect(mocks.post).toHaveBeenNthCalledWith(1, "/api/v1/auth/verify-email", { token: "verification-token" });
    expect(mocks.post).toHaveBeenNthCalledWith(2, "/api/v1/auth/resend-verification", { email: "person@example.com" });
    expect(mocks.post).toHaveBeenNthCalledWith(3, "/api/v1/auth/forgot-password", { email: "person@example.com" });
    expect(mocks.post).toHaveBeenNthCalledWith(4, "/api/v1/auth/reset-password", { token: "reset-token", new_password: "ReplacementPassword123" });
  });
});
