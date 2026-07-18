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
});
