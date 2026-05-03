"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { api } from "@/lib/api";
import type { Corpus, IngestResponse } from "@/types";

export function useCorpora() {
  return useQuery({
    queryKey: ["corpora"],
    queryFn: () => api.corpora.list(),
  });
}

export function useIngestCorpus() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (formData: FormData) => api.corpora.ingest(formData),
    onSuccess: (_data: IngestResponse) => {
      queryClient.invalidateQueries({ queryKey: ["corpora"] });
    },
  });
}

export function useDeleteCorpus() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => api.corpora.delete(id),
    onSuccess: (_data: void, deletedId: string) => {
      queryClient.setQueryData<Corpus[]>(["corpora"], (old) =>
        (old ?? []).filter((c) => c.id !== deletedId),
      );
    },
  });
}
