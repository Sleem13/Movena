import { Platform } from "react-native";

import { resolveApiBaseUrl } from "./apiBaseUrl";
import { validateRemoteApiConfiguration } from "./runtimeSafety";

const configuredBaseUrl = process.env.EXPO_PUBLIC_API_BASE_URL?.trim();

export const APP_ENV = process.env.EXPO_PUBLIC_APP_ENV?.trim() || "development";
export const API_BASE_URL = resolveApiBaseUrl(configuredBaseUrl, Platform.OS);
validateRemoteApiConfiguration(APP_ENV, configuredBaseUrl);
export const API_TIMEOUT_MS = 120_000;
