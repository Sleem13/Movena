const day = /^\d{4}-\d{2}-\d{2}$/;

export function localCalendarDay(value) {
  const year = value.getFullYear();
  const month = String(value.getMonth() + 1).padStart(2, "0");
  const date = String(value.getDate()).padStart(2, "0");
  return `${year}-${month}-${date}`;
}

export function validReportPeriod(start, end) {
  if (!day.test(start) || !day.test(end)) return false;
  const first = Date.parse(`${start}T00:00:00Z`);
  const last = Date.parse(`${end}T00:00:00Z`);
  if (!Number.isFinite(first) || !Number.isFinite(last)) return false;
  if (new Date(first).toISOString().slice(0, 10) !== start) return false;
  if (new Date(last).toISOString().slice(0, 10) !== end) return false;
  const days = (last - first) / 86400000;
  return days >= 0 && days <= 366;
}

export function createReportPath(patientId, start, end, share) {
  const query = new URLSearchParams({
    period_start: start,
    period_end: end,
    share_with_patient: String(share),
  });
  return `therapist/patients/${encodeURIComponent(patientId)}/reports?${query}`;
}

export function reportHref(value) {
  if (typeof value !== "string" || value.length > 4096) return null;
  if (value.startsWith("/api/v1/artifacts/")) {
    return `/api/platform/${value.slice("/api/v1/".length)}`;
  }
  try {
    const parsed = new URL(value);
    return ["http:", "https:"].includes(parsed.protocol) &&
      !parsed.username &&
      !parsed.password
      ? parsed.toString()
      : null;
  } catch {
    return null;
  }
}
