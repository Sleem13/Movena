import { buildCameraGuidance } from "@/src/components/CameraChecklist";
import type { ExerciseMetadata } from "@/src/types/exercise";

const supported = ["bodyweight_squat", "sit_to_stand", "knee_extension", "shoulder_abduction", "hip_abduction"];

describe("camera guidance", () => {
  test.each(supported)("renders safety-oriented guidance for %s", (exercise_id) => {
    const exercise = { exercise_id, display_name: exercise_id, supported_in_app: true, body_region: "test", exercise_family: "test", recommended_camera_view: "front", required_landmarks: ["hip", "knee"], movement_description: "test", expected_movement_pattern: "test", safety_notes: "test", endpoint_path: "/test", ml_model_status: "not_applicable", recognition_status: "experimental" } satisfies ExerciseMetadata;
    const guidance = buildCameraGuidance(exercise);
    expect(guidance.join(" ")).toMatch(/camera stable/i);
    expect(guidance.join(" ")).toMatch(/hip, knee/i);
  });
});
