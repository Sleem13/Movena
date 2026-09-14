export const planNumbers = [
  ["sets", "sets", 1, 20, true],
  ["reps", "reps", 1, 100, true],
  ["days_per_week", "daysPerWeek", 1, 7, true],
  ["duration_minutes", "durationMinutes", 1, 240, false],
  ["rest_interval_seconds", "restSeconds", 0, 3600, false],
  ["target_rom_degrees", "targetRom", 0, 360, false],
  ["target_score", "targetScore", 0, 100, false],
];
export const planTexts = [
  ["instructions", "instructions", 1000],
  ["tempo", "tempo", 64],
  ["precautions", "precautions", 1000],
];
export function planPayload(form, ids) {
  const text = (key) => String(form.get(key) ?? "").trim();
  const start = text("start_date"),
    end = text("end_date");
  if (start && end && end < start) throw new Error("invalidPlanDates");
  const items = ids.map((id) => {
    const row = {
      exercise_id: text(`${id}:exercise_id`),
      schedule_days: form.getAll(`${id}:schedule_days`).map(Number),
      requested_media_upload: form.get(`${id}:requested_media_upload`) === "on",
      requires_ai_analysis: form.get(`${id}:requires_ai_analysis`) === "on",
    };
    for (const [field, , min, max, required] of planNumbers) {
      const value = text(`${id}:${field}`);
      if (required && !value) throw new Error("requiredDosage");
      if (value) {
        const n = Number(value);
        if (
          !Number.isFinite(n) ||
          n < min ||
          n > max ||
          (!field.startsWith("target_") && !Number.isInteger(n))
        )
          throw new Error("invalidDosage");
        row[field] = n;
      } else row[field] = null;
    }
    for (const [field] of planTexts)
      row[field] = text(`${id}:${field}`) || null;
    return row;
  });
  return {
    title: text("title"),
    notes: text("notes") || null,
    start_date: start ? `${start}T00:00:00Z` : null,
    end_date: end ? `${end}T00:00:00Z` : null,
    items,
  };
}
