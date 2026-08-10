import * as SecureStore from "expo-secure-store";
import { ApiError, handleAuthenticationFailure } from "@/src/api/client";

jest.mock("expo-secure-store", () => ({ isAvailableAsync: jest.fn().mockResolvedValue(true), setItemAsync: jest.fn(), getItemAsync: jest.fn(), deleteItemAsync: jest.fn() }));

describe("token lifecycle", () => {
  it.each([["INVALID_TOKEN", 401], ["TOKEN_EXPIRED", 401]])("clears SecureStore for %s", async (code, status) => {
    await handleAuthenticationFailure(new ApiError("Expired", code as string, status as number));
    expect(SecureStore.deleteItemAsync).toHaveBeenCalledWith("physiovision_access_token");
  });

  it("does not clear a token for an offline request", async () => {
    (SecureStore.deleteItemAsync as jest.Mock).mockClear();
    await handleAuthenticationFailure(new ApiError("Offline", "NETWORK_ERROR"));
    expect(SecureStore.deleteItemAsync).not.toHaveBeenCalled();
  });
});
