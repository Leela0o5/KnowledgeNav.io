import { useEffect, useState } from 'react';
import { Plus } from 'lucide-react';
import { motion } from 'motion/react';
import SessionItem from './SessionItem';
import { getSessions, deleteSession, Session } from '../../lib/api';

interface SessionListProps {
  selectedSessionId: string | null;
  onSelectSession: (id: string | null) => void;
  onSelectCorpus: (corpusId: string) => void;
  selectedCorpusId: string | null;
}

function formatDate(iso: string) {
  const d = new Date(iso);
  const now = new Date();
  const diffHrs = (now.getTime() - d.getTime()) / 3600000;
  if (diffHrs < 1) return 'Just now';
  if (diffHrs < 24) return `${Math.floor(diffHrs)}h ago`;
  if (diffHrs < 48) return 'Yesterday';
  return d.toLocaleDateString();
}

export default function SessionList({ selectedSessionId, onSelectSession, onSelectCorpus, selectedCorpusId }: SessionListProps) {
  const [sessions, setSessions] = useState<Session[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getSessions()
      .then((res) => setSessions(res.data))
      .catch(() => setSessions([]))
      .finally(() => setLoading(false));
  }, []);

  useEffect(() => {
    const handler = (e: CustomEvent<Session>) => {
      setSessions((prev) => {
        if (prev.some((s) => s.id === e.detail.id)) return prev;
        return [e.detail, ...prev];
      });
    };
    window.addEventListener('session:created', handler as EventListener);
    return () => window.removeEventListener('session:created', handler as EventListener);
  }, []);

  const handleNew = () => onSelectSession(null);

  const handleDelete = async (sessionId: string) => {
    await deleteSession(sessionId);
    setSessions((prev) => prev.filter((s) => s.id !== sessionId));
    if (selectedSessionId === sessionId) onSelectSession(null);
  };

  return (
    <div className="flex-1 overflow-y-auto px-4 py-2 custom-scrollbar dark-sidebar-scroll space-y-1">
      {/* New Conversation */}
      <button
        onClick={handleNew}
        className="w-full flex items-center gap-3 px-3 py-3 rounded-xl bg-blue-500/10 border border-blue-500/20 text-blue-400 hover:bg-blue-500 hover:text-white transition-all duration-300 group mb-4"
      >
        <motion.div
          whileHover={{ rotate: 90 }}
          transition={{ type: 'spring', stiffness: 300 }}
          className="w-5 h-5 rounded-full bg-blue-500/20 flex items-center justify-center group-hover:bg-white/20"
        >
          <Plus className="w-3 h-3" />
        </motion.div>
        <span className="text-sm font-semibold">New conversation</span>
      </button>

      {/* Session Items */}
      {loading ? (
        <div className="space-y-4 px-3 py-2">
          {[1, 2, 3].map((i) => (
            <div key={i} className="flex flex-col gap-2">
              <div className="h-4 w-3/4 bg-slate-800 rounded animate-pulse" />
              <div className="h-3 w-1/4 bg-slate-800/50 rounded animate-pulse" />
            </div>
          ))}
        </div>
      ) : sessions.length === 0 ? (
        <p className="text-center text-xs text-slate-600 py-6 font-medium">No conversations yet.</p>
      ) : (
        sessions.map((session) => (
          <SessionItem
            key={session.id}
            title={session.title ?? 'Untitled'}
            date={formatDate(session.updated_at)}
            isActive={selectedSessionId === session.id}
            onClick={() => {
              onSelectSession(session.id);
              onSelectCorpus(session.corpus_id);
            }}
            onDelete={() => handleDelete(session.id)}
          />
        ))
      )}
    </div>
  );
}
