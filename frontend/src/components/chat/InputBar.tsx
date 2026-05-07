import { useState, useRef, useEffect, KeyboardEvent } from 'react';
import { Send, Paperclip } from 'lucide-react';
import { motion } from 'motion/react';

interface InputBarProps {
  onSend: (text: string) => void;
  disabled?: boolean;
}

export default function InputBar({ onSend, disabled = false }: InputBarProps) {
  const [text, setText] = useState('');
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      textareaRef.current.style.height = `${Math.min(textareaRef.current.scrollHeight, 200)}px`;
    }
  }, [text]);

  const handleSend = () => {
    const trimmed = text.trim();
    if (!trimmed || disabled) return;
    onSend(trimmed);
    setText('');
  };

  const handleKeyDown = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div className="relative group animate-slide-up">
      <div className="absolute -inset-1 bg-linear-to-r from-blue-500/20 to-blue-500/20 rounded-[26px] blur opacity-0 group-focus-within:opacity-100 transition duration-1000" />

      <div className="relative flex items-end gap-2 p-3 bg-white border border-slate-200 rounded-2xl shadow-xl shadow-slate-200/50 group-focus-within:border-blue-400 group-focus-within:shadow-[0_0_8px_2px_rgba(59,130,246,0.5)] transition-all duration-300">
        <button className="p-2.5 rounded-xl hover:bg-slate-50 text-slate-400 hover:text-blue-500 transition-colors self-end">
          <Paperclip className="w-5 h-5" />
        </button>

        <textarea
          ref={textareaRef}
          rows={1}
          value={text}
          onChange={(e) => setText(e.target.value)}
          onKeyDown={handleKeyDown}
          disabled={disabled}
          placeholder={disabled ? 'Waiting for response…' : 'Ask me anything… (Enter to send)'}
          className="flex-1 max-h-50 py-2.5 px-1 bg-transparent border-none focus:ring-0 focus:outline-none text-slate-700 placeholder:text-slate-400 resize-none font-medium leading-normal scrollbar-hide disabled:opacity-50"
        />

        <div className="flex items-center gap-1 self-end">
          <motion.button
            whileTap={{ scale: 0.95 }}
            onClick={handleSend}
            disabled={!text.trim() || disabled}
            className={`p-2.5 rounded-xl flex items-center justify-center transition-all duration-300 ${
              text.trim() && !disabled
                ? 'bg-blue-600 text-white shadow-lg shadow-blue-200'
                : 'bg-slate-100 text-slate-400 cursor-not-allowed'
            }`}
          >
            <Send className={`w-5 h-5 ${text.trim() && !disabled ? 'translate-x-0.5 -translate-y-0.5' : ''}`} />
          </motion.button>
        </div>
      </div>
    </div>
  );
}
