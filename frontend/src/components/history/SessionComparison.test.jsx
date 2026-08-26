import { describe, expect, it } from "vitest";
import { buildComparisonRows } from "./SessionComparison.jsx";

describe("buildComparisonRows", () => {
  it("orders sessions chronologically and calculates metric deltas", () => {
    const rows = buildComparisonRows([
      { created_at: "2026-08-20T10:00:00Z", movement_score: 88, total_reps: 5, metrics: [{ metric_name: "average_knee_angle", metric_value_float: 105 }] },
      { created_at: "2026-08-01T10:00:00Z", movement_score: 80, total_reps: 3, metrics: [{ metric_name: "average_knee_angle", metric_value_float: 112 }] },
    ]);
    expect(rows.find((row) => row.key === "movement_score")).toMatchObject({ previous: 80, current: 88, delta: 8 });
    expect(rows.find((row) => row.key === "total_reps")).toMatchObject({ previous: 3, current: 5, delta: 2 });
    expect(rows.find((row) => row.key === "average_knee_angle")).toMatchObject({ previous: 112, current: 105, delta: -7 });
  });

  it("omits unavailable and placeholder zero-only joint metrics", () => {
    const rows = buildComparisonRows([
      { created_at: "2026-08-01T10:00:00Z", movement_score: null, total_reps: 2, metrics: [{ metric_name: "average_hip_angle", metric_value_float: 0 }] },
      { created_at: "2026-08-02T10:00:00Z", movement_score: null, total_reps: 3, metrics: [{ metric_name: "average_hip_angle", metric_value_float: 0 }] },
    ]);
    expect(rows.map((row) => row.key)).toEqual(["total_reps"]);
  });
});
