import { Image, View } from "react-native";

const GUIDE_POSES = [
  "heel_raise", "lunge", "step_up",
  "hip_flexion", "ankle_pumps", "heel_slide",
  "quad_set", "straight_leg_raise", "glute_bridge",
];
export const hasExerciseAvatar = (id: string) => GUIDE_POSES.includes(id);

/** Crop a single illustration cell without downloading an external asset. */
export function ExerciseAvatar({ id, label, width = 88 }: { id: string; label: string; width?: number }) {
  const index = GUIDE_POSES.indexOf(id);
  if (index < 0) return null;
  const height = width / 1.5;
  return <View accessible accessibilityRole="image" accessibilityLabel={label} style={{ width, height, overflow: "hidden", borderRadius: 10 }}>
    <Image accessible={false} source={require("../../assets/images/exercise-guides-avatars.png")} resizeMode="stretch" style={{
      position: "absolute", width: width * 3, height: height * 3,
      left: -(index % 3) * width, top: -Math.floor(index / 3) * height,
    }} />
  </View>;
}
