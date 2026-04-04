import { QueryClient } from "@tanstack/react-query";

export const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      // Data is fresh for 30s, then refetched in background
      staleTime: 30_000,
      // Retry once on failure (API may be momentarily unavailable)
      retry: 1,
      // Don't refetch when window regains focus — markets don't need it
      refetchOnWindowFocus: false,
    },
  },
});
