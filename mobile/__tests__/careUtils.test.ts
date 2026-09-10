import { completionLabel, exerciseName, homeRoute, initials, needsReview, optionalScore } from "@/src/utils/care";

describe("role-aware care helpers", () => {
  test("routes patients and therapists into focused workspaces", () => {
    expect(homeRoute("patient")).toBe("/today");
    expect(homeRoute("therapist")).toBe("/patients");
  });

  test("formats patient-facing labels", () => {
    expect(exerciseName("sit_to_stand")).toBe("Sit to stand");
    expect(initials("Alex Morgan Lee")).toBe("AM");
    expect(completionLabel("partial")).toBe("Partly completed");
  });

  test("validates optional patient-reported scores", () => {
    expect(optionalScore("", "Pain", 0, 10)).toBeNull();
    expect(optionalScore("8", "Pain", 0, 10)).toBe(8);
    expect(() => optionalScore("11", "Pain", 0, 10)).toThrow("0 to 10");
  });

  test("keeps resolved responses out of the review queue", () => {
    expect(needsReview({ clinician_review_required: true, reviewed_at: null })).toBe(true);
    expect(needsReview({ clinician_review_required: true, reviewed_at: "2026-09-09" })).toBe(false);
  });
});
