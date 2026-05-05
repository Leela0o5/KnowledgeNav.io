import { type NextRequest, NextResponse } from "next/server";

const IS_SECURE = process.env.NEXT_PUBLIC_BASE_URL?.startsWith("https") ?? false;
const AT_COOKIE = IS_SECURE ? "__Secure-at" : "knav_at";

async function verifyToken(accessToken: string): Promise<boolean> {
  try {
    const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8080"}/auth/me`, {
      headers: { Cookie: `${AT_COOKIE}=${accessToken}` },
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
  const accessToken = request.cookies.get(AT_COOKIE)?.value;
  if (!accessToken) return redirectToLogin(request);
  const valid = await verifyToken(accessToken);
  if (!valid) return redirectToLogin(request);
  return NextResponse.next();
}

export const config = { matcher: ["/chat", "/chat/:path*", "/corpora", "/corpora/:path*", "/settings"] };
