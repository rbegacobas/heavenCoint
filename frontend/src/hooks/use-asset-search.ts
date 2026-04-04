// Debounced asset search — fires 300ms after user stops typing.

import { useQuery } from "@tanstack/react-query";
import { useDeferredValue } from "react";
import { assetsApi } from "@/lib/api";

export function useAssetSearch(rawQuery: string) {
  // React 19 built-in debounce — avoids external dependencies
  const query = useDeferredValue(rawQuery.trim());

  return useQuery({
    queryKey: ["asset-search", query],
    queryFn: () => assetsApi.search(query),
    enabled: query.length >= 1,
    staleTime: 60_000,
    placeholderData: (prev) => prev,
  });
}
