import { describe, expect, it, vi } from "vitest";
import { fireEvent, render, screen, waitFor } from "@testing-library/react";

import { LocaleProvider } from "../i18n/LocaleContext.jsx";
import RealtimeCoachingSpike, { cameraErrorMessageKey, coachingCueKey, drawPoseOverlay, readOptionalLandmarkSummary, summarizeFrame } from "./RealtimeCoachingSpike.jsx";
import { getLocalPoseLandmarkExtractor } from "../services/poseLandmarkExtractor.js";

vi.mock("../services/api.js", () => ({
  getRecognitionModels: vi.fn().mockResolvedValue({ status: "not_available", models: [] }),
  getCoachingReadiness: vi.fn().mockResolvedValue({ status: "ready", capabilities: {
    pose_data_pipeline: true, recognition_models: true, hand_orientation_evidence: true,
    authenticated_streaming: true, rep_events: true, metadata_persistence: true,
  } }),
  recognizeExerciseVideo: vi.fn(),
}));

vi.mock("../services/realtimeCoaching.js", () => ({
  connectRealtimeCoaching: vi.fn(() => ({ sendLandmarks: vi.fn(), stop: vi.fn(), close: vi.fn() })),
}));

vi.mock("../services/poseLandmarkExtractor.js", () => ({
  getLocalPoseLandmarkExtractor: vi.fn(),
}));

