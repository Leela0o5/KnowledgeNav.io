"use client";

import { useEffect, useRef } from "react";
import { useChat } from "@/hooks/useChat";
import { MessageBubble } from "@/components/chat/MessageBubble";
import { StreamingMessage } from "@/components/chat/StreamingMessage";
import { InputBar } from "@/components/chat/InputBar";

interface Props {
  sessionId: string;
}

export function ChatWindow({ sessionId }: Props) {
  const { messages, streamingContent, isStreaming, sendMessage } = useChat(sessionId);
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, streamingContent]);

  return (
    <div className="flex flex-col h-full">
      <div className="flex-1 overflow-y-auto p-4">
        {messages.map((message) => (
          <MessageBubble key={message.id} message={message} />
        ))}
        {isStreaming && <StreamingMessage content={streamingContent} />}
        <div ref={bottomRef} />
      </div>
      <InputBar onSubmit={sendMessage} disabled={isStreaming} />
    </div>
  );
}
