"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { api } from "@/lib/api";
import type { CreateSessionBody, Session } from "@/types";

export function useSessions() {
  return useQuery({
    queryKey: ["sessions"],
    queryFn: () => api.sessions.list(),
    select: (data) => data.data,
  });
}

export function useCreateSession() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (body: CreateSessionBody) => api.sessions.create(body),
    onSuccess: (newSession: Session) => {
      queryClient.setQueryData<{ data: Session[]; has_more: boolean }>(
        ["sessions"],
        (old) => ({
          data: [newSession, ...(old?.data ?? [])],
          has_more: old?.has_more ?? false,
        }),
      );
    },
  });
}

export function useDeleteSession() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => api.sessions.delete(id),
    onSuccess: (_data, deletedId) => {
      queryClient.setQueryData<{ data: Session[]; has_more: boolean }>(
        ["sessions"],
        (old) => ({
          data: (old?.data ?? []).filter((s) => s.id !== deletedId),
          has_more: old?.has_more ?? false,
        }),
      );
    },
  });
}
