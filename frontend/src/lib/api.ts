// In dev the Vite proxy handles /api and /auth, so BASE is empty.
// In production set VITE_API_BASE to the Railway backend URL.
const BASE: string = (import.meta.env.VITE_API_BASE as string | undefined) ?? '';
export const BACKEND_ORIGIN = BASE || 'http://localhost:8080';

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
  role: 'user' | 'assistant';
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

export interface IngestResponse {
  corpus_id: string;
  chunks_indexed: number;
}

export interface DonePayload {
  answer: string;
  citations: Citation[];
  trace_id: string;
  citation_coverage: number;
  warning: string | null;
}

async function fetchJson<T>(url: string, options?: RequestInit): Promise<T> {
  const res = await fetch(url, { credentials: 'include', ...options });
  if (!res.ok) throw res;
  return res.json();
}


export const getMe = () => fetchJson<User>(`${BASE}/auth/me`);

export const logout = () =>
  fetch(`${BASE}/auth/logout`, { method: 'POST', credentials: 'include' });

export const refreshToken = () =>
  fetch(`${BASE}/auth/refresh`, { method: 'POST', credentials: 'include' });


export const getSessions = () =>
  fetchJson<{ data: Session[]; has_more: boolean }>(`${BASE}/api/v1/sessions`);

export const createSession = (corpus_id: string, title?: string) =>
  fetchJson<Session>(`${BASE}/api/v1/sessions`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ corpus_id, title }),
  });

export const deleteSession = (id: string) =>
  fetch(`${BASE}/api/v1/sessions/${id}`, { method: 'DELETE', credentials: 'include' });

export const getMessages = (sessionId: string, cursor?: string, limit = 50) => {
  const params = new URLSearchParams({ limit: String(limit) });
  if (cursor) params.set('cursor', cursor);
  return fetchJson<{ data: Message[]; next_cursor: string | null; has_more: boolean }>(
    `${BASE}/api/v1/sessions/${sessionId}/messages?${params}`,
  );
};

export interface DocumentInfo {
  source_file: string;
  chunk_count: number;
}


export const getCorpora = () => fetchJson<Corpus[]>(`${BASE}/api/v1/corpora`);

export const getCorpusDocuments = (corpusId: string) =>
  fetchJson<DocumentInfo[]>(`${BASE}/api/v1/corpora/${corpusId}/documents`);

export const deleteCorpusDocument = (corpusId: string, sourceFile: string) =>
  fetch(
    `${BASE}/api/v1/corpora/${corpusId}/documents?source_file=${encodeURIComponent(sourceFile)}`,
    { method: 'DELETE', credentials: 'include' },
  );

export const deleteCorpus = (id: string) =>
  fetch(`${BASE}/api/v1/corpora/${id}`, { method: 'DELETE', credentials: 'include' });

export const ingestFiles = (corpus_id: string, files: File[], overwrite = false) => {
  const form = new FormData();
  form.append('corpus_id', corpus_id);
  form.append('overwrite', String(overwrite));
  files.forEach((f) => form.append('files', f));
  return fetchJson<IngestResponse>(`${BASE}/api/v1/ingest`, { method: 'POST', body: form });
};

export const queryStream = (
  question: string,
  session_id: string,
  onToken: (token: string) => void,
  onDone: (payload: DonePayload) => void,
  onError: (msg: string) => void,
): (() => void) => {
  const params = new URLSearchParams({ question, session_id });
  const controller = new AbortController();

  (async () => {
    try {
      const res = await fetch(`${BASE}/api/v1/query?${params}`, {
        credentials: 'include',
        signal: controller.signal,
      });

      if (!res.ok || !res.body) {
        onError(`Request failed: ${res.status}`);
        return;
      }

      const reader = res.body.getReader();
      const decoder = new TextDecoder();
      let buffer = '';
      let currentEvent = '';

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        buffer += decoder.decode(value, { stream: true });

        const lines = buffer.split('\n');
        buffer = lines.pop() ?? '';

        for (const line of lines) {
          if (line.startsWith('event: ')) {
            currentEvent = line.slice(7).trim();
          } else if (line.startsWith('data: ')) {
            const data = line.slice(6);
            if (currentEvent === 'token') onToken(data);
            else if (currentEvent === 'done') {
              try { onDone(JSON.parse(data)); } catch { onError('Malformed done payload'); }
            } else if (currentEvent === 'error') onError(data);
            currentEvent = '';
          }
        }
      }
    } catch (e: any) {
      if (e?.name !== 'AbortError') onError(String(e));
    }
  })();

  return () => controller.abort();
};
