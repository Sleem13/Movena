const REMOTE_ENVIRONMENTS = new Set(["staging", "production"]);

export function validateRemoteApiConfiguration(appEnv: string, configuredBaseUrl?: string): void {
  if (!REMOTE_ENVIRONMENTS.has(appEnv.trim().toLowerCase())) return;
  const url = configuredBaseUrl?.trim();
  if (!url) {
    throw new Error("A private HTTPS API URL is required for staging and production mobile builds.");
  }
  if (!url.startsWith("https://")) {
    throw new Error("Staging and production mobile builds require an HTTPS API URL.");
  }
  if (/\.invalid(?::\d+)?(?:\/|$)/i.test(url)) {
    throw new Error("Replace the placeholder API URL before creating a staging or production build.");
  }
}
