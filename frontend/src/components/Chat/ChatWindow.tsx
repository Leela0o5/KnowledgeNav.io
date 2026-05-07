import { useState, useEffect, useRef, useCallback } from 'react';
import { Sparkles, FileText, FolderOpen } from 'lucide-react';
import MessageBubble from './MessageBubble';
import InputBar from './InputBar';
import StreamingMessage from './StreamingMessage';
import { getMessages, createSession, queryStream, Message, Corpus } from '../../lib/api';

interface ChatWindowProps {
  sessionId: string | null;
  corpusId: string | null;
  corpus: Corpus | null;
  onSessionCreated: (id: string) => void;
}

export default function ChatWindow({ sessionId, corpusId, corpus, onSessionCreated }: ChatWindowProps) {
  const [messages, setMessages] = useState<Message[]>([]);
  const [loading, setLoading] = useState(false);
  const [streamingContent, setStreamingContent] = useState('');
  const [isStreaming, setIsStreaming] = useState(false);
  const bottomRef = useRef<HTMLDivElement>(null);
  const abortRef = useRef<(() => void) | null>(null);

  useEffect(() => {
    if (!sessionId) { setMessages([]); return; }
    setLoading(true);
    getMessages(sessionId)
      .then((res) => setMessages(res.data))
      .catch(() => setMessages([]))
      .finally(() => setLoading(false));
  }, [sessionId]);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, streamingContent]);

  useEffect(() => () => abortRef.current?.(), []);

  const handleSend = useCallback(
    async (question: string) => {
      if (isStreaming) return;
      let activeSessionId = sessionId;

      if (!activeSessionId) {
        if (!corpusId) return;
        try {
          const session = await createSession(corpusId, question.slice(0, 80));
          activeSessionId = session.id;
          onSessionCreated(session.id);
          window.dispatchEvent(new CustomEvent('session:created', { detail: session }));
        } catch { return; }
      }

      const userMsg: Message = {
        id: crypto.randomUUID(),
        session_id: activeSessionId,
        role: 'user',
        content: question,
        citations: null,
        citation_coverage: null,
        trace_id: null,
        created_at: new Date().toISOString(),
      };
      setMessages((prev) => [...prev, userMsg]);
      setIsStreaming(true);
      setStreamingContent('');

      abortRef.current = queryStream(
        question,
        activeSessionId,
        (token) => setStreamingContent((prev) => prev + token),
        (payload) => {
          setMessages((prev) => [
            ...prev,
            {
              id: crypto.randomUUID(),
              session_id: activeSessionId!,
              role: 'assistant',
              content: payload.answer,
              citations: payload.citations,
              citation_coverage: payload.citation_coverage,
              trace_id: payload.trace_id,
              created_at: new Date().toISOString(),
            },
          ]);
          setStreamingContent('');
          setIsStreaming(false);
        },
        (errMsg) => {
          setMessages((prev) => [
            ...prev,
            {
              id: crypto.randomUUID(),
              session_id: activeSessionId!,
              role: 'assistant',
              content: `Something went wrong: ${errMsg}`,
              citations: null,
              citation_coverage: null,
              trace_id: null,
              created_at: new Date().toISOString(),
            },
          ]);
          setStreamingContent('');
          setIsStreaming(false);
        },
      );
    },
    [sessionId, corpusId, isStreaming, onSessionCreated],
  );

  const hasCorpus = !!corpus;
  const canChat = hasCorpus || !!sessionId;

  return (
    <div className="flex flex-col h-full min-h-0 bg-slate-50">
      {/* Header — h-16 matches sidebar brand row exactly */}
      <header className="h-16 shrink-0 border-b border-slate-200 bg-white px-6 flex items-center justify-between">
        <div className="flex items-center gap-3 min-w-0">
          {corpus ? (
            <>
              <div className="w-8 h-8 rounded-lg bg-blue-100 flex items-center justify-center shrink-0">
                <FolderOpen className="w-4 h-4 text-blue-600" />
              </div>
              <div className="min-w-0">
                <div className="text-sm font-bold text-slate-800 truncate">{corpus.name}</div>
                <div className="flex items-center gap-1.5 mt-0.5">
                  <FileText className="w-3 h-3 text-slate-400" />
                  <span className="text-[10px] text-slate-400 font-medium font-mono truncate">{corpus.id}</span>
                </div>
              </div>
            </>
          ) : (
            <div className="flex items-center gap-2">
              <div className="w-8 h-8 rounded-lg bg-slate-100 flex items-center justify-center">
                <FolderOpen className="w-4 h-4 text-slate-400" />
              </div>
              <span className="text-sm text-slate-400 font-medium">No corpus selected</span>
            </div>
          )}
        </div>

        <div className="flex items-center gap-2 shrink-0">
          <div className={`w-2 h-2 rounded-full ${isStreaming ? 'bg-amber-400 animate-pulse' : 'bg-emerald-500'}`} />
          <span className="text-xs font-semibold text-slate-500">{isStreaming ? 'Generating…' : 'Ready'}</span>
        </div>
      </header>

      {/* Messages — only this region scrolls */}
      <div className="flex-1 min-h-0 overflow-y-auto custom-scrollbar scroll-smooth">
        <div className="flex flex-col items-center w-full py-10 px-4">
          <div className="w-full max-w-2xl space-y-8">

            {loading && (
              <div className="space-y-4">
                {[1, 2, 3].map((i) => (
                  <div key={i} className="h-16 bg-slate-100 rounded-2xl animate-pulse" />
                ))}
              </div>
            )}

            {messages.map((msg) => (
              <MessageBubble
                key={msg.id}
                role={msg.role}
                content={msg.content}
                citations={msg.citations ?? []}
                citationCoverage={msg.citation_coverage}
              />
            ))}

            {isStreaming && <StreamingMessage content={streamingContent} />}

            {!loading && !hasCorpus && !sessionId && (
              <div className="flex flex-col items-center justify-center py-24 text-center">
                <div className="w-20 h-20 bg-slate-100 rounded-3xl flex items-center justify-center mb-6">
                  <FolderOpen className="w-10 h-10 text-slate-300" />
                </div>
                <h3 className="text-xl font-bold text-slate-700 mb-2">No corpus selected</h3>
                <p className="text-slate-400 max-w-xs text-sm leading-relaxed">
                  Open the <span className="font-semibold text-blue-500">Documents</span> tab in the sidebar to select or upload a corpus, then start chatting.
                </p>
              </div>
            )}

            {!loading && hasCorpus && messages.length === 0 && !isStreaming && (
              <div className="flex flex-col items-center justify-center py-24 text-center">
                <div className="w-20 h-20 bg-blue-50 rounded-3xl flex items-center justify-center mb-6">
                  <Sparkles className="w-10 h-10 text-blue-300" />
                </div>
                <h3 className="text-xl font-bold text-slate-800 mb-2">How can I help you?</h3>
                <p className="text-slate-400 max-w-xs text-sm leading-relaxed">
                  Ask anything about <span className="font-semibold text-blue-600">{corpus!.name}</span>. Summarize, find details, or explore your documents.
                </p>
              </div>
            )}

            <div ref={bottomRef} />
          </div>
        </div>
      </div>

      {/* Input */}
      <div className="shrink-0 bg-linear-to-t from-slate-50 via-slate-50 to-transparent px-4 pb-6 pt-2">
        <div className="w-full max-w-2xl mx-auto">
          {!canChat && (
            <p className="text-center text-xs text-slate-400 font-medium mb-2">
              Select a corpus in the Documents tab to start chatting.
            </p>
          )}
          <InputBar onSend={handleSend} disabled={isStreaming || !canChat} />
          <p className="mt-3 text-center text-[10px] text-slate-400 font-bold uppercase tracking-widest">
            Powered by KnowledgeNav.io RAG Engine
          </p>
        </div>
      </div>
    </div>
  );
}
