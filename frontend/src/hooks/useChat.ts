"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { api } from "@/lib/api";
import { streamQuery } from "@/lib/sse";
import type { Citation, Message, QueryResponse } from "@/types";

interface ChatState {
  messages: Message[];
  streamingContent: string;
  isStreaming: boolean;
  streamingCitations: Citation[];
}

export function useChat(sessionId: string) {
  const [state, setState] = useState<ChatState>({
    messages: [],
    streamingContent: "",
    isStreaming: false,
    streamingCitations: [],
  });

  const cleanupRef = useRef<(() => void) | null>(null);

  const { data: historicalMessages } = useQuery({
    queryKey: ["messages", sessionId],
    queryFn: () => api.sessions.messages(sessionId),
    select: (data) => data.data,
    enabled: !!sessionId,
  });

  useEffect(() => {
    if (historicalMessages) {
      setState((prev) => ({ ...prev, messages: historicalMessages }));
    }
  }, [historicalMessages]);

  useEffect(() => {
    return () => {
      cleanupRef.current?.();
    };
  }, []);

  const sendMessage = useCallback(
    (question: string) => {
      const userMessage: Message = {
        id: crypto.randomUUID(),
        session_id: sessionId,
        role: "user",
        content: question,
        citations: null,
        citation_coverage: null,
        trace_id: null,
        created_at: new Date().toISOString(),
      };

      setState((prev) => ({
        ...prev,
        messages: [...prev.messages, userMessage],
        streamingContent: "",
        isStreaming: true,
        streamingCitations: [],
      }));

      const onToken = (token: string) => {
        setState((prev) => ({
          ...prev,
          streamingContent: prev.streamingContent + token,
        }));
      };

      const onDone = (response: QueryResponse) => {
        const assistantMessage: Message = {
          id: crypto.randomUUID(),
          session_id: sessionId,
          role: "assistant",
          content: response.answer,
          citations: response.citations,
          citation_coverage: response.citation_coverage,
          trace_id: response.trace_id,
          created_at: new Date().toISOString(),
        };
        setState((prev) => ({
          ...prev,
          messages: [...prev.messages, assistantMessage],
          streamingContent: "",
          isStreaming: false,
          streamingCitations: [],
        }));
      };

      const onError = () => {
        setState((prev) => ({
          ...prev,
          streamingContent: "",
          isStreaming: false,
          streamingCitations: [],
        }));
      };

      cleanupRef.current = streamQuery({ question, session_id: sessionId }, onToken, onDone, onError);
    },
    [sessionId],
  );

  return {
    messages: state.messages,
    streamingContent: state.streamingContent,
    isStreaming: state.isStreaming,
    sendMessage,
  };
}
