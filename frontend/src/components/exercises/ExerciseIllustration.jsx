import ExercisePoseGraph from "./ExercisePoseGraph.jsx";

const POSES = [
  "bodyweight_squat", "sit_to_stand", "knee_extension", "shoulder_abduction",
  "shoulder_flexion", "hip_abduction", "walking_gait_screen", "balance",
  "push_up", "shoulder_press", "bicep_curl", "hammer_curl",
  "heel_raise", "lunge", "step_up", "hip_flexion",
];

export default function ExerciseIllustration({ exerciseId, label, supported }) {
  const index = POSES.indexOf(exerciseId);
  if (index < 0) return <ExercisePoseGraph exerciseId={exerciseId} label={label} supported={supported} />;
  return <div role="img" aria-label={label} className="exercise-illustration" style={{
    backgroundPosition: `${(index % 4) * 100 / 3}% ${Math.floor(index / 4) * 100 / 3}%`,
  }} />;
}
