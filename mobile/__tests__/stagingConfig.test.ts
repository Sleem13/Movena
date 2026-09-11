import fs from "node:fs";
import path from "node:path";

describe("mobile staging configuration", () => {
  it("defines an internal preview-staging profile backed by EAS preview variables", () => {
    const config = JSON.parse(fs.readFileSync(path.join(process.cwd(), "eas.json"), "utf8"));
    expect(config.build["preview-staging"]).toMatchObject({ distribution: "internal", environment: "preview" });
    expect(config.build["preview-staging"].env.EXPO_PUBLIC_APP_ENV).toBe("staging");
    expect(config.build["preview-staging"].env.EXPO_PUBLIC_API_BASE_URL).toBe("https://d1ylxhoq5y66vd.cloudfront.net");
  });

  it("documents an HTTPS staging API without a secret", () => {
    const example = fs.readFileSync(path.join(process.cwd(), ".env.staging.example"), "utf8");
    expect(example).toMatch(/EXPO_PUBLIC_API_BASE_URL=https:\/\//);
    expect(example).not.toMatch(/SECRET_KEY|localhost|127\.0\.0\.1/);
  });

  it("ships the Movena app identity and approved visual assets", () => {
    const config = JSON.parse(fs.readFileSync(path.join(process.cwd(), "app.json"), "utf8"));
    expect(config.expo.name).toBe("Movena");
    expect(config.expo.version).toBe("0.29.0");
    expect(config.expo.icon).toBe("./assets/images/icon.png");
    expect(config.expo.android.adaptiveIcon.foregroundImage).toBe("./assets/images/adaptive-icon.png");
    expect(config.expo.plugins).toContainEqual(expect.arrayContaining(["expo-splash-screen", expect.objectContaining({ image: "./assets/images/splash-icon.png" })]));
    for (const asset of ["icon.png", "adaptive-icon.png", "splash-icon.png", "brand-wordmark.png"]) {
      expect(fs.statSync(path.join(process.cwd(), "assets/images", asset)).size).toBeGreaterThan(0);
    }
  });
});
