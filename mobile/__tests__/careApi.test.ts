jest.mock("@/src/api/client", () => ({ apiRequest: jest.fn().mockResolvedValue({ status: "ok" }) }));

import { apiRequest } from "@/src/api/client";
import { acknowledgeResponse, getConnections, getPatientAdherence, getPatients, getToday, logAdherence, markNotificationRead, respondToInvitation } from "@/src/api/care";

const mockedApiRequest = apiRequest as jest.Mock;

beforeEach(() => mockedApiRequest.mockClear());

test("loads the patient-owned Today contract", async () => {
  await getToday();
  expect(mockedApiRequest).toHaveBeenCalledWith("/api/v1/patient/today", {}, true);
});

test("uses role-scoped care endpoints", async () => {
  await getConnections();
  await getPatients();
  mockedApiRequest.mockResolvedValueOnce([]);
  await getPatientAdherence("patient 1");
  expect(mockedApiRequest).toHaveBeenNthCalledWith(1, "/api/v1/connections", {}, true);
  expect(mockedApiRequest).toHaveBeenNthCalledWith(2, "/api/v1/therapist/patients", {}, true);
  expect(mockedApiRequest).toHaveBeenNthCalledWith(3, "/api/v1/therapist/patients/patient%201/adherence", {}, true);
});

test("carries the scoped patient ID from adherence retrieval into acknowledgement", async () => {
  mockedApiRequest.mockResolvedValueOnce([{
    adherence_id: "response/1", plan_item_id: "item-1", scheduled_date: "2026-09-10",
    completion_status: "partial", clinician_review_required: true, reviewed_at: null,
    symptom_flags: ["pain_increase"],
  }]);
  const [response] = await getPatientAdherence("patient/1");
  await acknowledgeResponse(response.patient_id, response.adherence_id, {
    disposition: "contacted_patient", clinician_attestation: true,
  });
  expect(mockedApiRequest).toHaveBeenLastCalledWith(
    "/api/v1/therapist/patients/patient%2F1/adherence/response%2F1/acknowledge",
    expect.objectContaining({ method: "POST" }), true,
  );
});

test("sends explicit invitation and clinical review actions", async () => {
  await respondToInvitation("invite/1", "accept");
  await acknowledgeResponse("patient/1", "response/1", { disposition: "contacted_patient", clinician_attestation: true });
  expect(mockedApiRequest).toHaveBeenNthCalledWith(1, "/api/v1/care-invitations/invite%2F1/respond", expect.objectContaining({ method: "POST", body: JSON.stringify({ action: "accept" }) }), true);
  expect(mockedApiRequest).toHaveBeenNthCalledWith(2, "/api/v1/therapist/patients/patient%2F1/adherence/response%2F1/acknowledge", expect.objectContaining({ method: "POST" }), true);
});

test("reuses a supplied idempotency key when retrying a check-in", async () => {
  await logAdherence({ plan_item_id: "item-1" }, "stable-key");
  expect(mockedApiRequest).toHaveBeenCalledWith("/api/v1/patient/adherence", expect.objectContaining({ headers: { "Idempotency-Key": "stable-key" } }), true);
});

test("marks a patient notification read", async () => {
  await markNotificationRead("notice/1");
  expect(mockedApiRequest).toHaveBeenCalledWith("/api/v1/patient/notifications/notice%2F1/read", { method: "POST" }, true);
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
