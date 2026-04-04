"use client";

import {
  Activity,
  ImageIcon,
  Download,
  Settings,
  BarChart3,
  LayoutGrid,
  Eye,
  ChevronDown,
  Pencil,
  CircleCheck,
  TriangleAlert,
  TrendingUp,
  TrendingDown,
  ArrowDown,
  CircleAlert,
  Search,
} from "lucide-react";
import { useAssetStore } from "@/stores/asset-store";
import { useKpiSnapshot } from "@/hooks/use-kpi-snapshot";
import {
  KpiSnapshot,
  TrendDirection,
  VolatilityState,
  MomentumClass,
} from "@/types/api";

// ── Skeleton ──────────────────────────────────────────────────────────────────

function Skeleton({ className }: { className?: string }) {
  return (
    <div className={`animate-pulse rounded bg-hc-border-dark ${className ?? ""}`} />
  );
}

// ── Empty State ───────────────────────────────────────────────────────────────

function EmptyState() {
  return (
    <div className="flex flex-1 flex-col items-center justify-center gap-4 p-10 text-center">
      <Search className="h-12 w-12 text-hc-text-muted opacity-40" />
      <p className="text-sm font-semibold text-hc-text-muted">
        Busca un activo para comenzar
      </p>
      <p className="max-w-xs text-xs leading-5 text-hc-text-muted opacity-70">
        Ingresa un ticker en la barra lateral izquierda y pulsa{" "}
        <span className="text-hc-accent-green">Analizar con HeavenCoint</span>.
      </p>
    </div>
  );
}

// ── Asset Header ──────────────────────────────────────────────────────────────

function AssetHeader({ snapshot }: { snapshot: KpiSnapshot }) {
  const date = snapshot.last_updated
    ? new Date(snapshot.last_updated).toLocaleDateString("es-ES", {
        day: "2-digit",
        month: "2-digit",
        year: "2-digit",
      })
    : "—";

  return (
    <div className="flex items-center justify-between">
      <div className="flex items-center gap-3">
        <span className="text-[22px] font-bold text-hc-text-dark">
          {snapshot.ticker}
        </span>
        <span className="text-xs text-hc-text-muted">{date}</span>
        <button className="flex items-center gap-1.5 rounded-md bg-hc-accent-green px-3 py-1.5">
          <ImageIcon className="h-3.5 w-3.5 text-white" />
          <span className="text-[11px] font-semibold text-white">Ver imagen</span>
        </button>
        <button className="flex items-center gap-1.5 rounded-md bg-hc-accent-green px-3 py-1.5">
          <Download className="h-3.5 w-3.5 text-white" />
          <span className="text-[11px] font-semibold text-white">Descargar imagen</span>
        </button>
      </div>
      <div className="flex items-center gap-2.5">
        <div className="flex items-center gap-2">
          <Settings className="h-5 w-5 text-hc-text-muted" />
          <BarChart3 className="h-5 w-5 text-hc-text-muted" />
          <LayoutGrid className="h-5 w-5 text-hc-text-muted" />
          <Eye className="h-5 w-5 text-hc-text-muted" />
        </div>
        <div className="flex items-center gap-1.5 rounded-md bg-hc-bg-input px-3 py-1.5">
          <span className="text-[11px] text-hc-text-white">Custom 1</span>
          <ChevronDown className="h-3 w-3 text-hc-text-muted" />
        </div>
        <div className="flex items-center gap-1.5 rounded-md bg-hc-bg-input px-3.5 py-1.5">
          <Pencil className="h-[13px] w-[13px] text-hc-text-white" />
          <span className="text-[11px] text-hc-text-white">Editar tablero</span>
        </div>
      </div>
    </div>
  );
}

function AssetHeaderSkeleton() {
  return (
    <div className="flex items-center gap-3">
      <Skeleton className="h-7 w-20" />
      <Skeleton className="h-4 w-16" />
      <Skeleton className="h-7 w-24" />
    </div>
  );
}

// ── Situation Analysis Card ───────────────────────────────────────────────────

