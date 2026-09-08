import * as SecureStore from "expo-secure-store";
import { clearToken, getToken, saveToken } from "@/src/utils/secureTokenStorage";

jest.mock("expo-secure-store", () => ({ isAvailableAsync: jest.fn(), setItemAsync: jest.fn(), getItemAsync: jest.fn(), deleteItemAsync: jest.fn() }));

describe("secure token storage", () => {
  it("saves, reads, and clears only through SecureStore", async () => {
    (SecureStore.isAvailableAsync as jest.Mock).mockResolvedValue(true);
    (SecureStore.getItemAsync as jest.Mock).mockResolvedValue("token");
    await saveToken("token");
    await expect(getToken()).resolves.toBe("token");
    await clearToken();
    expect(SecureStore.setItemAsync).toHaveBeenCalledWith("movena_access_token", "token");
    expect(SecureStore.deleteItemAsync).toHaveBeenCalledWith("movena_access_token");
  });

  it("uses volatile session storage when the native module is unavailable", async () => {
    (SecureStore.isAvailableAsync as jest.Mock).mockResolvedValue(false);
    await saveToken("temporary-token");
    await expect(getToken()).resolves.toBe("temporary-token");
    await clearToken();
    await expect(getToken()).resolves.toBeNull();
    expect(SecureStore.setItemAsync).not.toHaveBeenCalledWith("movena_access_token", "temporary-token");
  });
});
