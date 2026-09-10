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
    ["shoulder_flexion", "/api/v1/analyze/shoulder-flexion"],
    ["hammer_curl", "/api/v1/analyze/hammer-curl"],
    ["walking_gait_screen", "/api/v1/analyze/gait"],
    ["balance", "/api/v1/analyze/balance"],
  ])("maps %s", (exercise, endpoint) => expect(getAnalysisEndpoint(exercise)).toBe(endpoint));

  test.each(["heel_raise", "lunge", "step_up", "hip_flexion", "ankle_pumps", "heel_slide", "quad_set", "straight_leg_raise", "glute_bridge"])("rejects guide-only analysis for %s", (id) => expect(() => getAnalysisEndpoint(id)).toThrow("not available"));
});
