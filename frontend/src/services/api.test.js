import { beforeEach, describe, expect, it, vi } from "vitest";

const mocks = vi.hoisted(() => {
  const get = vi.fn();
  const post = vi.fn();
  const del = vi.fn();
  const use = vi.fn();
  return {
    get,
    use,
    create: vi.fn(() => ({ get, post, delete: del, interceptors: { request: { use } } })),
  };
});

vi.mock("axios", () => ({ default: { create: mocks.create } }));

import {
  API_BASE_URL,
  artifactUrl,
  getTherapistDashboard,
  listSavedSessions,
} from "./api.js";

describe("deployment API configuration", () => {
  beforeEach(() => mocks.get.mockReset());

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
});
