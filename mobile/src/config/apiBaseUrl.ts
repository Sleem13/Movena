export function resolveApiBaseUrl(configuredBaseUrl: string | undefined, platform: string): string {
  const configured = configuredBaseUrl?.trim();
  if (configured) return configured.replace(/\/$/, "");

  // Expo web and iOS run on the development machine and use the standard
  // local FastAPI port. Android emulators require the host-machine alias and
  // keep the separately documented mobile backend port.
  return platform === "android" ? "http://10.0.2.2:8010" : "http://127.0.0.1:8000";
}
