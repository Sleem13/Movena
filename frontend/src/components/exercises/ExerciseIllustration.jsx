import ExercisePoseGraph from "./ExercisePoseGraph.jsx";

const POSES = [
  "bodyweight_squat", "sit_to_stand", "knee_extension", "shoulder_abduction",
  "shoulder_flexion", "hip_abduction", "walking_gait_screen", "balance",
  "push_up", "shoulder_press", "bicep_curl", "hammer_curl",
  "heel_raise", "lunge", "step_up", "hip_flexion",
];

export const GUIDE_POSES = [
  "heel_raise", "lunge", "step_up",
  "hip_flexion", "ankle_pumps", "heel_slide",
  "quad_set", "straight_leg_raise", "glute_bridge",
];

export default function ExerciseIllustration({ exerciseId, label, supported }) {
  const guideIndex = GUIDE_POSES.indexOf(exerciseId);
  if (guideIndex >= 0) return <div role="img" aria-label={label} className="exercise-illustration" style={{
    backgroundImage: "url('/exercise-guides-avatars.png')",
    backgroundSize: "300% 300%",
    backgroundPosition: `${(guideIndex % 3) * 50}% ${Math.floor(guideIndex / 3) * 50}%`,
  }} />;
  const index = POSES.indexOf(exerciseId);
  if (index < 0) return <ExercisePoseGraph exerciseId={exerciseId} label={label} supported={supported} />;
  return <div role="img" aria-label={label} className="exercise-illustration" style={{
    backgroundPosition: `${(index % 4) * 100 / 3}% ${Math.floor(index / 4) * 100 / 3}%`,
  }} />;
}
