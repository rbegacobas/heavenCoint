import { render, screen } from "@testing-library/react";
import { describe, it, expect, vi, beforeEach } from "vitest";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import DashboardPage from "@/app/dashboard/page";
import type { KpiSnapshot } from "@/types/api";

// ── Fixture ───────────────────────────────────────────────────────────────────

const mockSnapshot: KpiSnapshot = {
  ticker: "AAPL",
  source: "calculated",
  is_stale: false,
  price: { current: 195.5, range_low_95: 188.0, range_high_95: 203.0 },
  atr: { value: 3.42, period: 14 },
  volatility: { implied: 28.5, change_pct: 2.1, state: "expansion" },
  momentum: { value: 12.4, class: "POSITIVE" },
  trends: { d200: "UP", d134: "UP", d50: "UP", divergence: false },
  last_updated: "2026-04-03T12:00:00Z",
};

// ── Mocks ────────────────────────────────────────────────────────────────────

vi.mock("@/stores/asset-store", () => ({
  useAssetStore: vi.fn(),
}));

vi.mock("@/hooks/use-kpi-snapshot", () => ({
  useKpiSnapshot: vi.fn(),
}));

// ── Helpers ───────────────────────────────────────────────────────────────────

function makeQueryClient() {
  return new QueryClient({ defaultOptions: { queries: { retry: false } } });
}

function renderWithProviders(ui: React.ReactElement) {
  const queryClient = makeQueryClient();
  return render(
    <QueryClientProvider client={queryClient}>{ui}</QueryClientProvider>,
  );
}

// ── Tests ─────────────────────────────────────────────────────────────────────

describe("DashboardPage", () => {
  beforeEach(() => {
    vi.resetAllMocks();
  });

  it("renders the empty state when no asset is selected", async () => {
    const { useAssetStore } = await import("@/stores/asset-store");
    const { useKpiSnapshot } = await import("@/hooks/use-kpi-snapshot");

    vi.mocked(useAssetStore).mockReturnValue({
      activeTicker: null,
      kpiSnapshot: null,
      isLoading: false,
      error: null,
      lastRefreshed: null,
      setActiveTicker: vi.fn(),
      setKpiSnapshot: vi.fn(),
      setLoading: vi.fn(),
      setError: vi.fn(),
      reset: vi.fn(),
    });

    vi.mocked(useKpiSnapshot).mockReturnValue({
      data: undefined,
      isFetching: false,
    } as ReturnType<typeof useKpiSnapshot>);

    renderWithProviders(<DashboardPage />);

    expect(
      screen.getByText(/busca un activo para comenzar/i),
    ).toBeInTheDocument();
  });

  it("renders skeleton while loading", async () => {
    const { useAssetStore } = await import("@/stores/asset-store");
    const { useKpiSnapshot } = await import("@/hooks/use-kpi-snapshot");

    vi.mocked(useAssetStore).mockReturnValue({
      activeTicker: "AAPL",
      kpiSnapshot: null,
      isLoading: true,
      error: null,
      lastRefreshed: null,
      setActiveTicker: vi.fn(),
      setKpiSnapshot: vi.fn(),
      setLoading: vi.fn(),
      setError: vi.fn(),
      reset: vi.fn(),
    });

    vi.mocked(useKpiSnapshot).mockReturnValue({
      data: undefined,
      isFetching: true,
    } as ReturnType<typeof useKpiSnapshot>);

    const { container } = renderWithProviders(<DashboardPage />);

    // Skeleton renders animate-pulse divs
    expect(container.querySelector(".animate-pulse")).toBeInTheDocument();
  });

  it("renders KPI cards with real data after loading", async () => {
    const { useAssetStore } = await import("@/stores/asset-store");
    const { useKpiSnapshot } = await import("@/hooks/use-kpi-snapshot");

    vi.mocked(useAssetStore).mockReturnValue({
      activeTicker: "AAPL",
      kpiSnapshot: mockSnapshot,
      isLoading: false,
      error: null,
      lastRefreshed: "2026-04-03T12:00:00Z",
      setActiveTicker: vi.fn(),
      setKpiSnapshot: vi.fn(),
      setLoading: vi.fn(),
      setError: vi.fn(),
      reset: vi.fn(),
    });

    vi.mocked(useKpiSnapshot).mockReturnValue({
      data: mockSnapshot,
      isFetching: false,
    } as ReturnType<typeof useKpiSnapshot>);

    renderWithProviders(<DashboardPage />);

    // Ticker shown
    expect(screen.getByText("AAPL")).toBeInTheDocument();
    // ATR section
    expect(screen.getByText("ATR Actual")).toBeInTheDocument();
    // Price visible (formatted — appears in multiple cards, use getAllBy)
    expect(screen.getAllByText("$195.50").length).toBeGreaterThan(0);
  });

  it("renders error message when store has an error", async () => {
    const { useAssetStore } = await import("@/stores/asset-store");
    const { useKpiSnapshot } = await import("@/hooks/use-kpi-snapshot");

    vi.mocked(useAssetStore).mockReturnValue({
      activeTicker: "AAPL",
      kpiSnapshot: null,
      isLoading: false,
      error: "Error al cargar el activo",
      lastRefreshed: null,
      setActiveTicker: vi.fn(),
      setKpiSnapshot: vi.fn(),
      setLoading: vi.fn(),
      setError: vi.fn(),
      reset: vi.fn(),
    });

    vi.mocked(useKpiSnapshot).mockReturnValue({
      data: undefined,
      isFetching: false,
    } as ReturnType<typeof useKpiSnapshot>);

    renderWithProviders(<DashboardPage />);

    expect(screen.getByText("Error al cargar el activo")).toBeInTheDocument();
  });
});
