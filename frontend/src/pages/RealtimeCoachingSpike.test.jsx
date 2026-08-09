import { describe, expect, it, vi } from "vitest";
import { fireEvent, render, screen, waitFor } from "@testing-library/react";

import { LocaleProvider } from "../i18n/LocaleContext.jsx";
import RealtimeCoachingSpike, { cameraErrorMessageKey, readOptionalLandmarkSummary, summarizeFrame } from "./RealtimeCoachingSpike.jsx";

vi.mock("../services/api.js", () => ({
  getRecognitionModels: vi.fn().mockResolvedValue({ status: "not_available", models: [] }),
  recognizeExerciseVideo: vi.fn(),
}));

describe("RealtimeCoachingSpike", () => {
  it("renders as a disabled-by-default safety spike surface", () => {
    render(<LocaleProvider><RealtimeCoachingSpike /></LocaleProvider>);
    expect(screen.getByText("Exercise coaching lab")).toBeInTheDocument();
    expect(screen.getByText(/No video or audio is uploaded/)).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Start camera" })).toBeInTheDocument();
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
    await expect(readOptionalLandmarkSummary({})).resolves.toEqual({
      enabled: true,
      landmarkCount: 2,
      averageConfidence: 0.7,
    });
    delete window.physioVisionLandmarkExtractor;
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
