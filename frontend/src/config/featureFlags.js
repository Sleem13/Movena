export function resolveFeatureFlag(value) {
  return String(value || "").trim().toLowerCase() === "true";
}

export const ENABLE_REALTIME_COACHING_SPIKE = resolveFeatureFlag(
  import.meta.env.VITE_ENABLE_REALTIME_COACHING_SPIKE ?? (import.meta.env.DEV ? "true" : "false"),
);
