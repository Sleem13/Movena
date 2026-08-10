import fs from "node:fs";
import path from "node:path";

describe("session history exercise coverage", () => {
  it.each(["bodyweight_squat", "sit_to_stand", "knee_extension", "shoulder_abduction", "hip_abduction", "push_up", "shoulder_press", "bicep_curl"])("includes %s", (exerciseId) => {
    const source = fs.readFileSync(path.join(process.cwd(), "app/history.tsx"), "utf8");
    expect(source).toContain(`\"${exerciseId}\"`);
  });
});
