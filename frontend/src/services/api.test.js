import { beforeEach, describe, expect, it, vi } from "vitest";

const mocks = vi.hoisted(() => {
  const get = vi.fn();
  const post = vi.fn();
  const del = vi.fn();
  const use = vi.fn();
  return {
    get,
    post,
    use,
    create: vi.fn(() => ({ get, post, delete: del, interceptors: { request: { use } } })),
  };
});

vi.mock("axios", () => ({ default: { create: mocks.create } }));

import {
  API_BASE_URL,
  analyzeExerciseVideo,
  artifactUrl,
  getTherapistDashboard,
  listSavedSessions,
  recognizeExerciseVideo,
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
    ["push_up", "push-up"],
    ["shoulder_press", "shoulder-press"],
    ["bicep_curl", "bicep-curl"],
  ])("routes %s to its dedicated analysis endpoint", async (exerciseId, endpoint) => {
    mocks.post.mockResolvedValue({ data: { exercise_id: exerciseId } });
    await analyzeExerciseVideo(exerciseId, new File(["video"], "movement.mp4", { type: "video/mp4" }));
    expect(mocks.post.mock.calls[0][0]).toContain(`/api/v1/analyze/${endpoint}?`);
  });

  it("uploads a video to the temporal recognition endpoint", async () => {
    mocks.post.mockResolvedValue({ data: { suggested_exercise_id: "push_up" } });
    const file = new File(["video"], "movement.mp4", { type: "video/mp4" });
    await recognizeExerciseVideo(file);
    expect(mocks.post).toHaveBeenCalledWith(
      "/api/v1/recognition/video",
      expect.any(FormData),
      expect.objectContaining({ headers: { "Content-Type": "multipart/form-data" } }),
    );
  });
});
