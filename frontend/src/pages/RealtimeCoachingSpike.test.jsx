import { describe, expect, it, vi } from "vitest";
import { render, screen } from "@testing-library/react";

import { LocaleProvider } from "../i18n/LocaleContext.jsx";
import RealtimeCoachingSpike, { readOptionalLandmarkSummary, summarizeFrame } from "./RealtimeCoachingSpike.jsx";

describe("RealtimeCoachingSpike", () => {
  it("renders as a disabled-by-default safety spike surface", () => {
    render(<LocaleProvider><RealtimeCoachingSpike /></LocaleProvider>);
    expect(screen.getByText("Real-time coaching technical spike")).toBeInTheDocument();
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
});
