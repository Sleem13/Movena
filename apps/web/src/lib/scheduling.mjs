export function calendarDay(date = new Date()) {
  return `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, "0")}-${String(date.getDate()).padStart(2, "0")}`;
}
export function shiftDay(value, amount) {
  const [year, month, day] = value.split("-").map(Number);
  return calendarDay(new Date(year, month - 1, day + amount, 12));
}
export function visitUrl(grant, now = Date.now()) {
  const url = new URL(grant.room_url);
  if (
    url.protocol !== "https:" ||
    url.username ||
    url.password ||
    !grant.meeting_token ||
    typeof grant.meeting_token !== "string" ||
    !Number.isFinite(Date.parse(grant.expires_at)) ||
    Date.parse(grant.expires_at) <= now
  )
    throw new Error("Invalid or expired visit grant");
  url.searchParams.set("t", grant.meeting_token);
  return url.toString();
}
export function minutes(value) {
  if (!/^\d{2}:\d{2}$/.test(value)) return NaN;
  const [hours, mins] = value.split(":").map(Number);
  return hours < 24 && mins < 60 ? hours * 60 + mins : NaN;
}
