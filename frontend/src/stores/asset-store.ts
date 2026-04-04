// Global state for the active asset and its KPI snapshot.
// Only ONE asset active at a time (business rule RN-7).

import { create } from "zustand";
import { KpiSnapshot } from "@/types/api";

interface AssetState {
  // The ticker currently loaded in the dashboard (e.g. "AAPL")
  activeTicker: string | null;
  // Latest KPI snapshot fetched from the API
  kpiSnapshot: KpiSnapshot | null;
  // True while the asset is being loaded (POST /assets/{ticker}/load)
  isLoading: boolean;
  // Non-null when the last load or fetch failed
  error: string | null;
  // ISO timestamp of when the snapshot was last refreshed
  lastRefreshed: string | null;

  // Actions
  setActiveTicker: (ticker: string) => void;
  setKpiSnapshot: (snapshot: KpiSnapshot) => void;
  setLoading: (loading: boolean) => void;
  setError: (error: string | null) => void;
  reset: () => void;
}

const initialState = {
  activeTicker: null,
  kpiSnapshot: null,
  isLoading: false,
  error: null,
  lastRefreshed: null,
};

export const useAssetStore = create<AssetState>((set) => ({
  ...initialState,

  setActiveTicker(ticker) {
    // Changing ticker resets snapshot — one asset at a time
    set({ activeTicker: ticker.toUpperCase(), kpiSnapshot: null, error: null });
  },

  setKpiSnapshot(snapshot) {
    set({ kpiSnapshot: snapshot, lastRefreshed: new Date().toISOString() });
  },

  setLoading(loading) {
    set({ isLoading: loading });
  },

  setError(error) {
    set({ error, isLoading: false });
  },

  reset() {
    set(initialState);
  },
}));
