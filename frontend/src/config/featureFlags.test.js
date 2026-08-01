import { describe, expect, it } from "vitest";

import { resolveFeatureFlag } from "./featureFlags";

describe("feature flags", () => {
  it("only enables explicit true values", () => {
    expect(resolveFeatureFlag("true")).toBe(true);
    expect(resolveFeatureFlag(" TRUE ")).toBe(true);
    expect(resolveFeatureFlag("false")).toBe(false);
    expect(resolveFeatureFlag("1")).toBe(false);
    expect(resolveFeatureFlag(undefined)).toBe(false);
  });
});