function SituationAnalysis({ snapshot }: { snapshot: KpiSnapshot }) {
  const trend = snapshot.trends.d50 ?? "SIDEWAYS";
  const volState = snapshot.volatility.state;

  const trendLabel =
    trend === "UP" ? "alcista" : trend === "DOWN" ? "bajista" : "lateral";
  const volLabel =
    volState === "expansion"
      ? "expansión de volatilidad"
      : volState === "contraction"
        ? "contracción de volatilidad"
        : "volatilidad estable";

  return (
    <div className="flex flex-1 flex-col gap-2.5 rounded-[10px] bg-hc-bg-card p-4">
      <div className="flex items-center gap-2">
        <Activity className="h-4 w-4 text-hc-accent-blue" />
        <span className="text-[13px] font-semibold text-hc-text-dark">
          Análisis de situación
        </span>
      </div>
      <p className="text-xs leading-6 text-hc-text-secondary">
        El mercado muestra tendencia{" "}
        <span
          className={
            trend === "UP" ? "text-hc-accent-green" : trend === "DOWN" ? "text-hc-accent-red" : ""
          }
        >
          {trendLabel}
        </span>{" "}
        con precio actual de{" "}
        <span className="font-semibold text-hc-text-dark">
          ${snapshot.price.current.toFixed(2)}
        </span>
        .
        <br />
        Rango de confianza 95%:{" "}
        <span className="font-semibold text-hc-text-dark">
          ${(snapshot.price.range_low_95 ?? 0).toFixed(2)} —{" "}
          ${(snapshot.price.range_high_95 ?? 0).toFixed(2)}
        </span>
        .
        <br />
        Estado de volatilidad:{" "}
        <span
          className={
            volState === "expansion"
              ? "text-hc-accent-yellow"
              : volState === "contraction"
                ? "text-hc-accent-green"
                : ""
          }
        >
          {volLabel}
        </span>
        .{" "}
        {/* TODO: M3 — add oscillator signals to this summary */}
      </p>
    </div>
  );
}

// ── Price Levels Card ─────────────────────────────────────────────────────────

function PriceLevels({ snapshot }: { snapshot: KpiSnapshot }) {
  const price = snapshot.price.current;
  const atr = snapshot.atr.value;

  const r2 = price + atr * 2;
  const r1 = price + atr;
  const s1 = price - atr;

  const pct = (level: number) => (((level - price) / price) * 100).toFixed(2);

  const rows = [
    { label: "R2", price: r2.toFixed(2), dist: `+${pct(r2)}%`, color: "text-hc-accent-purple", bg: true },
    { label: "R1", price: r1.toFixed(2), dist: `+${pct(r1)}%`, color: "text-hc-accent-purple", bg: false },
    { label: "Actual", price: price.toFixed(2), dist: "0.00%", color: "text-hc-accent-blue", bg: true },
    { label: "S1", price: s1.toFixed(2), dist: `${pct(s1)}%`, color: "text-hc-accent-red", bg: false },
  ];

  const volPct = snapshot.volatility.change_pct;

  return (
    <div className="flex w-[340px] shrink-0 flex-col gap-2 rounded-[10px] bg-hc-bg-card p-4">
      <div className="flex flex-col">
        <div className="flex px-2 py-1.5">
          <span className="flex-1 text-[10px] font-semibold text-hc-text-muted">Nivel</span>
          <span className="flex-1 text-[10px] font-semibold text-hc-text-muted">Precio</span>
          <span className="flex-1 text-[10px] font-semibold text-hc-text-muted">Distancia</span>
        </div>
        {rows.map((r) => (
          <div
            key={r.label}
            className={`flex px-2 py-1.5 ${r.bg ? "rounded bg-hc-bg-card-light" : ""}`}
          >
            <span className={`flex-1 text-[11px] font-semibold ${r.color}`}>{r.label}</span>
            <span className="flex-1 text-[11px] text-hc-text-dark">{r.price}</span>
            <span className="flex-1 text-[11px] text-hc-accent-green">{r.dist}</span>
          </div>
        ))}
      </div>

      <div className="flex flex-col gap-3">
        <div className="flex justify-between">
          <span className="text-[10px] text-hc-text-muted">Vol. Implícita</span>
          <span className="text-[10px] text-hc-text-muted">Cambio 7d</span>
          <span className="text-[10px] text-hc-text-muted">Estado</span>
        </div>
        <div className="flex justify-between">
          <span className="text-[11px] font-semibold text-hc-text-dark">
            {snapshot.volatility.implied !== null
              ? `${(snapshot.volatility.implied * 100).toFixed(2)}%`
              : "—"}
          </span>
          <span
            className={`text-[11px] font-semibold ${
              (volPct ?? 0) >= 0 ? "text-hc-accent-red" : "text-hc-accent-green"
            }`}
          >
            {volPct !== null ? `${volPct >= 0 ? "+" : ""}${volPct.toFixed(2)}%` : "—"}
          </span>
          <span className="text-[11px] font-semibold text-hc-text-muted">
            {snapshot.volatility.state}
          </span>
        </div>
      </div>
    </div>
  );
}

