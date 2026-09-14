import test from "node:test";
import assert from "node:assert/strict";
import {
  calendarDay,
  shiftDay,
  minutes,
  visitUrl,
} from "../src/lib/scheduling.mjs";

test("calendar day uses local fields and availability rejects malformed times", () => {
  assert.equal(calendarDay(new Date(2030, 0, 2, 23)), "2030-01-02");
  assert.equal(shiftDay("2030-12-31", 1), "2031-01-01");
  assert.equal(shiftDay("2028-03-01", -1), "2028-02-29");
  assert.equal(minutes("09:30"), 570);
  for (const time of ["24:00", "12:60", "9:30", "wrong", "-1:00"])
    assert.ok(Number.isNaN(minutes(time)));
});

test("visit grant requires HTTPS and a future expiry; token is encoded once", () => {
  const now = Date.parse("2030-01-01T00:00:00Z");
  const grant = {
    room_url: "https://video.example.test/room?lang=ar",
    meeting_token: "a+b/c==",
    expires_at: "2030-01-01T01:00:00Z",
  };
  const url = new URL(visitUrl(grant, now));
  assert.equal(url.searchParams.get("t"), grant.meeting_token);
  assert.equal(url.searchParams.get("lang"), "ar");
  for (const room_url of [
    "http://video.example.test",
    "javascript:alert(1)",
    "https://user:pass@video.example.test",
  ])
    assert.throws(() => visitUrl({ ...grant, room_url }, now));
  for (const expires_at of [
    "unavailable",
    "2030-01-01T00:00:00Z",
    "2029-12-31T23:00:00Z",
  ])
    assert.throws(() => visitUrl({ ...grant, expires_at }, now));
  assert.throws(() => visitUrl({ ...grant, meeting_token: "" }, now));
});
