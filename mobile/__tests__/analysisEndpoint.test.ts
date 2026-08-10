import { getAnalysisEndpoint } from "@/src/api/analysis";

describe("analysis endpoint mapping", () => {
  test.each([
    ["bodyweight_squat", "/api/v1/analyze/squat"],
    ["sit_to_stand", "/api/v1/analyze/sit-to-stand"],
    ["knee_extension", "/api/v1/analyze/knee-extension"],
    ["shoulder_abduction", "/api/v1/analyze/shoulder-abduction"],
    ["hip_abduction", "/api/v1/analyze/hip-abduction"],
    ["push_up", "/api/v1/analyze/push-up"],
    ["shoulder_press", "/api/v1/analyze/shoulder-press"],
    ["bicep_curl", "/api/v1/analyze/bicep-curl"],
  ])("maps %s", (exercise, endpoint) => expect(getAnalysisEndpoint(exercise)).toBe(endpoint));

  it("rejects a planned exercise", () => expect(() => getAnalysisEndpoint("heel_raise")).toThrow("planned"));
});
