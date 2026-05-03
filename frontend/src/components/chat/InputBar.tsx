"use client";

import { type KeyboardEvent, useState } from "react";

interface Props {
  onSubmit: (question: string) => void;
  disabled: boolean;
}

export function InputBar({ onSubmit, disabled }: Props) {
  const [value, setValue] = useState("");

  const handleKeyDown = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      if (value.trim() && !disabled) {
        onSubmit(value.trim());
        setValue("");
      }
    }
  };

  return (
    <div className="border-t border-gray-200 p-4">
      <textarea
        value={value}
        onChange={(e) => setValue(e.target.value)}
        onKeyDown={handleKeyDown}
        disabled={disabled}
        rows={2}
        placeholder="Ask a question... (Enter to send, Shift+Enter for new line)"
        className="w-full resize-none border border-gray-300 rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-1 focus:ring-gray-400 disabled:opacity-50"
      />
    </div>
  );
}
