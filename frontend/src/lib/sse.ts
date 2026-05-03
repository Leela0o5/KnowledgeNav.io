import type { QueryParams, QueryResponse } from "@/types";

function buildQueryUrl(params: QueryParams): string {
  const searchParams = new URLSearchParams({
    question: params.question,
    session_id: params.session_id,
  });
  return `/api/v1/query?${searchParams.toString()}`;
}

export function streamQuery(
  params: QueryParams,
  onToken: (token: string) => void,
  onDone: (response: QueryResponse) => void,
  onError: (error: Event) => void,
): () => void {
  const source = new EventSource(buildQueryUrl(params), { withCredentials: true });

  source.addEventListener("token", (e: MessageEvent) => {
    onToken(e.data as string);
  });

  source.addEventListener("done", (e: MessageEvent) => {
    onDone(JSON.parse(e.data as string) as QueryResponse);
    source.close();
  });

  source.addEventListener("error", (e: Event) => {
    onError(e);
    source.close();
  });

  return () => source.close();
}
