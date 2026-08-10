import { buildRecognitionHandoff } from "@/src/utils/recognitionHandoff";
import type { ExerciseMetadata } from "@/src/types/exercise";

const exercise: ExerciseMetadata = {
  exercise_id: "push_up", display_name: "Push-Up", supported_in_app: true,
  body_region: "Upper body", exercise_family: "Press", recommended_camera_view: "Side",
  required_landmarks: ["shoulder", "hip", "ankle"], movement_description: "Push-up",
  expected_movement_pattern: "Lower and return", safety_notes: "Stop if pain occurs.",
  endpoint_path: "/api/v1/analyze/push-up", ml_model_status: "not_applicable", recognition_status: "candidate",
};

describe("recognition-to-analysis handoff", () => {
  it("preserves the exact selected video and marks the route source", () => {
    const video = { uri: "file:///push-up.mp4", name: "push-up.mp4", type: "video/mp4", size: 1024 };
    const handoff = buildRecognitionHandoff(exercise, video);
    expect(handoff.video).toBe(video);
    expect(handoff.exercise).toBe(exercise);
    expect(handoff.route).toEqual({ pathname: "/upload/[id]", params: { id: "push_up", source: "recognition" } });
  });
});
