// Polls oscillator data (NetBrute + Intenciones) for the active ticker.

import { useQuery } from "@tanstack/react-query";
import { oscillatorsApi } from "@/lib/api";

export function useOscillators(ticker: string | null) {
  return useQuery({
    queryKey: ["oscillators", ticker],
    queryFn: () => oscillatorsApi.get(ticker!),
    enabled: ticker !== null,
    staleTime: 30_000,
    refetchInterval: 60_000,
    retry: 1,
  });
}
