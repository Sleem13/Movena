export const PUBLIC_AUTH = new Set([
  "auth/login",
  "auth/register",
  "auth/forgot-password",
  "auth/reset-password",
  "auth/verify-email",
  "auth/resend-verification",
]);
export function safePath(segments) {
  return (
    segments.length > 0 && segments.every((p) => /^[a-zA-Z0-9_-]+$/.test(p))
  );
}
export function sameOriginMutation(method, origin, requestOrigin) {
  return (
    ["GET", "HEAD", "OPTIONS"].includes(method) ||
    (typeof origin === 'string' && typeof requestOrigin === 'string' && origin !== '' && origin === requestOrigin)
  );
}
// Trust deployment configuration, never caller-supplied Forwarded/Host values.
export function publicOrigin(configured, fallback) {
  try {
    const url = new URL(configured === undefined ? fallback : configured);
    if (!['http:', 'https:'].includes(url.protocol) || url.username || url.password ||
      url.pathname !== '/' || url.search || url.hash) return null;
    return url.origin;
  } catch { return null; }
}
