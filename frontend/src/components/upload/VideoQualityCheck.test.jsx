import { render, screen, waitFor } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { LocaleProvider } from "../../i18n/LocaleContext.jsx";
import VideoQualityCheck, { evaluateFrameSamples, evaluateVideoMetadata } from "./VideoQualityCheck.jsx";

describe("video quality preflight thresholds", () => {
  it("passes a clear, standard recording", () => {
    expect(evaluateVideoMetadata({ duration: 20, width: 1080, height: 1920 }).map((item) => item.status)).toEqual(["pass", "pass", "pass"]);
    expect(evaluateFrameSamples({ brightnessValues: [100, 120, 130], motionValues: [12, 18] }).map((item) => item.status)).toEqual(["pass", "pass"]);
  });

  it("blocks unusably short or low-resolution recordings", () => {
    const checks = evaluateVideoMetadata({ duration: 1.2, width: 240, height: 320 });
    expect(checks.find((item) => item.code === "duration").status).toBe("fail");
    expect(checks.find((item) => item.code === "resolution").status).toBe("fail");
  });

  it("warns for extreme lighting and nearly static samples", () => {
    const checks = evaluateFrameSamples({ brightnessValues: [20, 25, 30], motionValues: [1, 2] });
    expect(checks.map((item) => item.status)).toEqual(["warn", "warn"]);
  });

  it.each([
    ["pass", "Recording looks ready", false],
    ["warn", "Review the recording", false],
    ["fail", "Choose a clearer recording", true],
  ])("renders the %s result state and reports blocking status", async (status, title, blocked) => {
    const onBlockingChange = vi.fn();
    const inspect = vi.fn().mockResolvedValue({ checks: [
      { code: "duration", status, value: "20.0s" },
      { code: "resolution", status: "pass", value: "1080×1920" },
    ] });
    render(<LocaleProvider><VideoQualityCheck file={new File(["video"], "movement.mp4", { type: "video/mp4" })} inspect={inspect} onBlockingChange={onBlockingChange} /></LocaleProvider>);
    expect(screen.getByText("Checking recording quality…")).toBeInTheDocument();
    expect(await screen.findByText(title)).toBeInTheDocument();
    expect(screen.getByText("Duration")).toBeInTheDocument();
    await waitFor(() => expect(onBlockingChange).toHaveBeenLastCalledWith(blocked));
  });
});
