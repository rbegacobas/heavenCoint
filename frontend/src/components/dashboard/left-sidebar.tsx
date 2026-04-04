"use client";

import { useState, useRef, useEffect } from "react";
import { RefreshCw, CircleCheck, CircleX, Loader2, Search } from "lucide-react";
import { useAssetSearch } from "@/hooks/use-asset-search";
import { useAssetStore } from "@/stores/asset-store";
import { assetsApi, kpisApi } from "@/lib/api";
import { ApiError } from "@/types/api";

type AnalysisHistoryItem = {
  date: string;
  ticker: string;
  check1: boolean;
  check2: boolean;
};

// Static history — will be dynamic in M9 (User Management)
const recentAnalyses: AnalysisHistoryItem[] = [
  { date: "25/03", ticker: "NFLX", check1: true, check2: true },
  { date: "24/03", ticker: "MSFT", check1: true, check2: false },
  { date: "23/03", ticker: "PM", check1: true, check2: true },
  { date: "22/03", ticker: "PLTR", check1: false, check2: true },
  { date: "21/03", ticker: "V", check1: true, check2: true },
  { date: "20/03", ticker: "UBER", check1: true, check2: false },
];

export default function LeftSidebar() {
  const [inputValue, setInputValue] = useState("");
  const [dropdownOpen, setDropdownOpen] = useState(false);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);
  const dropdownRef = useRef<HTMLDivElement>(null);

  const { activeTicker, setActiveTicker, setKpiSnapshot, setLoading, setError } =
    useAssetStore();

  const { data: searchData, isFetching: isSearching } = useAssetSearch(inputValue);
  const results = searchData?.results ?? [];

  // Close dropdown on outside click
  useEffect(() => {
    function handleClick(e: MouseEvent) {
      if (
        dropdownRef.current &&
        !dropdownRef.current.contains(e.target as Node) &&
        inputRef.current &&
        !inputRef.current.contains(e.target as Node)
      ) {
        setDropdownOpen(false);
      }
    }
    document.addEventListener("mousedown", handleClick);
    return () => document.removeEventListener("mousedown", handleClick);
  }, []);

  function handleSelectTicker(ticker: string) {
    setInputValue(ticker);
    setActiveTicker(ticker);
    setDropdownOpen(false);
  }

  async function handleAnalyze() {
    const ticker = inputValue.trim().toUpperCase();
    if (!ticker) return;

    setIsAnalyzing(true);
    setLoading(true);
    setError(null);

    try {
      // Step 1: Load asset (ingests price data)
      await assetsApi.load(ticker);
      // Step 2: Fetch KPIs
      const snapshot = await kpisApi.get(ticker);
      setActiveTicker(ticker);
      setKpiSnapshot(snapshot);
    } catch (err) {
      const message =
        err instanceof ApiError ? err.message : "Error al cargar el activo";
      setError(message);
    } finally {
      setIsAnalyzing(false);
      setLoading(false);
    }
  }

  function handleKeyDown(e: React.KeyboardEvent<HTMLInputElement>) {
    if (e.key === "Enter") {
      setDropdownOpen(false);
      handleAnalyze();
    } else if (e.key === "Escape") {
      setDropdownOpen(false);
    }
  }

  return (
    <aside className="flex w-[220px] shrink-0 flex-col gap-4 bg-hc-bg-sidebar px-4 py-5">
      <h2 className="text-center text-[13px] font-bold text-hc-text-white">ANÁLISIS</h2>

      {/* Search input */}
      <div className="relative">
        <div className="flex h-9 items-center gap-2 rounded-md bg-hc-bg-input px-2.5">
          <Search className="h-3.5 w-3.5 shrink-0 text-hc-text-muted" />
          <input
            ref={inputRef}
            type="text"
            value={inputValue}
            onChange={(e) => {
              setInputValue(e.target.value);
              setDropdownOpen(e.target.value.length > 0);
            }}
            onFocus={() => inputValue.length > 0 && setDropdownOpen(true)}
            onKeyDown={handleKeyDown}
            placeholder="Ingresa el mercado"
            className="w-full bg-transparent text-xs text-hc-text-white placeholder-hc-text-muted outline-none"
          />
          {isSearching && (
            <Loader2 className="h-3 w-3 shrink-0 animate-spin text-hc-text-muted" />
          )}
        </div>

        {/* Search dropdown */}
        {dropdownOpen && results.length > 0 && (
          <div
            ref={dropdownRef}
            className="absolute left-0 right-0 top-10 z-50 overflow-hidden rounded-md border border-hc-border-dark bg-hc-bg-sidebar shadow-lg"
          >
            {results.slice(0, 5).map((r) => (
              <button
                key={r.ticker}
                onMouseDown={() => handleSelectTicker(r.ticker)}
                className="flex w-full items-center gap-2 px-3 py-2 text-left hover:bg-hc-bg-input"
              >
                <span className="text-[11px] font-semibold text-hc-text-white">
                  {r.ticker}
                </span>
                <span className="truncate text-[10px] text-hc-text-muted">{r.name}</span>
              </button>
            ))}
          </div>
        )}
      </div>

      {/* Value Investing checkbox */}
      <div className="flex items-center gap-2">
        <div className="h-4 w-4 rounded-[3px] border border-hc-text-muted" />
        <span className="text-[11px] text-hc-text-white">Habilitar Value Investing</span>
        <RefreshCw className="h-3.5 w-3.5 text-hc-accent-green" />
      </div>

      {/* Analyze button */}
      <button
        onClick={handleAnalyze}
        disabled={isAnalyzing || !inputValue.trim()}
        className="flex h-[38px] items-center justify-center gap-2 rounded-lg bg-hc-btn-green text-xs font-semibold text-hc-text-white disabled:cursor-not-allowed disabled:opacity-60"
      >
        {isAnalyzing ? (
          <>
            <Loader2 className="h-3.5 w-3.5 animate-spin" />
            Analizando...
          </>
        ) : (
          "Analizar con HeavenCoint"
        )}
      </button>

      <p className="text-center text-[10px] text-hc-text-muted">
        {activeTicker ? (
          <span className="text-hc-accent-green">✓ {activeTicker} cargado</span>
        ) : (
          "Te quedan 80 llamadas"
        )}
      </p>

      {/* Divider */}
      <div className="h-px bg-hc-border-dark" />

      <p className="text-[11px] font-semibold text-hc-text-muted">ÚLTIMOS ANÁLISIS</p>

      {/* History list */}
      <div className="flex flex-col gap-1">
        {recentAnalyses.map((a) => (
          <div key={a.date + a.ticker} className="flex items-center gap-2 py-1.5">
            <span className="text-[9px] text-hc-text-muted">{a.date}</span>
            <span className="text-[11px] font-semibold text-hc-text-white">{a.ticker}</span>
            {a.check1 ? (
              <CircleCheck className="h-3.5 w-3.5 text-hc-accent-green" />
            ) : (
              <CircleX className="h-3.5 w-3.5 text-hc-accent-red" />
            )}
            {a.check2 ? (
              <CircleCheck className="h-3.5 w-3.5 text-hc-accent-green" />
            ) : (
              <CircleX className="h-3.5 w-3.5 text-hc-accent-red" />
            )}
          </div>
        ))}
      </div>

      {/* View all */}
      <button className="flex h-8 items-center justify-center rounded-md bg-hc-accent-blue text-[11px] font-medium text-hc-text-white">
        Ver todos
      </button>
    </aside>
  );
}
