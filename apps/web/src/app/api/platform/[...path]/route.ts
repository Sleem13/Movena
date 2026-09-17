import { NextRequest, NextResponse } from "next/server";
import { cookies } from "next/headers";
import {
  PUBLIC_AUTH,
  safePath,
  sameOriginMutation,
  publicOrigin,
} from "../../../../lib/proxy-policy.mjs";

export const runtime = "nodejs";
const COOKIE = "movena_session_v2";
async function forward(
  request: NextRequest,
  context: { params: Promise<{ path: string[] }> },
) {
  const { path } = await context.params;
  if (!safePath(path))
    return NextResponse.json({ message: "Invalid path." }, { status: 400 });
  if (
    !sameOriginMutation(
      request.method,
      request.headers.get("origin"),
      publicOrigin(process.env.MOVENA_WEB_ORIGIN, request.nextUrl.origin),
    )
  )
    return NextResponse.json(
      { message: "Request origin is not allowed." },
      { status: 403 },
    );
  const resource = path.join("/");
  const jar = await cookies();
  const token = jar.get(COOKIE)?.value;
  if (!token && !PUBLIC_AUTH.has(resource) && resource !== "exercises")
    return NextResponse.json({ message: "Please log in." }, { status: 401 });
  const base = process.env.MOVENA_PLATFORM_URL || "http://127.0.0.1:8020";
  const headers = new Headers({ Accept: "application/json" });
  if (token && !PUBLIC_AUTH.has(resource))
    headers.set("Authorization", `Bearer ${token}`);
  for (const name of ["content-type", "idempotency-key"]) {
    const value = request.headers.get(name);
    if (value) headers.set(name, value);
  }
  let upstream: Response;
  try {
    upstream = await fetch(
      `${base}/api/v2/${resource}${request.nextUrl.search}`,
      {
        method: request.method,
        headers,
        body: ["GET", "HEAD"].includes(request.method)
          ? undefined
          : await request.arrayBuffer(),
        cache: "no-store",
        redirect: "manual",
        signal: AbortSignal.timeout(300000),
      },
    );
  } catch {
    return NextResponse.json(
      { message: "Movena is temporarily unavailable." },
      { status: 503 },
    );
  }
  if (upstream.status >= 300 && upstream.status < 400)
    return NextResponse.json(
      { message: "Unexpected service response." },
      { status: 502 },
    );
  if (resource === "auth/login" && upstream.ok) {
    const result = await upstream.json();
    if (typeof result.access_token !== "string" || !result.user)
      return NextResponse.json(
        { message: "Invalid authentication response." },
        { status: 502 },
      );
    const response = NextResponse.json(
      { user: result.user },
      { headers: { "Cache-Control": "no-store" } },
    );
    response.cookies.set(COOKIE, result.access_token, {
      httpOnly: true,
      secure: process.env.NODE_ENV === "production",
      sameSite: "strict",
      path: "/",
      maxAge: Math.max(1, Math.min(Number(result.expires_in) || 3600, 86400)),
    });
    return response;
  }
  const response = new NextResponse(upstream.body, {
    status: upstream.status,
    headers: {
      "Content-Type":
        upstream.headers.get("content-type") || "application/json",
      "Cache-Control": "no-store",
    },
  });
  const disposition = upstream.headers.get("content-disposition");
  if (disposition) response.headers.set("Content-Disposition", disposition);
  if (upstream.status === 401 || (resource === "auth/logout" && upstream.ok))
    response.cookies.delete(COOKIE);
  return response;
}
export {
  forward as GET,
  forward as POST,
  forward as PATCH,
  forward as PUT,
  forward as DELETE,
};
