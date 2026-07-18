import { isErrorResult, isRejectedResult, shouldShowScore } from "@/src/utils/result";

describe("result safety behavior", () => {
  it("never shows a score for rejected input", () => {
    const rejected = { exercise: "bodyweight_squat", status: "rejected", movement_score: 80 };
    expect(isRejectedResult(rejected)).toBe(true);
    expect(shouldShowScore(rejected)).toBe(false);
  });
  it("shows a real score only on success", () => expect(shouldShowScore({ exercise: "bodyweight_squat", status: "success", movement_score: 82 })).toBe(true));
  it("handles a null score", () => expect(shouldShowScore({ exercise: "bodyweight_squat", status: "success", movement_score: null })).toBe(false));
  it("treats status=error as a non-scoreable result", () => {
    const result = { exercise: "bodyweight_squat", status: "error", movement_score: 80 };
    expect(isErrorResult(result)).toBe(true);
    expect(shouldShowScore(result)).toBe(false);
  });
});
