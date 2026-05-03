import type { Message } from "@/types";
import { CitationCard } from "@/components/chat/CitationCard";

interface Props {
  message: Message;
}

export function MessageBubble({ message }: Props) {
  const isUser = message.role === "user";

  return (
    <div className={`flex ${isUser ? "justify-end" : "justify-start"} mb-4`}>
      <div className={`max-w-2xl space-y-2 ${isUser ? "items-end" : "items-start"} flex flex-col`}>
        <div
          className={`px-4 py-2 rounded-lg text-sm ${
            isUser
              ? "bg-gray-900 text-white"
              : "bg-gray-100 text-gray-900"
          }`}
        >
          {message.content}
        </div>
        {message.citations && message.citations.length > 0 && (
          <div className="w-full space-y-1">
            {message.citations.map((citation, i) => (
              <CitationCard key={citation.chunk_id} citation={citation} index={i} />
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
