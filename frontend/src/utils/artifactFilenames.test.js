import { describe, expect, it } from "vitest";

import { artifactFilename } from "./artifactFilenames.js";

describe("artifactFilename", () => {
  it("names each artifact after its exercise", () => {
    expect(artifactFilename("walking_gait_screen", "overlay")).toBe("physiovision-walking-gait-screen-overlay.mp4");
    expect(artifactFilename("hammer_curl", "report")).toBe("physiovision-hammer-curl-report.pdf");
  });

  it("sanitizes unknown labels and falls back to movement", () => {
    expect(artifactFilename("../../Unsafe Name", "report")).toBe("physiovision-unsafe-name-report.pdf");
    expect(artifactFilename("", "overlay")).toBe("physiovision-movement-overlay.mp4");
  });
});
