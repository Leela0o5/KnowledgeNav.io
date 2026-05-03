import { type NextRequest, NextResponse } from "next/server";

async function verifyToken(accessToken: string): Promise<boolean> {
  try {
    const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8080"}/auth/me`, {
      headers: { Cookie: `__Secure-at=${accessToken}` },
    });
    return res.ok;
  } catch {
    return false;
  }
}

function redirectToLogin(request: NextRequest): NextResponse {
  return NextResponse.redirect(new URL("/", request.url));
}

export async function middleware(request: NextRequest): Promise<NextResponse> {
  const accessToken = request.cookies.get("__Secure-at")?.value;
  if (!accessToken) return redirectToLogin(request);
  const valid = await verifyToken(accessToken);
  if (!valid) return redirectToLogin(request);
  return NextResponse.next();
}

export const config = { matcher: ["/(app)/:path*"] };
