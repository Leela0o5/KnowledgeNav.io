import { motion } from 'motion/react';
import { User, BookOpen } from 'lucide-react';
import CitationCard from './CitationCard';
import MarkdownContent from './MarkdownContent';
import { Citation } from '../../lib/api';

export interface MessageBubbleProps {
  role: 'user' | 'assistant';
  content: string;
  citations?: Citation[];
  citationCoverage?: number | null;
}

function formatContent(raw: string, citations: Citation[]): string {
  const idToIndex = new Map(citations.map((c, i) => [c.chunk_id, i + 1]));
  return raw.replace(/\[SOURCE:([^\]]+)\]/g, (_match, inner: string) => {
    const ids = inner.split(',').map((s) => s.trim().replace(/^SOURCE:/, ''));
    const nums = ids.map((id) => idToIndex.get(id)).filter((n): n is number => n !== undefined);
    if (nums.length === 0) return '';
    return nums.map((n) => `<sup class="cite-ref">${n}</sup>`).join('');
  });
}

export default function MessageBubble({ role, content, citations = [], citationCoverage }: MessageBubbleProps) {
  const isAi = role === 'assistant';

  if (!isAi) {
    return (
      <motion.div
        initial={{ opacity: 0, y: 8 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.25 }}
        className="flex justify-end"
      >
        <div className="flex items-end gap-2.5 max-w-[80%]">
          <div className="bg-blue-600 text-white px-5 py-3.5 rounded-2xl rounded-br-sm shadow-lg shadow-blue-500/20 text-sm leading-relaxed font-medium">
            {content}
          </div>
          <div className="w-7 h-7 rounded-full bg-slate-200 flex items-center justify-center shrink-0 mb-0.5">
            <User className="w-3.5 h-3.5 text-slate-600" />
          </div>
        </div>
      </motion.div>
    );
  }

  const displayContent = formatContent(content, citations);

  return (
    <motion.div
      initial={{ opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
      className="flex items-start gap-3"
    >
      {/* AI avatar */}
      <div className="w-8 h-8 rounded-xl bg-linear-to-br from-blue-500 to-blue-600 flex items-center justify-center shrink-0 shadow-md shadow-blue-500/30 mt-0.5">
        <svg className="w-4 h-4 text-white" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={2.5}>
          <path strokeLinecap="round" strokeLinejoin="round" d="M9.813 15.904 9 18.75l-.813-2.846a4.5 4.5 0 0 0-3.09-3.09L2.25 12l2.846-.813a4.5 4.5 0 0 0 3.09-3.09L9 5.25l.813 2.846a4.5 4.5 0 0 0 3.09 3.09L15.75 12l-2.846.813a4.5 4.5 0 0 0-3.09 3.09Z" />
        </svg>
      </div>

      {/* AI message body */}
      <div className="flex-1 min-w-0 space-y-3">
        <MarkdownContent content={displayContent} />

        {citations.length > 0 && (
          <div className="pt-1">
            <div className="flex items-center gap-2 mb-2.5">
              <BookOpen className="w-3.5 h-3.5 text-blue-400" />
              <span className="text-[10px] font-bold text-blue-500 uppercase tracking-widest">Sources</span>
              {citationCoverage != null && (
                <span className="text-[10px] text-slate-400 font-medium tabular-nums">
                  · {Math.round(citationCoverage * 100)}% coverage
                </span>
              )}
            </div>
            <div className="grid grid-cols-2 gap-2 items-start">
              {citations.map((cite, i) => (
                <CitationCard key={cite.chunk_id} index={i} citation={cite} />
              ))}
            </div>
          </div>
        )}
      </div>
    </motion.div>
  );
}