// ── Market Status Card ────────────────────────────────────────────────────────
// TODO: M3 — replace mock state with real oscillator data

function MarketStatus({ snapshot }: { snapshot: KpiSnapshot }) {
  const trend = snapshot.trends.d50 ?? "SIDEWAYS";
  const isUp = trend === "UP";

  return (
    <div className="flex flex-1 flex-col gap-2.5 rounded-[10px] bg-hc-bg-card p-4">
      <h3 className="text-sm font-bold text-hc-text-dark">Estado del Mercado</h3>
      <div className="flex items-center gap-2">
        <span className="text-[11px] text-hc-text-muted">Tendencia 50d</span>
        <span
          className={`flex items-center gap-1 rounded-full px-2 py-0.5 ${
            isUp ? "bg-hc-badge-green-bg" : "bg-hc-badge-red-bg"
          }`}
        >
          <CircleCheck
            className={`h-2.5 w-2.5 ${isUp ? "text-hc-accent-green" : "text-hc-accent-red"}`}
          />
          <span
            className={`text-[9px] font-semibold ${
              isUp ? "text-hc-accent-green" : "text-hc-accent-red"
            }`}
          >
            {isUp ? "ALCISTA" : trend === "DOWN" ? "BAJISTA" : "LATERAL"}
          </span>
        </span>
      </div>
      {snapshot.trends.divergence && (
        <span className="text-[13px] font-bold text-hc-accent-yellow">
          DIVERGENCIA →
        </span>
      )}
      <p className="text-[11px] leading-5 text-hc-text-secondary">
        {snapshot.trends.divergence
          ? "Divergencia detectada entre tendencias. Opera con precaución."
          : `Tendencias 50d/134d/200d ${isUp ? "alineadas al alza" : "alineadas a la baja o mixtas"}.`}
      </p>
      <div className="flex justify-between">
        <span className="text-[9px] text-hc-text-muted">Extremo Bajista</span>
        <span className="text-[9px] text-hc-text-muted">Neutral</span>
        <span className="text-[9px] text-hc-text-muted">Extremo Alcista</span>
      </div>
      <div className="flex h-1.5 overflow-hidden rounded-full">
        <div className="flex-1 bg-hc-accent-red" />
        <div className="flex-1 bg-hc-accent-yellow" />
        <div className="flex-1 bg-hc-accent-green" />
      </div>
      <div className="flex items-center gap-1.5">
        <TriangleAlert className="h-3 w-3 text-hc-accent-yellow" />
        <span className="text-[10px] font-semibold text-hc-accent-yellow">Nota:</span>
      </div>
      <p className="text-[10px] leading-4 text-hc-accent-cyan">
        Osciladores NetBrute e Intenciones disponibles en M3.
        {/* TODO: M3 — replace with real oscillator state */}
      </p>
    </div>
  );
}

// ── Monthly Seasonality Card ──────────────────────────────────────────────────

