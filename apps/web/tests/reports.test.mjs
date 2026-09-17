import test from "node:test";
import assert from "node:assert/strict";
import {
  createReportPath,
  localCalendarDay,
  reportHref,
  validReportPeriod,
} from "../src/lib/reports.mjs";

test("report periods and query parameters preserve calendar dates", () => {
  assert.equal(validReportPeriod("2025-01-01", "2026-01-02"), true);
  assert.equal(validReportPeriod("2025-01-01", "2026-01-03"), false);
  assert.equal(validReportPeriod("2025-02-02", "2025-02-01"), false);
  assert.equal(validReportPeriod("2025-02-30", "2025-03-01"), false);
  assert.equal(localCalendarDay(new Date(2025, 0, 9, 23, 30)), "2025-01-09");
  assert.equal(
    createReportPath("patient/id", "2025-01-01", "2025-01-31", true),
    "therapist/patients/patient%2Fid/reports?period_start=2025-01-01&period_end=2025-01-31&share_with_patient=true",
  );
});

test("signed report links stay behind the replacement proxy", () => {
  assert.equal(
    reportHref("/api/v1/artifacts/reports/id?expires=1&signature=abc"),
    "/api/platform/artifacts/reports/id?expires=1&signature=abc",
  );
  assert.equal(reportHref("javascript:alert(1)"), null);
  assert.equal(reportHref("https://user:secret@example.com/report"), null);
});
