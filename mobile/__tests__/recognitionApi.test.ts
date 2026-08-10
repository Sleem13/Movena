jest.mock("@/src/api/client", () => ({
  ApiError: class ApiError extends Error {},
  apiRequest: jest.fn().mockResolvedValue({ status: "confirmed" }),
  handleAuthenticationFailure: jest.fn(),
  parseApiError: jest.fn(),
}));
jest.mock("@/src/utils/secureTokenStorage", () => ({ getToken: jest.fn().mockResolvedValue(null) }));

import { confirmRecognitionSuggestion } from "@/src/api/recognition";
import { apiRequest } from "@/src/api/client";

const mockedApiRequest = apiRequest as jest.Mock;

describe("recognition confirmation API", () => {
  it("records the event and confirmed exercise without video data", async () => {
    await confirmRecognitionSuggestion("11111111-1111-1111-1111-111111111111", "push_up");
    expect(mockedApiRequest).toHaveBeenCalledWith(
      "/api/v1/recognition/confirm",
      { method: "POST", body: JSON.stringify({ event_id: "11111111-1111-1111-1111-111111111111", confirmed_exercise_id: "push_up" }) },
      true,
    );
    expect(mockedApiRequest.mock.calls[0][1].body).not.toContain("file://");
  });
});