function Seasonality() {
  return (
    <div className="flex flex-1 flex-col gap-2 rounded-[10px] bg-hc-bg-card p-4">
      <h3 className="text-sm font-bold text-hc-text-dark">Estacionalidad Mensual</h3>
      <div className="flex items-center justify-between">
        <span className="text-[11px] text-hc-text-muted">Confianza Mes Actual</span>
        <span className="text-lg font-bold text-hc-text-dark">51%</span>
      </div>
      <div className="relative flex h-20 items-end justify-center">
        <svg viewBox="0 0 120 65" className="h-full w-[140px]">
          <defs>
            <linearGradient id="gaugeGrad" x1="0%" y1="0%" x2="100%" y2="0%">
              <stop offset="0%" stopColor="#EF4444" />
              <stop offset="50%" stopColor="#F59E0B" />
              <stop offset="100%" stopColor="#22C55E" />
            </linearGradient>
          </defs>
          <path
            d="M 10 60 A 50 50 0 0 1 110 60"
            fill="none"
            stroke="url(#gaugeGrad)"
            strokeWidth="10"
            strokeLinecap="round"
          />
          <line
            x1="60" y1="58" x2="58" y2="18"
            stroke="#1A1D3A" strokeWidth="2"
            transform="rotate(2, 60, 58)"
          />
        </svg>
      </div>
      <div className="flex justify-between">
        <span className="text-[9px] text-hc-text-muted">0%</span>
        <span className="text-[9px] text-hc-text-muted">100%</span>
      </div>
      <div className="flex items-center justify-between">
        <span className="text-[11px] text-hc-text-muted">Retorno Mes Actual</span>
        <TrendingDown className="h-3.5 w-3.5 text-hc-accent-red" />
        <span className="text-sm font-bold text-hc-accent-red">-4.02%</span>
      </div>
      <div className="flex gap-3">
        <div className="flex flex-1 flex-col gap-1 rounded-lg bg-hc-badge-green-bg p-2.5">
          <span className="text-[9px] text-hc-text-muted">Mejor Mes</span>
          <span className="text-sm font-bold text-hc-accent-green">+10.97%</span>
          <span className="text-[9px] text-hc-text-muted">Mes 5 &nbsp; Mayo</span>
        </div>
        <div className="flex flex-1 flex-col gap-1 rounded-lg bg-hc-badge-red-bg p-2.5">
          <span className="text-[9px] text-hc-text-muted">Peor Mes</span>
          <span className="text-sm font-bold text-hc-accent-red">-4.02%</span>
          <span className="text-[9px] text-hc-text-muted">Mes 2 &nbsp; Febrero</span>
        </div>
      </div>
    </div>
  );
}

// ── ATR Card ──────────────────────────────────────────────────────────────────

function AtrCard({ snapshot }: { snapshot: KpiSnapshot }) {
  const { value, period } = snapshot.atr;
  const pricePct = snapshot.price.current > 0
    ? ((value / snapshot.price.current) * 100).toFixed(2)
    : "—";

  const volState: VolatilityState = snapshot.volatility.state;
  const badge =
    volState === "expansion"
      ? { label: "ALTA VOLATILIDAD", cls: "bg-hc-badge-red-bg text-hc-accent-red" }
      : volState === "contraction"
        ? { label: "BAJA VOLATILIDAD", cls: "bg-hc-badge-blue-bg text-hc-accent-blue" }
        : { label: "VOL. NORMAL", cls: "bg-hc-badge-blue-bg text-hc-accent-blue" };

  return (
    <div className="flex flex-1 flex-col gap-2 overflow-hidden rounded-[10px] bg-hc-bg-card p-4">
      <h3 className="text-sm font-bold text-hc-text-dark">ATR Actual</h3>
      <span className="text-[32px] font-bold leading-tight text-hc-text-dark">
        {value.toFixed(2)}
      </span>
      <span
        className={`self-start rounded-full px-2.5 py-0.5 text-[9px] font-semibold ${badge.cls}`}
      >
        {badge.label}
      </span>
      <div className="flex items-center gap-2">
        <span className="text-[10px] text-hc-text-muted">% del precio:</span>
        <span className="text-[11px] font-semibold text-hc-text-dark">{pricePct}%</span>
      </div>
      <div className="flex items-center gap-2">
        <span className="text-[10px] text-hc-text-muted">Período:</span>
        <span className="text-[11px] font-semibold text-hc-text-dark">{period}d</span>
      </div>
    </div>
  );
}

