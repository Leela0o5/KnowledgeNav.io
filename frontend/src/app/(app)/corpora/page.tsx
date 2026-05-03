"use client";

import { useRef } from "react";
import { useCorpora, useDeleteCorpus, useIngestCorpus } from "@/hooks/useCorpora";

export default function CorporaPage() {
  const { data: corpora, isLoading } = useCorpora();
  const ingest = useIngestCorpus();
  const deleteCorpus = useDeleteCorpus();
  const fileInputRef = useRef<HTMLInputElement>(null);
  const corpusIdRef = useRef<HTMLInputElement>(null);

  const handleUpload = async () => {
    const files = fileInputRef.current?.files;
    const corpusId = corpusIdRef.current?.value;
    if (!files || !corpusId || files.length === 0) return;

    const formData = new FormData();
    formData.append("corpus_id", corpusId);
    for (const file of Array.from(files)) {
      formData.append("files", file);
    }
    await ingest.mutateAsync(formData);
  };

  return (
    <div className="p-6 space-y-6">
      <h1 className="text-2xl font-semibold">Corpora</h1>
      <div className="border border-gray-200 rounded-md p-4 space-y-3">
        <h2 className="text-sm font-medium">Upload documents</h2>
        <input
          ref={corpusIdRef}
          type="text"
          placeholder="Corpus ID"
          className="w-full border border-gray-300 rounded px-3 py-1.5 text-sm"
        />
        <input ref={fileInputRef} type="file" multiple className="text-sm" />
        <button
          onClick={handleUpload}
          disabled={ingest.isPending}
          className="px-4 py-2 bg-gray-900 text-white rounded text-sm disabled:opacity-50"
        >
          {ingest.isPending ? "Uploading..." : "Upload"}
        </button>
      </div>
      <div className="space-y-2">
        {isLoading && <p className="text-gray-500 text-sm">Loading...</p>}
        {(corpora ?? []).map((corpus) => (
          <div
            key={corpus.id}
            className="flex items-center justify-between border border-gray-200 rounded px-4 py-2"
          >
            <span className="text-sm">{corpus.name}</span>
            <button
              onClick={() => deleteCorpus.mutate(corpus.id)}
              className="text-red-500 text-sm hover:underline"
            >
              Delete
            </button>
          </div>
        ))}
      </div>
    </div>
  );
}