describe("RealtimeCoachingSpike", () => {
  it("renders as a disabled-by-default safety spike surface", () => {
    render(<LocaleProvider><RealtimeCoachingSpike /></LocaleProvider>);
    expect(screen.getByText("Exercise coaching lab")).toBeInTheDocument();
    expect(screen.getByText(/No video or audio is uploaded/)).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Start camera" })).toBeInTheDocument();
    fireEvent.click(screen.getByRole("combobox", { name: "Live exercise" }));
    expect(screen.getByRole("option", { name: "Bodyweight squat" })).toBeInTheDocument();
    expect(screen.getByRole("option", { name: "Shoulder press" })).toBeInTheDocument();
    expect(screen.getByRole("option", { name: "Lateral raise" })).toBeInTheDocument();
    expect(screen.getByText(/Keep the upper arm steady/)).toBeInTheDocument();
    expect(screen.getByText("Start the camera to begin live rep tracking.")).toBeInTheDocument();
  });

  it("maps live counter phases to actionable coaching cues", () => {
    expect(coachingCueKey("active", "seeking_start")).toBe("coach.cue.seekingStart");
    expect(coachingCueKey("active", "working")).toBe("coach.cue.working");
    expect(coachingCueKey("active", "returning")).toBe("coach.cue.returning");
  });

  it("draws a live pose skeleton with highlighted working joints", () => {
    const context = {
      clearRect: vi.fn(), beginPath: vi.fn(), moveTo: vi.fn(), lineTo: vi.fn(), stroke: vi.fn(), arc: vi.fn(), fill: vi.fn(),
    };
    const landmarks = Array.from({ length: 33 }, (_, index) => ({ x: index / 33, y: index / 33, visibility: 0.9 }));
    drawPoseOverlay({ width: 640, height: 480, getContext: () => context }, landmarks, "bodyweight_squat");
    expect(context.stroke).toHaveBeenCalled();
    expect(context.arc).toHaveBeenCalledTimes(33);
  });

  it("updates instructions when a different live exercise is selected", () => {
    render(<LocaleProvider><RealtimeCoachingSpike /></LocaleProvider>);
    fireEvent.click(screen.getByLabelText("Live exercise"));
    fireEvent.click(screen.getByRole("option", { name: "Bodyweight squat" }));
    expect(screen.getByText(/Lower with control until the knees visibly bend/)).toBeInTheDocument();
  });

  it("summarizes local frame brightness without retaining frame data", () => {
    const data = new Uint8ClampedArray([
      100, 100, 100, 255,
      200, 200, 200, 255,
    ]);
    const canvas = {
      width: 2,
      height: 1,
      getContext: () => ({ getImageData: () => ({ data }) }),
    };
    expect(summarizeFrame(canvas)).toMatchObject({ brightness: 150, visibilityProxy: 100 });
  });

  it("uses an optional local landmark extractor only when present", async () => {
    delete window.physioVisionLandmarkExtractor;
    await expect(readOptionalLandmarkSummary({})).resolves.toEqual({
      enabled: false,
      landmarkCount: 0,
      averageConfidence: null,
    });
    window.physioVisionLandmarkExtractor = {
      estimate: vi.fn().mockResolvedValue({ landmarks: [{ visibility: 0.8 }, { score: 0.6 }] }),
    };
    await expect(readOptionalLandmarkSummary({})).resolves.toMatchObject({
      enabled: true,
      landmarkCount: 2,
      averageConfidence: 0.7,
      hands: [],
    });
    delete window.physioVisionLandmarkExtractor;
  });

  it("renders completed readiness from backend capabilities", async () => {
    render(<LocaleProvider><RealtimeCoachingSpike /></LocaleProvider>);
    expect(await screen.findByText("Real-time coaching ready")).toBeInTheDocument();
    expect(screen.getByText(/hammer-curl hand-orientation evidence active/)).toBeInTheDocument();
    expect(screen.getByText(/metadata-only persistence implemented/)).toBeInTheDocument();
  });

  it("keeps recognition upload disabled when optional model runtimes are unavailable", async () => {
    render(<LocaleProvider><RealtimeCoachingSpike /></LocaleProvider>);

    expect(await screen.findByText("Artifact pending")).toBeInTheDocument();
    expect(screen.getByLabelText("Choose a movement video")).toBeDisabled();
    expect(screen.getByRole("button", { name: "Identify exercise" })).toBeDisabled();
  });

  it("loads the built-in local pose extractor when camera capture starts", async () => {
    const originalMediaDevices = navigator.mediaDevices;
    const extractor = { estimate: vi.fn().mockReturnValue({ landmarks: [] }) };
    getLocalPoseLandmarkExtractor.mockResolvedValue(extractor);
    Object.defineProperty(navigator, "mediaDevices", {
      configurable: true,
      value: { getUserMedia: vi.fn().mockResolvedValue({ getTracks: () => [] }) },
    });
    const playMock = vi.spyOn(HTMLMediaElement.prototype, "play").mockResolvedValue();

    render(<LocaleProvider><RealtimeCoachingSpike /></LocaleProvider>);
    fireEvent.click(screen.getByRole("button", { name: "Start camera" }));
    await waitFor(() => expect(getLocalPoseLandmarkExtractor).toHaveBeenCalledOnce());

    Object.defineProperty(navigator, "mediaDevices", {
      configurable: true,
      value: originalMediaDevices,
    });
    playMock.mockRestore();
  });

  it("classifies camera startup failures without treating every error as permission denial", () => {
    expect(cameraErrorMessageKey({ name: "NotFoundError" })).toBe("coach.noCameraError");
    expect(cameraErrorMessageKey({ name: "NotAllowedError" })).toBe("coach.permissionDeniedError");
    expect(cameraErrorMessageKey({ name: "NotReadableError" })).toBe("coach.cameraBusyError");
    expect(cameraErrorMessageKey({ name: "OverconstrainedError" })).toBe("coach.cameraConstraintsError");
    expect(cameraErrorMessageKey({ name: "AbortError" })).toBe("coach.permissionError");
  });

  it("shows a specific no-camera message and preserves the upload path", async () => {
    const originalMediaDevices = navigator.mediaDevices;
    Object.defineProperty(navigator, "mediaDevices", {
      configurable: true,
      value: { getUserMedia: vi.fn().mockRejectedValue({ name: "NotFoundError" }) },
    });
    render(<LocaleProvider><RealtimeCoachingSpike /></LocaleProvider>);
    fireEvent.click(screen.getByRole("button", { name: "Start camera" }));
    await waitFor(() => expect(screen.getByText(/No camera was detected/)).toBeInTheDocument());
    expect(screen.getByRole("heading", { name: "Identify an exercise from video" })).toBeInTheDocument();
    Object.defineProperty(navigator, "mediaDevices", {
      configurable: true,
      value: originalMediaDevices,
    });
  });
});
