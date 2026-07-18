import { Platform } from "react-native";

import { validateRemoteApiConfiguration } from "./runtimeSafety";

const configuredBaseUrl = process.env.EXPO_PUBLIC_API_BASE_URL?.trim();
const developmentDefault = Platform.OS === "android" ? "http://10.0.2.2:8010" : "http://127.0.0.1:8010";

export const APP_ENV = process.env.EXPO_PUBLIC_APP_ENV?.trim() || "development";
export const API_BASE_URL = (configuredBaseUrl || developmentDefault).replace(/\/$/, "");
validateRemoteApiConfiguration(APP_ENV, configuredBaseUrl);
export const API_TIMEOUT_MS = 120_000;
