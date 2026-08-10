import { isErrorResult, isRejectedResult, mlStatusMessage, movementScoreLabel, rejectedRecordingTip, shouldShowScore, totalRepsLabel } from "@/src/utils/result";

describe("result safety behavior", () => {
  it("never shows a score for rejected input", () => {
    const rejected = { exercise: "bodyweight_squat", status: "rejected", movement_score: 80 };
    expect(isRejectedResult(rejected)).toBe(true);
    expect(shouldShowScore(rejected)).toBe(false);
  });
  it("shows a real score only on success", () => expect(shouldShowScore({ exercise: "bodyweight_squat", status: "success", movement_score: 82 })).toBe(true));
  it("handles a null score", () => expect(shouldShowScore({ exercise: "bodyweight_squat", status: "success", movement_score: null })).toBe(false));
  it("labels null score and zero reps without inventing values", () => {
    const result = { exercise: "bodyweight_squat", status: "rejected", movement_score: null, score_breakdown: null, total_reps: 0 };
    expect(movementScoreLabel(result)).toBe("Not scored");
    expect(totalRepsLabel(result)).toBe("0");
  });
  it("handles ML not_applicable without presenting a prediction", () => {
    expect(mlStatusMessage({ enabled: false, warning: "ML is not applicable for this exercise." })).toMatch(/not applicable/i);
  });
  it.each(["bodyweight_squat", "sit_to_stand", "knee_extension", "shoulder_abduction", "hip_abduction", "push_up", "shoulder_press", "bicep_curl"])("returns exercise-specific retry guidance for %s", (exercise) => {
    expect(rejectedRecordingTip(exercise)).toMatch(/view/i);
  });
  it("treats status=error as a non-scoreable result", () => {
    const result = { exercise: "bodyweight_squat", status: "error", movement_score: 80 };
    expect(isErrorResult(result)).toBe(true);
    expect(shouldShowScore(result)).toBe(false);
  });
});
