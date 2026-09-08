import { describe, expect, it } from "vitest";

import { artifactFilename } from "./artifactFilenames.js";

describe("artifactFilename", () => {
  it("names each artifact after its exercise", () => {
    expect(artifactFilename("walking_gait_screen", "overlay")).toBe("movena-walking-gait-screen-overlay.webm");
    expect(artifactFilename("hammer_curl", "report")).toBe("movena-hammer-curl-report.pdf");
  });

  it("sanitizes unknown labels and falls back to movement", () => {
    expect(artifactFilename("../../Unsafe Name", "report")).toBe("movena-unsafe-name-report.pdf");
    expect(artifactFilename("", "overlay")).toBe("movena-movement-overlay.webm");
  });
});
