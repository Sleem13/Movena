// @vitest-environment node
import { describe, expect, it } from "vitest";
import { loadConfigFromFile } from "vite";
import { fileURLToPath } from "node:url";

describe("Vite build configuration", () => {
  it.each(["", "https://name-physiovision-api-staging.onrender.com", "https://name-movena-api-staging.onrender.com"])("fails before compilation for invalid production URL %s", async (value) => {
    const previous = process.env.VITE_API_BASE_URL;
    process.env.VITE_API_BASE_URL = value;
    try {
      await expect(loadConfigFromFile(
        { command: "build", mode: "production" },
        fileURLToPath(new URL("./vite.config.js", import.meta.url)),
      )).rejects.toThrow(/VITE_API_BASE_URL/);
    } finally {
      if (previous === undefined) delete process.env.VITE_API_BASE_URL;
      else process.env.VITE_API_BASE_URL = previous;
    }
  });
});