// ── Momentum Card ─────────────────────────────────────────────────────────────

function MomentumCard({ snapshot }: { snapshot: KpiSnapshot }) {
  const { value, class: cls } = snapshot.momentum;
  const momentumClass: MomentumClass = cls;

  const signalBadge =
    momentumClass === "POSITIVE"
      ? { label: "Positivo", cls: "bg-hc-badge-green-bg text-hc-accent-green" }
      : momentumClass === "NEGATIVE"
        ? { label: "Negativo", cls: "bg-hc-badge-red-bg text-hc-accent-red" }
        : { label: "Neutral", cls: "bg-hc-badge-yellow-bg text-hc-accent-yellow" };

  const isPositive = momentumClass === "POSITIVE";

  return (
    <div className="flex flex-1 flex-col gap-2 overflow-hidden rounded-[10px] bg-hc-bg-card p-4">
      <h3 className="text-sm font-bold text-hc-text-dark">Momentum</h3>
      <span className="text-[32px] font-bold leading-tight text-hc-text-dark">
        {value !== null ? value.toFixed(2) : "—"}
      </span>
      <div className="flex items-center gap-1.5">
        {isPositive ? (
          <TrendingUp className="h-3 w-3 text-hc-accent-green" />
        ) : (
          <TrendingDown className="h-3 w-3 text-hc-accent-red" />
        )}
        <span
          className={`text-[11px] font-semibold ${
            isPositive ? "text-hc-accent-green" : "text-hc-accent-red"
          }`}
        >
          {momentumClass}
        </span>
      </div>
      <div className="flex items-center gap-2">
        <span className="text-[10px] text-hc-text-muted">Señal</span>
        <span className={`rounded-full px-2.5 py-0.5 text-[9px] font-semibold ${signalBadge.cls}`}>
          {signalBadge.label}
        </span>
      </div>
    </div>
  );
}

// ── Projection Card ───────────────────────────────────────────────────────────

function ProjectionCard({ snapshot }: { snapshot: KpiSnapshot }) {
  const current = snapshot.price.current;
  // Placeholder projection: current + 1.5×ATR (upside target level 1)
  // TODO: M3 will replace this with oscillator-based projection
  const projected = current + snapshot.atr.value * 1.5;
  const pct = (((projected - current) / current) * 100).toFixed(2);
  const isPositive = projected > current;

  return (
    <div className="flex flex-1 flex-col gap-2.5 rounded-[10px] bg-hc-bg-card p-4">
      <h3 className="text-sm font-bold text-hc-text-dark">Proyección Corto Plazo</h3>
      <div className="flex flex-col gap-1">
        <span className="text-[10px] text-hc-text-muted">Precio actual</span>
        <span className="text-xl font-bold text-hc-text-dark">${current.toFixed(2)}</span>
      </div>
      <div className="flex flex-col gap-1">
        <span className="text-[10px] text-hc-text-muted">TP1 estimado (1.5×ATR)</span>
        <span className="text-xl font-bold text-hc-text-dark">${projected.toFixed(2)}</span>
      </div>
      <div className="flex items-center gap-1.5">
        {isPositive ? (
          <TrendingUp className="h-3.5 w-3.5 text-hc-accent-green" />
        ) : (
          <TrendingDown className="h-3.5 w-3.5 text-hc-accent-red" />
        )}
        <span
          className={`text-[13px] font-bold ${
            isPositive ? "text-hc-accent-green" : "text-hc-accent-red"
          }`}
        >
          {isPositive ? "+" : ""}
          {pct}%
        </span>
      </div>
    </div>
  );
}

// ── Volatility Card ───────────────────────────────────────────────────────────

