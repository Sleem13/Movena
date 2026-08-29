import { describe, expect, it } from "vitest";

import { getApiErrorMessage } from "./requestErrors.js";

describe("getApiErrorMessage", () => {
  it("prefers the API message", () => {
    const error = { response: { data: { message: "API message" } } };
    expect(getApiErrorMessage(error, "Fallback")).toBe("API message");
  });

  it("preserves the caller fallback", () => {
    expect(getApiErrorMessage(new Error("offline"), "Fallback")).toBe(
      "Fallback",
    );
  });
});
