import { useEffect, useState } from 'react';
import { motion } from 'motion/react';
import { Database, CheckCircle2 } from 'lucide-react';
import { cn } from '../../lib/utils';
import { getCorpora, Corpus } from '../../lib/api';

interface CorpusGridProps {
  selectedCorpusId: string | null;
  onSelect: (id: string) => void;
}

export default function CorpusGrid({ selectedCorpusId, onSelect }: CorpusGridProps) {
  const [corpora, setCorpora] = useState<Corpus[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getCorpora()
      .then(setCorpora)
      .catch(() => setCorpora([]))
      .finally(() => setLoading(false));
  }, []);

  if (loading) {
    return (
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {[1, 2].map((i) => (
          <div key={i} className="h-28 bg-slate-100 rounded-2xl animate-pulse" />
        ))}
      </div>
    );
  }

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
      {corpora.map((corpus, index) => {
        const isSelected = selectedCorpusId === corpus.id;
        return (
          <motion.button
            key={corpus.id}
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ delay: index * 0.08 }}
            onClick={() => onSelect(corpus.id)}
            className={cn(
              'p-5 rounded-2xl border-2 text-left transition-all duration-300 relative group',
              isSelected
                ? 'border-blue-500 bg-blue-50/50 shadow-lg shadow-blue-500/10'
                : 'border-slate-100 bg-white hover:border-slate-200 hover:shadow-sm',
            )}
          >
            <div className="flex items-start justify-between mb-4">
              <div
                className={cn(
                  'w-12 h-12 rounded-xl flex items-center justify-center transition-colors',
                  isSelected
                    ? 'bg-blue-600 text-white'
                    : 'bg-slate-50 text-slate-400 group-hover:bg-slate-100',
                )}
              >
                <Database className="w-6 h-6" />
              </div>
              {isSelected && <CheckCircle2 className="w-5 h-5 text-blue-600" />}
            </div>

            <div>
              <h4 className="font-bold text-slate-900">{corpus.name}</h4>
              <p className="text-xs text-slate-500 mt-1 leading-relaxed">
                ID: {corpus.id}
              </p>
            </div>
          </motion.button>
        );
      })}

      {corpora.length === 0 && (
        <div className="col-span-full py-10 border-2 border-dashed border-slate-200 rounded-2xl flex flex-col items-center justify-center text-slate-400">
          <Database className="w-10 h-10 mb-4 opacity-20" />
          <p className="text-sm font-medium">No corpora yet. Upload documents first.</p>
        </div>
      )}
    </div>
  );
}
