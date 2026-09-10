jest.mock("@/src/api/client", () => ({ apiRequest: jest.fn().mockResolvedValue({ user_id: "user-1" }) }));

import { apiRequest } from "@/src/api/client";
import { register } from "@/src/api/auth";

test("registers a patient with the backend-required identity and consent fields", async () => {
  const payload = {
    username: "patient.one",
    email: "patient@example.com",
    password: "StrongPassword123",
    full_name: "Patient One",
    accepted_terms: true,
    accepted_privacy: true,
  };
  await register(payload);
  expect(apiRequest).toHaveBeenCalledWith("/api/v1/auth/register", {
    method: "POST",
    body: JSON.stringify({ ...payload, role: "patient" }),
  });
});
