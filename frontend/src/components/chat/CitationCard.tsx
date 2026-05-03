"use client";

import { useState } from "react";
import type { Citation } from "@/types";

interface Props {
  citation: Citation;
  index: number;
}

export function CitationCard({ citation, index }: Props) {
  const [expanded, setExpanded] = useState(false);

  return (
    <div className="border border-gray-200 rounded text-xs">
      <button
        onClick={() => setExpanded((v) => !v)}
        className="w-full flex items-center justify-between px-3 py-2 text-left hover:bg-gray-50"
      >
        <span className="font-medium text-gray-700">
          [{index + 1}] {citation.source_file.split("/").pop()}
          {citation.page_range ? ` (p. ${citation.page_range})` : ""}
        </span>
        <span className="text-gray-400">{expanded ? "-" : "+"}</span>
      </button>
      {expanded && (
        <div className="px-3 py-2 border-t border-gray-100 text-gray-600">
          {citation.excerpt}
        </div>
      )}
    </div>
  );
}
