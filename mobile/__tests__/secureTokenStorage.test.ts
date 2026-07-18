import * as SecureStore from "expo-secure-store";
import { clearToken, getToken, saveToken } from "@/src/utils/secureTokenStorage";

jest.mock("expo-secure-store", () => ({ setItemAsync: jest.fn(), getItemAsync: jest.fn(), deleteItemAsync: jest.fn() }));

describe("secure token storage", () => {
  it("saves, reads, and clears only through SecureStore", async () => {
    (SecureStore.getItemAsync as jest.Mock).mockResolvedValue("token");
    await saveToken("token");
    await expect(getToken()).resolves.toBe("token");
    await clearToken();
    expect(SecureStore.setItemAsync).toHaveBeenCalledWith("physiovision_access_token", "token");
    expect(SecureStore.deleteItemAsync).toHaveBeenCalledWith("physiovision_access_token");
  });
});
