import { cookies } from "next/headers";
import type { User } from "@/types";

const IS_SECURE = process.env.NEXT_PUBLIC_BASE_URL?.startsWith("https") ?? false;
const AT_COOKIE = IS_SECURE ? "__Secure-at" : "knav_at";
const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8080";

export async function getSession(): Promise<User | null> {
  try {
    const cookieStore = await cookies();
    const token = cookieStore.get(AT_COOKIE);
    if (!token) return null;
    const res = await fetch(`${API_URL}/auth/me`, {
      headers: { Cookie: `${AT_COOKIE}=${token.value}` },
      cache: "no-store",
    });
    if (!res.ok) return null;
    return res.json() as Promise<User>;
  } catch {
    return null;
  }
}

export function getLoginUrl(provider: "google" | "github"): string {
  return `/auth/${provider}`;
}

export async function logout(queryClientClear: () => void): Promise<void> {
  await fetch("/auth/logout", { method: "POST", credentials: "include" });
  queryClientClear();
  window.location.href = "/";
}
