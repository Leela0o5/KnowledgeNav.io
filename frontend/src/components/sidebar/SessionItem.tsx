import { X, MessageSquare } from 'lucide-react';
import { motion } from 'motion/react';
import { cn } from '../../lib/utils';

export interface SessionItemProps {
  title: string;
  date: string;
  isActive: boolean;
  onClick: () => void;
  onDelete: () => void;
}

export default function SessionItem({ title, date, isActive, onClick, onDelete }: SessionItemProps) {
  return (
    <div
      className={cn(
        'w-full group flex items-center gap-3 px-3 py-3 rounded-xl transition-all duration-200 relative cursor-pointer',
        isActive ? 'bg-blue-500/10 text-white' : 'text-slate-400 hover:bg-white/5 hover:text-slate-200',
      )}
      onClick={onClick}
    >
      {isActive && (
        <motion.div
          layoutId="activeIndicator"
          className="absolute left-0 top-1/2 -translate-y-1/2 w-1 h-6 bg-blue-500 rounded-r-full"
        />
      )}

      <div
        className={cn(
          'shrink-0 w-8 h-8 rounded-lg flex items-center justify-center transition-colors',
          isActive ? 'bg-blue-500 text-white' : 'bg-slate-800 text-slate-500 group-hover:bg-slate-700',
        )}
      >
        <MessageSquare className="w-4 h-4" />
      </div>

      <div className="flex-1 text-left min-w-0">
        <div className="font-semibold text-sm truncate pr-7">{title}</div>
        <div className="text-[11px] text-slate-500 font-medium">{date}</div>
      </div>

      {/* Delete button — pure CSS hover, no framer-motion opacity override */}
      <button
        className="absolute right-2 p-1.5 rounded-md opacity-0 group-hover:opacity-100 hover:bg-red-500/20 hover:text-red-400 text-slate-500 transition-all duration-150"
        onClick={(e) => { e.stopPropagation(); onDelete(); }}
        title="Delete chat"
      >
        <X className="w-3.5 h-3.5" />
      </button>
    </div>
  );
}