function VolatilityCard({ snapshot }: { snapshot: KpiSnapshot }) {
  const implied = snapshot.volatility.implied;
  const state = snapshot.volatility.state;

  const riskLabel =
    implied !== null && implied > 0.4
      ? "Riesgo Alto"
      : implied !== null && implied > 0.2
        ? "Riesgo Moderado"
        : "Riesgo Bajo";

  const color =
    implied !== null && implied > 0.4
      ? "text-hc-accent-red"
      : implied !== null && implied > 0.2
        ? "text-hc-accent-yellow"
        : "text-hc-accent-green";

  return (
    <div className="flex flex-1 flex-col items-center gap-2 rounded-[10px] bg-hc-bg-card p-4">
      <h3 className="text-sm font-bold text-hc-text-dark">Volatilidad</h3>
      <span className={`text-[32px] font-bold leading-tight ${color}`}>
        {implied !== null ? `${(implied * 100).toFixed(2)}%` : "—"}
      </span>
      <span className={`text-[11px] font-semibold ${color}`}>{riskLabel}</span>
      <div className="flex items-center gap-1.5">
        <span className="text-[10px] text-hc-text-muted">Estado:</span>
        <span className="text-[11px] font-semibold text-hc-text-dark capitalize">{state}</span>
      </div>
    </div>
  );
}

// ── Directional Analysis Card ─────────────────────────────────────────────────

function DirectionalCard({ snapshot }: { snapshot: KpiSnapshot }) {
  function TrendDisplay({ dir, label }: { dir: TrendDirection | null; label: string }) {
    const isUp = dir === "UP";
    const isDown = dir === "DOWN";
    return (
      <div className="flex flex-col items-center gap-1">
        <span className="text-[10px] text-hc-text-muted">{label}</span>
        {isUp ? (
          <TrendingUp className="h-9 w-9 text-hc-accent-green" />
        ) : isDown ? (
          <TrendingDown className="h-9 w-9 text-hc-accent-red" />
        ) : (
          <ArrowDown className="h-9 w-9 text-hc-accent-yellow" />
        )}
        <span
          className={`text-xs font-semibold ${
            isUp
              ? "text-hc-accent-green"
              : isDown
                ? "text-hc-accent-red"
                : "text-hc-accent-yellow"
          }`}
        >
          {dir ?? "LATERAL"}
        </span>
      </div>
    );
  }

  return (
    <div className="flex flex-1 flex-col gap-2.5 rounded-[10px] bg-hc-bg-card p-4">
      <h3 className="text-sm font-bold text-hc-text-dark">Análisis Direccional</h3>
      <div className="flex justify-around">
        <TrendDisplay dir={snapshot.trends.d50} label="Corto plazo" />
        <TrendDisplay dir={snapshot.trends.d134} label="Medio plazo" />
      </div>
      {snapshot.trends.divergence && (
        <p className="text-center text-[10px] font-semibold text-hc-accent-yellow">
          ⚠ Divergencia entre tendencias
        </p>
      )}
    </div>
  );
}

// ── NetBrut Card ──────────────────────────────────────────────────────────────
// TODO: M3 — replace static zones with real CMF (NetBrute) oscillator data

