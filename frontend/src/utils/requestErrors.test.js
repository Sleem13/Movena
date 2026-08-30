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

  it("prefers a localized message for a known API error code", () => {
    const error = {
      response: {
        data: {
          error_code: "DATABASE_SCHEMA_OUTDATED",
          message: "English server message",
        },
      },
    };
    expect(
      getApiErrorMessage(error, "Fallback", {
        DATABASE_SCHEMA_OUTDATED: "مخطط قاعدة البيانات قديم.",
      }),
    ).toBe("مخطط قاعدة البيانات قديم.");
  });
});
