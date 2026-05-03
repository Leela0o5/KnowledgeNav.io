"use client";

import Link from "next/link";
import { useSessions } from "@/hooks/useSessions";
import { SessionItem } from "@/components/sidebar/SessionItem";

export function SessionList() {
  const { data: sessions, isLoading } = useSessions();

  return (
    <div className="p-2 space-y-1">
      <Link
        href="/chat"
        className="block w-full text-center px-3 py-2 text-sm border border-gray-200 rounded hover:bg-gray-50"
      >
        New chat
      </Link>
      {isLoading && <p className="text-xs text-gray-400 px-3">Loading...</p>}
      {(sessions ?? []).map((session) => (
        <SessionItem key={session.id} session={session} />
      ))}
    </div>
  );
}
