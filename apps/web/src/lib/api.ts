export class ApiError extends Error {
  constructor(
    message: string,
    public status: number,
    public code?: string,
  ) {
    super(message);
  }
}
export async function api<T>(path: string, init: RequestInit = {}): Promise<T> {
  const headers = new Headers(init.headers);
  if (init.body && !(init.body instanceof FormData))
    headers.set("Content-Type", "application/json");
  let response: Response;
  try {
    response = await fetch(`/api/platform/${path}`, {
      ...init,
      headers,
      cache: "no-store",
    });
  } catch (error) {
    if (error instanceof DOMException && error.name === "AbortError")
      throw error;
    throw new ApiError(
      "Could not connect. Check your connection and try again.",
      0,
      "NETWORK_ERROR",
    );
  }
  const body = await response
    .json()
    .catch(() => ({ message: "The response could not be read." }));
  if (!response.ok) {
    if (response.status === 401 && !path.startsWith("auth/"))
      window.location.assign("/login");
    throw new ApiError(
      body.message || "The request could not be completed.",
      response.status,
      body.error_code,
    );
  }
  return body as T;
}
