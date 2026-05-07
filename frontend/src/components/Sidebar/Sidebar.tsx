import { useState } from 'react';
import { MessageSquare, FolderOpen, LayoutGrid } from 'lucide-react';
import { cn } from '../../lib/utils';
import SessionList from './SessionList';
import SidebarFooter from './SidebarFooter';
import DocumentsPanel from './DocumentsPanel';
import { Corpus } from '../../lib/api';

interface SidebarProps {
  selectedSessionId: string | null;
  onSelectSession: (id: string | null) => void;
  selectedCorpusId: string | null;
  onSelectCorpus: (id: string) => void;
  corpora: Corpus[];
  onOpenUpload: () => void;
  onCorporaChange: () => void;
}

type Tab = 'chats' | 'documents';

export default function Sidebar({
  selectedSessionId,
  onSelectSession,
  selectedCorpusId,
  onSelectCorpus,
  corpora,
  onOpenUpload,
  onCorporaChange,
}: SidebarProps) {
  const [activeTab, setActiveTab] = useState<Tab>('chats');

  return (
    <aside className="w-72 h-full bg-[#0f172a] text-slate-300 flex flex-col shrink-0 border-r border-slate-800/60">

      {/* Brand — exactly h-16 to align with ChatWindow header */}
      <div className="h-16 flex items-center gap-3 px-5 border-b border-slate-800/60 shrink-0">
        <div className="w-8 h-8 bg-blue-500 rounded-xl flex items-center justify-center shadow-lg shadow-blue-500/20 shrink-0">
          <LayoutGrid className="text-white w-4 h-4" />
        </div>
        <span className="font-bold text-white text-base tracking-tight">KnowledgeNav.io</span>
      </div>

      {/* Tab Bar */}
      <div className="mx-4 mt-3 mb-2 p-1 bg-slate-800/60 rounded-xl grid grid-cols-2 gap-1 shrink-0">
        {([
          { key: 'chats',     label: 'Chats',     icon: MessageSquare },
          { key: 'documents', label: 'Documents',  icon: FolderOpen },
        ] as { key: Tab; label: string; icon: React.ElementType }[]).map(({ key, label, icon: Icon }) => (
          <button
            key={key}
            onClick={() => setActiveTab(key)}
            className={cn(
              'flex items-center justify-center gap-2 py-2 rounded-lg text-xs font-semibold transition-all duration-200',
              activeTab === key
                ? 'bg-blue-500 text-white shadow-sm'
                : 'text-slate-400 hover:text-slate-200',
            )}
          >
            <Icon className="w-3.5 h-3.5" />
            {label}
          </button>
        ))}
      </div>

      {/* Panel Content */}
      <div className="flex-1 flex flex-col min-h-0">
        {activeTab === 'chats' ? (
          <SessionList
            selectedSessionId={selectedSessionId}
            onSelectSession={onSelectSession}
            onSelectCorpus={onSelectCorpus}
            selectedCorpusId={selectedCorpusId}
          />
        ) : (
          <DocumentsPanel
            corpora={corpora}
            selectedCorpusId={selectedCorpusId}
            onSelectCorpus={(id) => {
              onSelectCorpus(id);
              onSelectSession(null);
              setActiveTab('chats');
            }}
            onOpenUpload={onOpenUpload}
            onCorporaChange={onCorporaChange}
          />
        )}
      </div>

      <SidebarFooter onOpenUpload={onOpenUpload} />
    </aside>
  );
}
