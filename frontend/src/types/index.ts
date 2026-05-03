export interface User {
  id: string;
  email: string;
  name: string;
  avatar_url: string | null;
  role: string;
}

export interface Session {
  id: string;
  corpus_id: string;
  title: string | null;
  created_at: string;
  updated_at: string;
}

export interface Citation {
  chunk_id: string;
  source_file: string;
  page_range: string | null;
  excerpt: string;
}

export interface Message {
  id: string;
  session_id: string;
  role: "user" | "assistant";
  content: string;
  citations: Citation[] | null;
  citation_coverage: number | null;
  trace_id: string | null;
  created_at: string;
}

export interface Corpus {
  id: string;
  name: string;
}

export interface QueryResponse {
  answer: string;
  citations: Citation[];
  trace_id: string;
  citation_coverage: number;
  warning: string | null;
}

export interface CreateSessionBody {
  corpus_id: string;
  title?: string;
}

export interface IngestResponse {
  corpus_id: string;
  chunks_indexed: number;
}

export interface QueryParams {
  question: string;
  session_id: string;
}

export interface PaginatedResponse<T> {
  data: T[];
  next_cursor: string | null;
  has_more: boolean;
}
