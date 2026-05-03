"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { useCreateSession } from "@/hooks/useSessions";
import { useCorpora } from "@/hooks/useCorpora";

export default function NewChatPage() {
  const router = useRouter();
  const { data: corpora, isLoading } = useCorpora();
  const createSession = useCreateSession();
  const [selectedCorpusId, setSelectedCorpusId] = useState("");

  const handleStart = async () => {
    if (!selectedCorpusId) return;
    const session = await createSession.mutateAsync({ corpus_id: selectedCorpusId });
    router.push(`/chat/${session.id}`);
  };

  return (
    <div className="flex flex-col items-center justify-center h-full space-y-6 px-4">
      <h2 className="text-2xl font-semibold text-foreground">Start a new conversation</h2>
      {isLoading ? (
        <p className="text-gray-500">Loading corpora...</p>
      ) : (
        <div className="w-full max-w-sm space-y-4">
          <select
            className="w-full border border-gray-300 rounded-md px-3 py-2 text-sm"
            value={selectedCorpusId}
            onChange={(e) => setSelectedCorpusId(e.target.value)}
          >
            <option value="">Select a corpus</option>
            {(corpora ?? []).map((corpus) => (
              <option key={corpus.id} value={corpus.id}>
                {corpus.name}
              </option>
            ))}
          </select>
          <button
            onClick={handleStart}
            disabled={!selectedCorpusId || createSession.isPending}
            className="w-full px-4 py-2 bg-gray-900 text-white rounded-md text-sm font-medium disabled:opacity-50"
          >
            {createSession.isPending ? "Starting..." : "Start chat"}
          </button>
        </div>
      )}
    </div>
  );
}
