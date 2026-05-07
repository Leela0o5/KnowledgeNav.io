import { motion } from 'motion/react';
import MarkdownContent from './MarkdownContent';

interface StreamingMessageProps {
  content: string;
}

export default function StreamingMessage({ content }: StreamingMessageProps) {
  return (
    <div className="flex items-start gap-3">
      {/* AI avatar */}
      <div className="w-8 h-8 rounded-xl bg-linear-to-br from-blue-500 to-blue-600 flex items-center justify-center shrink-0 shadow-md shadow-blue-500/30 mt-0.5">
        <svg className="w-4 h-4 text-white" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={2.5}>
          <path strokeLinecap="round" strokeLinejoin="round" d="M9.813 15.904 9 18.75l-.813-2.846a4.5 4.5 0 0 0-3.09-3.09L2.25 12l2.846-.813a4.5 4.5 0 0 0 3.09-3.09L9 5.25l.813 2.846a4.5 4.5 0 0 0 3.09 3.09L15.75 12l-2.846.813a4.5 4.5 0 0 0-3.09 3.09Z" />
        </svg>
      </div>

      <div className="flex-1 min-w-0">
        {content ? (
          <div className="relative">
            <MarkdownContent content={content} />
            <motion.span
              animate={{ opacity: [1, 0] }}
              transition={{ repeat: Infinity, duration: 0.55, ease: 'linear' }}
              className="inline-block w-0.5 h-4 bg-blue-500 ml-0.5 rounded-full align-text-bottom"
            />
          </div>
        ) : (
          <div className="flex items-center gap-1.5 h-8">
            {[0, 1, 2].map((i) => (
              <motion.div
                key={i}
                animate={{ y: [0, -5, 0], opacity: [0.4, 1, 0.4] }}
                transition={{ repeat: Infinity, duration: 0.8, delay: i * 0.18, ease: 'easeInOut' }}
                className="w-1.5 h-1.5 bg-blue-400 rounded-full"
              />
            ))}
            <span className="text-xs text-slate-400 font-medium ml-1">Thinking…</span>
          </div>
        )}
      </div>
    </div>
  );
}
