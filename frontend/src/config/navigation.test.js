import { describe, expect, it } from "vitest";

import { landingPageForRole, pageForPath } from "./navigation.js";

describe("navigation mapping", () => {
  it.each([
    ["/therapist/patients/123", "therapistPatients"],
    ["/therapist", "therapist"],
    ["/admin/users/123", "adminUsers"],
    ["/admin/payments", "adminWorkflow"],
    ["/rehab-policy", "rehabPolicy"],
    ["/recovery-coaching", "recoveryCoaching"],
    ["/forgot-password", "forgotPassword"],
    ["/unknown", "home"],
  ])("maps %s to %s", (path, expected) => {
    expect(pageForPath(path, false)).toBe(expected);
  });

  it("keeps realtime coaching behind its feature flag", () => {
    expect(pageForPath("/coach", false)).toBe("home");
    expect(pageForPath("/coach", true)).toBe("coach");
  });

  it.each([
    ["patient", "care"],
    ["therapist", "therapist"],
    ["super_admin", "adminWorkflow"],
    ["admin", "workspace"],
  ])("maps the %s landing page", (role, expected) => {
    expect(landingPageForRole({ role })).toBe(expected);
  });
});