function NetBrutCard() {
  const zones = [
    { label: "Sobreventa", active: true },
    { label: "Bajista", active: false },
    { label: "Neutral", active: false },
    { label: "Alcista", active: false },
    { label: "Sobrecompra", active: false },
  ];

  return (
    <div className="flex flex-1 flex-col gap-1.5 rounded-[10px] bg-hc-bg-card p-4">
      <h3 className="text-sm font-bold text-hc-text-dark">Estado NetBrut</h3>
      <span className="text-[10px] text-hc-text-muted">Estado actual</span>
      <p className="text-[13px] font-bold leading-[1.3] text-hc-accent-yellow">
        PENDIENTE
        <br />
        MÓDULO M3
      </p>
      <div className="flex items-center gap-1.5">
        <CircleAlert className="h-3 w-3 text-hc-accent-yellow" />
        <span className="text-[9px] font-semibold text-hc-accent-yellow">
          DISPONIBLE EN M3
        </span>
      </div>
      <div className="flex flex-col gap-1">
        <span className="text-[10px] text-hc-text-muted">Oscillator Engine</span>
        <div className="flex items-center gap-2">
          <span className="text-xs font-bold text-hc-accent-yellow">
            CMF-14 próximamente
          </span>
        </div>
      </div>
      <div className="flex gap-0.5">
        {zones.map((z) => (
          <div key={z.label} className="flex flex-1 flex-col items-center gap-0.5">
            <span className="text-[7px] text-hc-text-muted">{z.label}</span>
            <div className={`h-4 w-full rounded-sm bg-hc-bg-card-light`} />
          </div>
        ))}
      </div>
      <div className="flex items-center gap-1.5">
        <TriangleAlert className="h-3 w-3 text-hc-accent-yellow" />
        <span className="text-[10px] font-semibold text-hc-accent-yellow">
          Oscilador NetBrute — M3
        </span>
      </div>
    </div>
  );
}

// ── Loading skeleton for a full row ──────────────────────────────────────────

function RowSkeleton({ height }: { height: string }) {
  return (
    <div className={`flex shrink-0 gap-4 ${height}`}>
      <Skeleton className="flex-1" />
      <Skeleton className="w-[340px]" />
    </div>
  );
}

// ── Main Content Export ───────────────────────────────────────────────────────

export default function MainContent() {
  const { activeTicker, kpiSnapshot, isLoading, error } = useAssetStore();

  // Wire up polling once we have an active ticker
  useKpiSnapshot(activeTicker);

  // ── Empty state ───────────────────────────────────────────────────────────
  if (!activeTicker && !isLoading) {
    return <EmptyState />;
  }

  // ── Error state (takes priority over skeleton) ────────────────────────────
  if (error) {
    return (
      <div className="flex flex-1 flex-col items-center justify-center gap-3 p-10 text-center">
        <TriangleAlert className="h-10 w-10 text-hc-accent-red" />
        <p className="text-sm font-semibold text-hc-accent-red">Error al cargar datos</p>
        <p className="max-w-sm text-xs text-hc-text-muted">{error}</p>
      </div>
    );
  }

  // ── Loading state ─────────────────────────────────────────────────────────
  if (isLoading || (activeTicker && !kpiSnapshot)) {
    return (
      <div className="h-full overflow-y-auto">
        <div className="flex min-h-full flex-col gap-4 p-5">
          <AssetHeaderSkeleton />
          <RowSkeleton height="shrink-0" />
          <RowSkeleton height="shrink-0" />
          <div className="flex flex-1 gap-4">
            <Skeleton className="flex-1" />
            <Skeleton className="flex-1" />
            <Skeleton className="flex-1" />
            <Skeleton className="flex-1" />
          </div>
        </div>
      </div>
    );
  }

  // ── Should not reach here — guard ─────────────────────────────────────────
  if (!kpiSnapshot) return <EmptyState />;

  const s = kpiSnapshot;

  return (
    <div className="h-full overflow-y-auto">
      <div className="flex min-h-full flex-col gap-4 p-5">
        <AssetHeader snapshot={s} />

        {/* Top Row: Situation Analysis + Price Levels */}
        <div className="flex shrink-0 gap-4">
          <SituationAnalysis snapshot={s} />
          <PriceLevels snapshot={s} />
        </div>

        {/* Middle Row: Market Status + Seasonality + ATR/Momentum */}
        <div className="flex shrink-0 gap-4">
          <MarketStatus snapshot={s} />
          <Seasonality />
          <div className="flex w-[200px] shrink-0 flex-col gap-4">
            <AtrCard snapshot={s} />
            <MomentumCard snapshot={s} />
          </div>
        </div>

        {/* Bottom Row: Projection + Volatility + Directional + NetBrut */}
        <div className="flex flex-1 gap-4">
          <ProjectionCard snapshot={s} />
          <VolatilityCard snapshot={s} />
          <DirectionalCard snapshot={s} />
          <NetBrutCard />
        </div>
      </div>
    </div>
  );
}
