import type { User } from "@/types";
import { ApiError } from "@/lib/api";

export async function getSession(): Promise<User | null> {
  try {
    const res = await fetch("/auth/me", { credentials: "include" });
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
