import fs from "node:fs";
import path from "node:path";

describe("mobile staging configuration", () => {
  it("defines an internal preview-staging profile backed by EAS preview variables", () => {
    const config = JSON.parse(fs.readFileSync(path.join(process.cwd(), "eas.json"), "utf8"));
    expect(config.build["preview-staging"]).toMatchObject({ distribution: "internal", environment: "preview" });
    expect(config.build["preview-staging"].env.EXPO_PUBLIC_APP_ENV).toBe("staging");
  });

  it("documents an HTTPS staging API without a secret", () => {
    const example = fs.readFileSync(path.join(process.cwd(), ".env.staging.example"), "utf8");
    expect(example).toMatch(/EXPO_PUBLIC_API_BASE_URL=https:\/\//);
    expect(example).not.toMatch(/SECRET_KEY|localhost|127\.0\.0\.1/);
  });
});
