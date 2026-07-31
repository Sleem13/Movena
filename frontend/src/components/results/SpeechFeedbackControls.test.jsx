import { fireEvent, render, screen } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { LocaleProvider } from "../../i18n/LocaleContext.jsx";
import SpeechFeedbackControls, { buildSpeechSummary } from "./SpeechFeedbackControls.jsx";

const report = {
  exercise: "bodyweight_squat",
  status: "success",
  summary: "Three controlled repetitions were observed.",
  total_reps: 3,
  movement_score: 82,
  analysis_confidence: { level: "medium" },
  feedback: ["Keep the full body visible."],
  limitations: ["Camera angle can affect measurements."],
};

class MockUtterance {
  constructor(text) { this.text = text; }
}

describe("SpeechFeedbackControls", () => {
  beforeEach(() => {
    globalThis.SpeechSynthesisUtterance = MockUtterance;
    Object.defineProperty(window, "speechSynthesis", {
      configurable: true,
      value: { speak: vi.fn(), cancel: vi.fn() },
    });
  });

  afterEach(() => {
    delete globalThis.SpeechSynthesisUtterance;
    delete window.speechSynthesis;
  });

  it("builds a conservative spoken summary from the current report", () => {
    const t = (key, values = {}) => ({
      "exercise.bodyweight_squat": "Bodyweight squat",
      "speech.statusComplete": `${values.exercise} analysis complete.`,
      "speech.reps": `Completed repetitions: ${values.count}.`,
      "speech.score": `Movement score: ${values.score} out of 100.`,
      "speech.confidence": `Analysis confidence: ${values.level}.`,
      "speech.feedbackIntro": "Feedback:",
      "speech.limitationsIntro": "Important limitations:",
      "speech.disclaimer": "Educational only.",
    }[key] || key);
    const summary = buildSpeechSummary(report, t);
    expect(summary).toContain("Bodyweight squat analysis complete.");
    expect(summary).toContain("Completed repetitions: 3.");
    expect(summary).toContain("Educational only.");
  });

  it("speaks and cancels feedback on demand", () => {
    render(<LocaleProvider><SpeechFeedbackControls report={report} /></LocaleProvider>);
    fireEvent.click(screen.getByRole("button", { name: "Listen to feedback" }));
    expect(window.speechSynthesis.speak).toHaveBeenCalledTimes(1);
    const utterance = window.speechSynthesis.speak.mock.calls[0][0];
    expect(utterance.text).toContain("Three controlled repetitions were observed.");
    expect(utterance.lang).toBe("en-US");
    fireEvent.click(screen.getByRole("button", { name: "Stop audio" }));
    expect(window.speechSynthesis.cancel).toHaveBeenCalled();
  });
});
