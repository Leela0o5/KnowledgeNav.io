"use client";

import { useRef, useState } from "react";
import { useQueryClient } from "@tanstack/react-query";
import { logout } from "@/lib/auth";
import { useIngestCorpus } from "@/hooks/useCorpora";

interface Props {
  email: string;
}

export function SidebarFooter({ email }: Props) {
  const queryClient = useQueryClient();
  const fileInputRef = useRef<HTMLInputElement>(null);
  const ingest = useIngestCorpus();
  const [uploading, setUploading] = useState(false);

  async function handleFiles(e: React.ChangeEvent<HTMLInputElement>) {
    const files = e.target.files;
    if (!files || files.length === 0) return;
    const corpusId = prompt("Enter a corpus name (e.g. my-docs):");
    if (!corpusId?.trim()) return;

    setUploading(true);
    const formData = new FormData();
    formData.append("corpus_id", corpusId.trim());
    for (const file of Array.from(files)) {
      formData.append("files", file);
    }
    try {
      await ingest.mutateAsync(formData);
    } finally {
      setUploading(false);
      if (fileInputRef.current) fileInputRef.current.value = "";
    }
  }

  return (
    <div className="p-4 border-t border-gray-200 space-y-2">
      <p className="text-xs text-gray-500 truncate">{email}</p>
      <input
        ref={fileInputRef}
        type="file"
        multiple
        accept=".pdf,.txt,.md,.html,.htm,.docx"
        className="hidden"
        onChange={handleFiles}
      />
      <button
        onClick={() => fileInputRef.current?.click()}
        disabled={uploading}
        className="w-full text-xs px-3 py-1.5 border border-gray-200 rounded hover:bg-gray-50 disabled:opacity-50"
      >
        {uploading ? "Uploading..." : "Upload documents"}
      </button>
      <button
        onClick={() => logout(() => queryClient.clear())}
        className="w-full text-xs px-3 py-1.5 border border-gray-200 rounded hover:bg-gray-50 text-gray-600"
      >
        Log out
      </button>
    </div>
  );
}
