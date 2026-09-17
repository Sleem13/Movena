/** @type {Array<[string, string, number]>} */
export const healthFields = [
  ["emergency_contact_name", "emergencyContactName", 120],
  ["emergency_contact_phone", "emergencyContactPhone", 32],
  ["medical_summary", "medicalSummary", 5000],
  ["precautions", "precautions", 5000],
];
export function healthPayload(data) {
  return Object.fromEntries(
    healthFields.map(([key]) => [
      key,
      String(data.get(key) ?? "").trim() || null,
    ]),
  );
}
// Only exact known destinations are routed. Never follow server-authored URLs.
export function notificationDestination(value) {
  return (
    {
      "/patient": "/workspace/today",
      "/patient/today": "/workspace/today",
      "/appointments": "/workspace/schedule",
      "/patient/appointments": "/workspace/schedule",
      "/connections": "/workspace/care",
    }[value] ?? null
  );
}
export function recordDate(value, locale) {
  if (!value) return "—";
  const date = new Date(
    /(?:Z|[+-]\d\d:\d\d)$/.test(value) ? value : value + "Z",
  );
  return Number.isNaN(date.valueOf())
    ? "—"
    : new Intl.DateTimeFormat(locale, { dateStyle: "medium" }).format(date);
}
