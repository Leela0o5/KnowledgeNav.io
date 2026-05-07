import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'motion/react';
import { Database, CheckCircle2, Upload, Trash2, RefreshCw, FileText, ChevronDown, Loader2 } from 'lucide-react';
import { cn } from '../../lib/utils';
import { deleteCorpus, deleteCorpusDocument, getCorpusDocuments, DocumentInfo, Corpus } from '../../lib/api';

interface DocumentsPanelProps {
  corpora: Corpus[];
  selectedCorpusId: string | null;
  onSelectCorpus: (id: string) => void;
  onOpenUpload: () => void;
  onCorporaChange: () => void;
}

function CorpusRow({
  corpus,
  isSelected,
  onSelect,
  onDelete,
  deletingId,
}: {
  corpus: Corpus;
  isSelected: boolean;
  onSelect: () => void;
  onDelete: (e: React.MouseEvent) => void;
  deletingId: string | null;
}) {
  const [expanded, setExpanded] = useState(false);
  const [docs, setDocs] = useState<DocumentInfo[]>([]);
  const [loadingDocs, setLoadingDocs] = useState(false);
  const [deletingDoc, setDeletingDoc] = useState<string | null>(null);

  const fetchDocs = () => {
    setLoadingDocs(true);
    getCorpusDocuments(corpus.id)
      .then(setDocs)
      .catch(() => setDocs([]))
      .finally(() => setLoadingDocs(false));
  };

  const toggleExpand = (e: React.MouseEvent) => {
    e.stopPropagation();
    if (!expanded) fetchDocs();
    setExpanded((v) => !v);
  };

  const handleDeleteDoc = async (sourceFile: string, e: React.MouseEvent) => {
    e.stopPropagation();
    if (!confirm(`Delete "${sourceFile.split(/[\\/]/).pop()}" and all its chunks from this corpus?`)) return;
    setDeletingDoc(sourceFile);
    try {
      await deleteCorpusDocument(corpus.id, sourceFile);
      setDocs((prev) => prev.filter((d) => d.source_file !== sourceFile));
    } catch {
      // ignore
    } finally {
      setDeletingDoc(null);
    }
  };

  return (
    <div
      className={cn(
        'rounded-xl border transition-all duration-200',
        isSelected
          ? 'bg-blue-500/10 border-blue-500/30'
          : 'bg-slate-800/50 border-slate-700/50',
      )}
    >
      {/* Corpus header row */}
      <div
        className={cn(
          'group flex items-center gap-2 p-3 cursor-pointer rounded-xl',
          isSelected ? 'text-white' : 'text-slate-400 hover:text-slate-200',
        )}
        onClick={onSelect}
      >
        <div
          className={cn(
            'w-7 h-7 rounded-lg flex items-center justify-center shrink-0 transition-colors',
            isSelected ? 'bg-blue-500 text-white' : 'bg-slate-700 text-slate-400',
          )}
        >
          <Database className="w-3.5 h-3.5" />
        </div>

        <div className="flex-1 min-w-0">
          <div className="text-sm font-semibold truncate">{corpus.name}</div>
        </div>

        {isSelected && <CheckCircle2 className="w-3.5 h-3.5 text-blue-400 shrink-0" />}

        {/* Expand toggle */}
        <button
          onClick={toggleExpand}
          className="p-1 rounded hover:bg-slate-700/60 text-slate-500 hover:text-slate-300 transition-colors shrink-0"
          title="Show documents"
        >
          <motion.div animate={{ rotate: expanded ? 180 : 0 }} transition={{ duration: 0.2 }}>
            <ChevronDown className="w-3.5 h-3.5" />
          </motion.div>
        </button>

        {/* Delete */}
        <button
          onClick={onDelete}
          disabled={deletingId === corpus.id}
          className="p-1 rounded opacity-0 group-hover:opacity-100 hover:bg-red-500/20 hover:text-red-400 text-slate-500 transition-all shrink-0"
          title="Delete corpus"
        >
          {deletingId === corpus.id ? (
            <Loader2 className="w-3.5 h-3.5 animate-spin" />
          ) : (
            <Trash2 className="w-3.5 h-3.5" />
          )}
        </button>
      </div>

      {/* Documents list */}
      <AnimatePresence>
        {expanded && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: 'auto', opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            transition={{ duration: 0.25, ease: 'easeInOut' }}
            className="overflow-hidden"
          >
            <div className="px-3 pb-3 pt-1 border-t border-slate-700/40">
              {loadingDocs ? (
                <div className="flex items-center gap-2 py-2 text-slate-500 text-xs">
                  <Loader2 className="w-3 h-3 animate-spin" />
                  Loading documents…
                </div>
              ) : docs.length === 0 ? (
                <p className="text-xs text-slate-600 py-2">No documents found.</p>
              ) : (
                <ul className="space-y-1 mt-1">
                  {docs.map((doc) => {
                    const filename = doc.source_file.split(/[\\/]/).pop() ?? doc.source_file;
                    const isDeleting = deletingDoc === doc.source_file;
                    return (
                      <li
                        key={doc.source_file}
                        className="group flex items-center gap-2 text-xs text-slate-400 bg-slate-800/60 rounded-lg px-2.5 py-1.5"
                      >
                        <FileText className="w-3 h-3 text-blue-400 shrink-0" />
                        <span className="flex-1 truncate font-medium" title={doc.source_file}>
                          {filename}
                        </span>
                        <span className="text-slate-600 shrink-0 tabular-nums mr-1">
                          {doc.chunk_count} chunks
                        </span>
                        <button
                          onClick={(e) => handleDeleteDoc(doc.source_file, e)}
                          disabled={isDeleting}
                          className="opacity-0 group-hover:opacity-100 p-0.5 rounded hover:bg-red-500/20 hover:text-red-400 transition-all shrink-0"
                          title="Delete document"
                        >
                          {isDeleting
                            ? <Loader2 className="w-3 h-3 animate-spin" />
                            : <Trash2 className="w-3 h-3" />
                          }
                        </button>
                      </li>
                    );
                  })}
                </ul>
              )}
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}

export default function DocumentsPanel({
  corpora,
  selectedCorpusId,
  onSelectCorpus,
  onOpenUpload,
  onCorporaChange,
}: DocumentsPanelProps) {
  const [deletingId, setDeletingId] = useState<string | null>(null);

  const handleDelete = async (id: string, e: React.MouseEvent) => {
    e.stopPropagation();
    if (!confirm(`Delete corpus "${id}" and all its documents? This cannot be undone.`)) return;
    setDeletingId(id);
    try {
      await deleteCorpus(id);
      onCorporaChange();
    } catch {
      // ignore
    } finally {
      setDeletingId(null);
    }
  };

  return (
    <div className="flex-1 flex flex-col min-h-0 overflow-hidden">
      {/* Actions */}
      <div className="px-4 py-3 flex gap-2 shrink-0">
        <button
          onClick={onOpenUpload}
          className="flex-1 flex items-center justify-center gap-2 py-2 rounded-lg bg-blue-500/10 border border-blue-500/20 text-blue-400 hover:bg-blue-500 hover:text-white transition-all duration-200 text-xs font-semibold"
        >
          <Upload className="w-3.5 h-3.5" />
          Upload Docs
        </button>
        <button
          onClick={onCorporaChange}
          className="p-2 rounded-lg bg-slate-800 text-slate-400 hover:bg-slate-700 hover:text-white transition-colors"
          title="Refresh"
        >
          <RefreshCw className="w-3.5 h-3.5" />
        </button>
      </div>

      {/* Corpus list */}
      <div className="flex-1 overflow-y-auto px-4 pb-4 space-y-2 custom-scrollbar dark-sidebar-scroll">
        {corpora.length === 0 ? (
          <div className="flex flex-col items-center justify-center py-12 text-center px-4">
            <Database className="w-10 h-10 text-slate-700 mb-3" />
            <p className="text-xs text-slate-500 font-medium">No corpora yet.</p>
            <p className="text-xs text-slate-600 mt-1">Upload documents to create one.</p>
          </div>
        ) : (
          corpora.map((corpus, i) => (
            <motion.div
              key={corpus.id}
              initial={{ opacity: 0, x: -8 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: i * 0.05 }}
            >
              <CorpusRow
                corpus={corpus}
                isSelected={selectedCorpusId === corpus.id}
                onSelect={() => onSelectCorpus(corpus.id)}
                onDelete={(e) => handleDelete(corpus.id, e)}
                deletingId={deletingId}
              />
            </motion.div>
          ))
        )}
      </div>

      {/* Active corpus indicator */}
      {selectedCorpusId && (
        <div className="px-4 py-3 border-t border-slate-800/60 shrink-0">
          <p className="text-[10px] text-slate-500 uppercase tracking-widest font-bold mb-1">Active for new chats</p>
          <div className="flex items-center gap-2">
            <div className="w-2 h-2 rounded-full bg-blue-500" />
            <span className="text-xs text-blue-300 font-semibold truncate">
              {corpora.find((c) => c.id === selectedCorpusId)?.name ?? selectedCorpusId}
            </span>
          </div>
        </div>
      )}
    </div>
  );
}
