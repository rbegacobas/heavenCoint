// TypeScript types mirroring backend Pydantic schemas.
// Keep in sync with backend response shapes in app/api/v1/.

export type AssetType = "stock" | "crypto" | "etf" | "forex";
export type TrendDirection = "UP" | "DOWN" | "SIDEWAYS";
export type VolatilityState = "expansion" | "contraction" | "stable";
export type MomentumClass = "POSITIVE" | "NEGATIVE" | "NEUTRAL";

// ── Asset ─────────────────────────────────────────────────────────────────────

export interface AssetSearchResult {
  ticker: string;
  name: string;
  asset_type: AssetType;
  exchange: string | null;
  currency: string | null;
}

export interface AssetSearchResponse {
  results: AssetSearchResult[];
  count: number;
}

export interface AssetLoadResponse {
  ticker: string;
  asset_id: string;
  status: string;
  message: string;
}

// ── KPI Snapshot ──────────────────────────────────────────────────────────────

export interface KpiPrice {
  current: number;
  range_low_95: number | null;
  range_high_95: number | null;
}

export interface KpiAtr {
  value: number;
  period: number;
}

export interface KpiVolatility {
  implied: number | null;
  change_pct: number | null;
  state: VolatilityState;
}

export interface KpiMomentum {
  value: number | null;
  class: MomentumClass;
}

export interface KpiTrends {
  d200: TrendDirection | null;
  d134: TrendDirection | null;
  d50: TrendDirection | null;
  divergence: boolean;
}

export interface KpiSnapshot {
  ticker: string;
  source: "cache" | "calculated";
  is_stale: boolean;
  price: KpiPrice;
  atr: KpiAtr;
  volatility: KpiVolatility;
  momentum: KpiMomentum;
  trends: KpiTrends;
  last_updated: string | null;
}

// ── Macro Indicators ──────────────────────────────────────────────────────────

export interface MacroIndicator {
  series_id: string;
  name: string;
  value: number | null;
  unit: string | null;
  observation_date: string | null;
  fetched_at: string | null;
}

export interface MacroIndicatorsResponse {
  indicators: MacroIndicator[];
  recession_probability: number | null;
  economic_cycle_phase: string | null;
}

// ── Strategy ─────────────────────────────────────────────────────────────────

export interface StrategyRequest {
  ticker: string;
  direction: "LONG" | "SHORT";
  capital: number;
  risk_pct: number;
}

export interface StrategyResult {
  ticker: string;
  direction: "LONG" | "SHORT";
  entry_price: number;
  stop_loss: number;
  tp1: number;
  tp2: number;
  tp3_trailing_atr_mult: number;
  n_shares: number;
  risk_amount: number;
  rr_ratio: number;
  is_recommended: boolean;
  atr_used: number;
  sl_atr_mult: number;
  tp1_pct: number;
  tp2_pct: number;
  tp3_pct: number;
  warning: string | null;
  calculated_at: string;
}

// ── Auth ─────────────────────────────────────────────────────────────────────

export interface LoginRequest {
  email: string;
  password: string;
}

export interface LoginResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
}

// ── API Error ─────────────────────────────────────────────────────────────────

export class ApiError extends Error {
  constructor(
    public readonly status: number,
    message: string,
  ) {
    super(message);
    this.name = "ApiError";
  }
}
