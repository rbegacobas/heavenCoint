// Heaven Coint API client.
// All endpoints require a Bearer JWT except /auth/login and /auth/register.
// Token is read from localStorage (key: "hc_access_token").

import {
  ApiError,
  AssetLoadResponse,
  AssetSearchResponse,
  KpiSnapshot,
  LoginRequest,
  LoginResponse,
  MacroIndicatorsResponse,
} from "@/types/api";

const BASE = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000/api/v1";

// ── Token helpers ─────────────────────────────────────────────────────────────

export function getToken(): string | null {
  if (typeof window === "undefined") return null;
  return localStorage.getItem("hc_access_token");
}

export function setToken(token: string): void {
  localStorage.setItem("hc_access_token", token);
  // Also write a cookie so Next.js middleware (Edge runtime) can check auth state.
  // SameSite=Lax prevents CSRF for normal navigation; not httpOnly so JS can clear it.
  document.cookie = `hc_auth=1; path=/; max-age=${60 * 60 * 24 * 7}; SameSite=Lax`;
}

export function clearToken(): void {
  localStorage.removeItem("hc_access_token");
  localStorage.removeItem("hc_refresh_token");
  // Clear auth cookie
  document.cookie = "hc_auth=; path=/; max-age=0";
}

// ── Core fetch ────────────────────────────────────────────────────────────────

async function request<T>(
  path: string,
  opts: RequestInit & { auth?: boolean } = {},
): Promise<T> {
  const { auth = true, ...fetchOpts } = opts;

  const headers: Record<string, string> = {
    "Content-Type": "application/json",
    ...(fetchOpts.headers as Record<string, string>),
  };

  if (auth) {
    const token = getToken();
    if (token) headers["Authorization"] = `Bearer ${token}`;
  }

  const res = await fetch(`${BASE}${path}`, { ...fetchOpts, headers });

  if (!res.ok) {
    const body = await res.json().catch(() => ({ detail: `HTTP ${res.status}` }));
    throw new ApiError(res.status, body.detail ?? `HTTP ${res.status}`);
  }

  // 204 No Content
  if (res.status === 204) return undefined as T;

  return res.json() as Promise<T>;
}

// ── Auth ──────────────────────────────────────────────────────────────────────

export const authApi = {
  login(body: LoginRequest): Promise<LoginResponse> {
    return request<LoginResponse>("/auth/login", {
      method: "POST",
      body: JSON.stringify(body),
      auth: false,
    });
  },

  register(body: { email: string; password: string; full_name: string }): Promise<unknown> {
    return request("/auth/register", {
      method: "POST",
      body: JSON.stringify(body),
      auth: false,
    });
  },
};

// ── Assets ────────────────────────────────────────────────────────────────────

export const assetsApi = {
  search(q: string, assetType?: string): Promise<AssetSearchResponse> {
    const params = new URLSearchParams({ q });
    if (assetType) params.set("asset_type", assetType);
    return request<AssetSearchResponse>(`/assets/search?${params}`);
  },

  load(ticker: string): Promise<AssetLoadResponse> {
    return request<AssetLoadResponse>(`/assets/${ticker.toUpperCase()}/load`, {
      method: "POST",
    });
  },
};

// ── KPIs ──────────────────────────────────────────────────────────────────────

export const kpisApi = {
  get(ticker: string): Promise<KpiSnapshot> {
    return request<KpiSnapshot>(`/kpis/${ticker.toUpperCase()}`);
  },

  refresh(ticker: string): Promise<KpiSnapshot> {
    return request<KpiSnapshot>(`/kpis/${ticker.toUpperCase()}/refresh`, {
      method: "POST",
    });
  },
};

// ── Strategies ───────────────────────────────────────────────────────────────

export const strategiesApi = {
  calculate(body: import("@/types/api").StrategyRequest): Promise<import("@/types/api").StrategyResult> {
    return request("/strategies/calculate", {
      method: "POST",
      body: JSON.stringify(body),
    });
  },

  getLast(ticker: string): Promise<import("@/types/api").StrategyResult> {
    return request(`/strategies/${ticker.toUpperCase()}/last`);
  },
};

// ── Macro ─────────────────────────────────────────────────────────────────────

export const macroApi = {
  get(): Promise<MacroIndicatorsResponse> {
    return request<MacroIndicatorsResponse>("/macro/indicators");
  },
};
