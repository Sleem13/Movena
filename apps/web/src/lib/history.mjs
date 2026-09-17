export const historyPageSize = 20;
export const historyStatuses = ["", "success", "rejected", "error"];
export function historyPath(offset, status) {
  if (
    !Number.isSafeInteger(offset) ||
    offset < 0 ||
    !historyStatuses.includes(status)
  ) {
    throw new RangeError("Invalid history page");
  }
  return (
    "sessions?" +
    new URLSearchParams({
      limit: String(historyPageSize),
      offset: String(offset),
      status,
    })
  );
}
export function historyRepetitions(session) {
  const value = session.total_reps;
  return session.status === "success" &&
    Number.isSafeInteger(value) &&
    value >= 0
    ? value
    : null;
}
export function historyStatusKey(value) {
  const labels = {
      success: "historySuccess",
      rejected: "historyRejected",
      error: "historyError",
    };
  return Object.hasOwn(labels, value) ? labels[value] : 'historyUnknown';
}
