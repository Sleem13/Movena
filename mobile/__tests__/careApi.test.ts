jest.mock("@/src/api/client", () => ({ apiRequest: jest.fn().mockResolvedValue({ status: "ok" }) }));

import { apiRequest } from "@/src/api/client";
import { getToday, logAdherence } from "@/src/api/care";

const mockedApiRequest = apiRequest as jest.Mock;

beforeEach(() => mockedApiRequest.mockClear());

test("loads the patient-owned Today contract", async () => {
  await getToday();
  expect(mockedApiRequest).toHaveBeenCalledWith("/api/v1/patient/today", {}, true);
});

test("sends fatigue, comment, and an optional analysis link in a check-in", async () => {
  const payload = {
    plan_item_id: "item-1",
    scheduled_date: "2026-08-29",
    completion_status: "partial",
    pain_before: 4,
    pain_after: 5,
    difficulty: 3,
    fatigue: 4,
    note: "Stopped after the second set.",
    analysis_session_id: "session-1",
  };
  await logAdherence(payload);
  expect(mockedApiRequest).toHaveBeenCalledWith(
    "/api/v1/patient/adherence",
    expect.objectContaining({ method: "POST", body: JSON.stringify(payload) }),
    true,
  );
});
