import * as SecureStore from "expo-secure-store";

const TOKEN_KEY = "movena_access_token";
let volatileToken: string | null = null;

async function secureStoreIsAvailable(): Promise<boolean> {
  try {
    return await SecureStore.isAvailableAsync();
  } catch {
    return false;
  }
}

export async function saveToken(token: string): Promise<void> {
  volatileToken = token;
  if (await secureStoreIsAvailable()) await SecureStore.setItemAsync(TOKEN_KEY, token);
}

export async function getToken(): Promise<string | null> {
  if (!await secureStoreIsAvailable()) return volatileToken;
  try {
    return await SecureStore.getItemAsync(TOKEN_KEY);
  } catch {
    return volatileToken;
  }
}

export async function clearToken(): Promise<void> {
  volatileToken = null;
  if (!await secureStoreIsAvailable()) return;
  try {
    await SecureStore.deleteItemAsync(TOKEN_KEY);
  } catch {
    // A stale development client may lose its native module during an update.
  }
}
