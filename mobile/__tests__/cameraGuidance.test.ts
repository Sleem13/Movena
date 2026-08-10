import { buildCameraGuidance } from "@/src/components/CameraChecklist";
import type { ExerciseMetadata } from "@/src/types/exercise";

const supported = ["bodyweight_squat", "sit_to_stand", "knee_extension", "shoulder_abduction", "hip_abduction", "push_up", "shoulder_press", "bicep_curl"];
const expectedCopy: Record<string, RegExp> = {
  bodyweight_squat: /full body.*side or front diagonal.*3–5 controlled/s,
  sit_to_stand: /side view.*chair and full body.*stand and sit cycle/s,
  knee_extension: /side view.*hip, knee, and ankle.*seated/s,
  shoulder_abduction: /front view.*shoulder, elbow, wrist, and trunk.*avoid trunk leaning/s,
  hip_abduction: /front view.*pelvis, hip, knee, and ankle.*avoid trunk leaning/s,
  push_up: /side view.*shoulders, hips, and ankles.*lowering and return/s,
  shoulder_press: /front view.*shoulders, elbows, wrists, and trunk.*approved load/s,
  bicep_curl: /front or slight side.*shoulder, elbow, wrist, and trunk.*extending, flexing/s,
};

describe("camera guidance", () => {
  test.each(supported)("renders safety-oriented guidance for %s", (exercise_id) => {
    const exercise = { exercise_id, display_name: exercise_id, supported_in_app: true, body_region: "test", exercise_family: "test", recommended_camera_view: "front", required_landmarks: ["hip", "knee"], movement_description: "test", expected_movement_pattern: "test", safety_notes: "test", endpoint_path: "/test", ml_model_status: "not_applicable", recognition_status: "experimental" } satisfies ExerciseMetadata;
    const guidance = buildCameraGuidance(exercise);
    const copy = guidance.join(" ");
    expect(copy).toMatch(/camera stable/i);
    expect(copy).toMatch(/one person only/i);
    expect(copy).toMatch(expectedCopy[exercise_id]);
  });
});
