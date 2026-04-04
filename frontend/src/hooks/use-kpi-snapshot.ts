// Polls the KPI snapshot for the active ticker every 60s.
// Syncs result into the Zustand store for non-query consumers.

import { useQuery } from "@tanstack/react-query";
import { useEffect } from "react";
import { kpisApi } from "@/lib/api";
import { useAssetStore } from "@/stores/asset-store";

export function useKpiSnapshot(ticker: string | null) {
  const setKpiSnapshot = useAssetStore((s) => s.setKpiSnapshot);
  const setError = useAssetStore((s) => s.setError);

  const query = useQuery({
    queryKey: ["kpi", ticker],
    queryFn: () => kpisApi.get(ticker!),
    enabled: ticker !== null,
    staleTime: 30_000,
    refetchInterval: 60_000,
  });

  // Keep Zustand store in sync
  useEffect(() => {
    if (query.data) setKpiSnapshot(query.data);
  }, [query.data, setKpiSnapshot]);

  useEffect(() => {
    if (query.error) setError((query.error as Error).message);
  }, [query.error, setError]);

  return query;
}
