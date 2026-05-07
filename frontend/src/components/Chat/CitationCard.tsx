import { useState } from 'react';
import { ChevronDown, FileText } from 'lucide-react';
import { motion, AnimatePresence } from 'motion/react';
import { Citation } from '../../lib/api';

interface CitationCardProps {
  index: number;
  citation: Citation;
}

export default function CitationCard({ index, citation }: CitationCardProps) {
  const [isOpen, setIsOpen] = useState(false);
  const filename = citation.source_file.split(/[\\/]/).pop() ?? citation.source_file;

  return (
    <div className="bg-white border border-slate-200 rounded-xl overflow-hidden hover:border-blue-200 hover:shadow-sm transition-all duration-200">
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="w-full flex items-center gap-2.5 px-3 py-2.5 text-left"
      >
        <span className="flex-shrink-0 w-5 h-5 rounded-md bg-blue-600 text-white text-[10px] font-bold flex items-center justify-center">
          {index + 1}
        </span>
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-1.5">
            <FileText className="w-3 h-3 text-blue-400 shrink-0" />
            <span className="text-[11px] font-semibold text-slate-700 truncate">{filename}</span>
          </div>
          {citation.page_range && (
            <span className="text-[10px] text-slate-400 font-medium">p. {citation.page_range}</span>
          )}
        </div>
        <motion.div
          animate={{ rotate: isOpen ? 180 : 0 }}
          transition={{ duration: 0.2 }}
          className="shrink-0 text-slate-400"
        >
          <ChevronDown className="w-3.5 h-3.5" />
        </motion.div>
      </button>

      <AnimatePresence>
        {isOpen && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: 'auto', opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            transition={{ duration: 0.25, ease: 'easeInOut' }}
            className="overflow-hidden"
          >
            <div className="px-3 pb-3 pt-1 border-t border-slate-100">
              <p className="text-[11px] text-slate-500 italic leading-relaxed">
                "{citation.excerpt}"
              </p>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
