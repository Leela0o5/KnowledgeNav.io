import type {
  Corpus,
  CreateSessionBody,
  IngestResponse,
  Message,
  PaginatedResponse,
  Session,
  User,
} from "@/types";

export class ApiError extends Error {
  constructor(
    public readonly status: number,
    message: string,
  ) {
    super(message);
    this.name = "ApiError";
  }
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`/api${path}`, {
    ...init,
    credentials: "include",
    headers: { "Content-Type": "application/json", ...init?.headers },
  });
  if (!res.ok) {
    const error = await res.json().catch(() => ({ message: res.statusText }));
    throw new ApiError(res.status, (error as { message: string }).message);
  }
  return res.json() as Promise<T>;
}

export const api = {
  auth: {
    me: () => request<User>("/v1/auth/me"),
  },
  sessions: {
    list: () => request<{ data: Session[]; has_more: boolean }>("/v1/sessions"),
    create: (body: CreateSessionBody) =>
      request<Session>("/v1/sessions", {
        method: "POST",
        body: JSON.stringify(body),
      }),
    get: (id: string) => request<Session>(`/v1/sessions/${id}`),
    messages: (id: string, cursor?: string) =>
      request<PaginatedResponse<Message>>(
        `/v1/sessions/${id}/messages${cursor ? `?cursor=${cursor}` : ""}`,
      ),
    delete: (id: string) =>
      request<void>(`/v1/sessions/${id}`, { method: "DELETE" }),
  },
  corpora: {
    list: () => request<Corpus[]>("/v1/corpora"),
    ingest: (formData: FormData) =>
      request<IngestResponse>("/v1/ingest", {
        method: "POST",
        body: formData,
        headers: {},
      }),
    delete: (id: string) =>
      request<void>(`/v1/corpora/${id}`, { method: "DELETE" }),
  },
};
