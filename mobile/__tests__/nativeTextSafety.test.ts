import fs from "node:fs";
import path from "node:path";

describe("React Native text-child safety", () => {
  it("does not use empty-string state directly with && inside native views", () => {
    const files = ["app/exercises.tsx", "app/upload/[id].tsx", "app/login.tsx", "app/register.tsx"];
    for (const file of files) {
      const source = fs.readFileSync(path.join(process.cwd(), file), "utf8");
      expect(source).not.toMatch(/\{(?:sessionMessage|error)\s*&&/);
    }
  });
});
