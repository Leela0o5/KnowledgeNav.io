"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import type { Session } from "@/types";
import { useDeleteSession } from "@/hooks/useSessions";

interface Props {
  session: Session;
}

export function SessionItem({ session }: Props) {
  const pathname = usePathname();
  const deleteSession = useDeleteSession();
  const isActive = pathname === `/chat/${session.id}`;

  return (
    <div
      className={`group flex items-center justify-between px-3 py-2 rounded text-sm ${
        isActive ? "bg-gray-100 text-gray-900" : "text-gray-600 hover:bg-gray-50"
      }`}
    >
      <Link href={`/chat/${session.id}`} className="flex-1 truncate">
        {session.title ?? session.corpus_id}
      </Link>
      <button
        onClick={() => deleteSession.mutate(session.id)}
        className="hidden group-hover:block text-gray-400 hover:text-red-500 ml-1 text-xs"
      >
        x
      </button>
    </div>
  );
}
