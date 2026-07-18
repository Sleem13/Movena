import fs from "node:fs";
import path from "node:path";
import { DISCLAIMER } from "@/src/config/theme";

describe("React Native text-child safety", () => {
  it("uses the required licensed-physiotherapist disclaimer", () => {
    expect(DISCLAIMER).toBe("PhysioVision AI supports exercise monitoring and does not replace assessment by a licensed physiotherapist.");
  });
  it("does not use empty-string state directly with && inside native views", () => {
    const files = ["app/exercises.tsx", "app/upload/[id].tsx", "app/login.tsx", "app/register.tsx"];
    for (const file of files) {
      const source = fs.readFileSync(path.join(process.cwd(), file), "utf8");
      expect(source).not.toMatch(/\{(?:sessionMessage|error)\s*&&/);
    }
  });
  it("keeps rejected-result retry and safety controls visible", () => {
    const source = fs.readFileSync(path.join(process.cwd(), "app/result.tsx"), "utf8");
    expect(source).toContain("Why this was rejected");
    expect(source).toContain('title="Try Again"');
    expect(source).toContain("<SafetyNotice />");
  });
});
