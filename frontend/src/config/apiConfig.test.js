import { describe, expect, it } from "vitest";
import { resolveApiBaseUrl } from "./apiConfig";

describe("staging API configuration", () => {
  it("uses and normalizes an explicit staging URL", () => {
    expect(resolveApiBaseUrl("https://staging-api.example.test/", false)).toBe("https://staging-api.example.test");
  });

  it("fails closed without a non-development API URL", () => {
    expect(() => resolveApiBaseUrl("", false)).toThrow(/VITE_API_BASE_URL/);
  });

  it("retains the localhost fallback only for development", () => {
    expect(resolveApiBaseUrl(undefined, true)).toBe("http://127.0.0.1:8000");
  });

  it.each([
    "https://name-physiovision-api-staging.onrender.com",
    "https://name-movena-api-staging.onrender.com/",
    "https://another-service.ONRENDER.com./",
  ])("rejects legacy production endpoints: %s", (url) => {
    expect(() => resolveApiBaseUrl(url, false)).toThrow(/legacy Render/);
  });

  it.each([" ", "/api", "not-a-url", "ftp://api.example.test", "https://user:password@api.example.test", "https://api.example.test?token=secret"])("rejects unsafe configuration: %s", (url) => {
    expect(() => resolveApiBaseUrl(url, false)).toThrow(/VITE_API_BASE_URL/);
  });
});
