export function resolveApiBaseUrl(configuredUrl, isDevelopment) {
  const value = configuredUrl?.trim();
  if (!value) {
    if (isDevelopment) return "http://127.0.0.1:8000";
    throw new Error("VITE_API_BASE_URL is required for non-development builds.");
  }
  let url;
  try {
    url = new URL(value);
  } catch {
    throw new Error("VITE_API_BASE_URL must be an absolute HTTP(S) URL.");
  }
  if (!['http:', 'https:'].includes(url.protocol) || url.username || url.password || url.search || url.hash) {
    throw new Error("VITE_API_BASE_URL must be an HTTP(S) URL without credentials, query, or fragment.");
  }
  if (!isDevelopment && /(^|\.)onrender\.com\.?$/i.test(url.hostname)) {
    throw new Error("VITE_API_BASE_URL must use the active AWS endpoint; legacy Render endpoints are disabled.");
  }
  return value.replace(/\/+$/, "");
}
