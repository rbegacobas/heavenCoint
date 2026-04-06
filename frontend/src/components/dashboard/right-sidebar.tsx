"use client";

import { useState } from "react";
import { Send, TrendingUp, TrendingDown, AlertTriangle, CheckCircle, Loader2 } from "lucide-react";
import { useAssetStore } from "@/stores/asset-store";
import { strategiesApi } from "@/lib/api";
import { StrategyResult } from "@/types/api";
import { ApiError } from "@/types/api";

// ── Strategy Card ─────────────────────────────────────────────────────────────

function StrategyCard({ s }: { s: StrategyResult }) {
  const isLong = s.direction === "LONG";
  const dirColor = isLong ? "#22C55E" : "#EF4444";

  function fmt(n: number) {
    if (n >= 1000) return n.toLocaleString("en-US", { maximumFractionDigits: 2 });
    if (n < 0.1) return n.toFixed(6);
    return n.toFixed(4);
  }

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 10 }}>
      {/* Header */}
      <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between" }}>
        <div style={{ display: "flex", alignItems: "center", gap: 6 }}>
          {isLong
            ? <TrendingUp size={14} color={dirColor} />
            : <TrendingDown size={14} color={dirColor} />}
          <span style={{ color: dirColor, fontSize: 12, fontWeight: 700 }}>
            {s.direction} — {s.ticker}
          </span>
        </div>
        {s.is_recommended ? (
          <div style={{ display: "flex", alignItems: "center", gap: 4, backgroundColor: "rgba(34,197,94,0.15)", border: "1px solid rgba(34,197,94,0.4)", borderRadius: 6, padding: "2px 8px" }}>
            <CheckCircle size={10} color="#22C55E" />
            <span style={{ color: "#22C55E", fontSize: 10, fontWeight: 700 }}>RECOMENDADA</span>
          </div>
        ) : (
          <div style={{ display: "flex", alignItems: "center", gap: 4, backgroundColor: "rgba(239,68,68,0.15)", border: "1px solid rgba(239,68,68,0.4)", borderRadius: 6, padding: "2px 8px" }}>
            <AlertTriangle size={10} color="#EF4444" />
            <span style={{ color: "#EF4444", fontSize: 10, fontWeight: 700 }}>R:R BAJO</span>
          </div>
        )}
      </div>

      {/* Levels */}
      <div style={{ backgroundColor: "#2A2D52", borderRadius: 8, padding: "10px 12px", display: "flex", flexDirection: "column", gap: 6 }}>
        {[
          { label: "Entrada", value: fmt(s.entry_price), color: "#FFFFFF" },
          { label: `Stop Loss  (ATR×${s.sl_atr_mult})`, value: fmt(s.stop_loss), color: "#EF4444" },
          { label: `TP1 — ${s.tp1_pct}%`, value: fmt(s.tp1), color: "#22C55E" },
          { label: `TP2 — ${s.tp2_pct}%`, value: fmt(s.tp2), color: "#22C55E" },
          { label: `TP3 — ${s.tp3_pct}% (trailing ×${s.tp3_trailing_atr_mult})`, value: "Trailing", color: "#06B6D4" },
        ].map(({ label, value, color }) => (
          <div key={label} style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
            <span style={{ color: "#A0A4B8", fontSize: 10 }}>{label}</span>
            <span style={{ color, fontSize: 11, fontWeight: 600 }}>{value}</span>
          </div>
        ))}
      </div>

      {/* Stats */}
      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 6 }}>
        {[
          { label: "Posición", value: `${s.n_shares.toFixed(4)} uds` },
          { label: "Riesgo $", value: `$${s.risk_amount.toFixed(2)}` },
          { label: "R:R ratio", value: `1 : ${s.rr_ratio.toFixed(2)}` },
          { label: "ATR usado", value: fmt(s.atr_used) },
        ].map(({ label, value }) => (
          <div key={label} style={{ backgroundColor: "#2A2D52", borderRadius: 6, padding: "6px 10px" }}>
            <div style={{ color: "#A0A4B8", fontSize: 9, marginBottom: 2 }}>{label}</div>
            <div style={{ color: "#FFFFFF", fontSize: 11, fontWeight: 600 }}>{value}</div>
          </div>
        ))}
      </div>

      {s.warning && (
        <div style={{ display: "flex", alignItems: "center", gap: 6, backgroundColor: "rgba(245,158,11,0.1)", border: "1px solid rgba(245,158,11,0.3)", borderRadius: 6, padding: "6px 10px" }}>
          <AlertTriangle size={10} color="#F59E0B" />
          <span style={{ color: "#F59E0B", fontSize: 10 }}>{s.warning}</span>
        </div>
      )}
    </div>
  );
}

// ── HeavenBuilder Tab ─────────────────────────────────────────────────────────

function HeavenBuilderTab() {
  const { activeTicker } = useAssetStore();
  const [direction, setDirection] = useState<"LONG" | "SHORT">("LONG");
  const [capital, setCapital] = useState("10000");
  const [riskPct, setRiskPct] = useState("1");
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<StrategyResult | null>(null);
  const [error, setError] = useState<string | null>(null);

  async function handleGenerate() {
    if (!activeTicker) return;
    setLoading(true);
    setError(null);
    setResult(null);
    try {
      const r = await strategiesApi.calculate({
        ticker: activeTicker,
        direction,
        capital: parseFloat(capital),
        risk_pct: parseFloat(riskPct) / 100,
      });
      setResult(r);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Error al calcular estrategia");
    } finally {
      setLoading(false);
    }
  }

  if (!activeTicker) {
    return (
      <div style={{ padding: "16px 0", textAlign: "center" }}>
        <p style={{ color: "#A0A4B8", fontSize: 11 }}>Carga un activo primero para generar una estrategia.</p>
      </div>
    );
  }

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 12 }}>
      {/* Direction toggle */}
      <div>
        <p style={{ color: "#A0A4B8", fontSize: 10, marginBottom: 6, fontWeight: 600 }}>DIRECCIÓN</p>
        <div style={{ display: "flex", height: 32, overflow: "hidden", borderRadius: 6 }}>
          {(["LONG", "SHORT"] as const).map((d) => (
            <button
              key={d}
              onClick={() => setDirection(d)}
              style={{
                flex: 1, border: "none", cursor: "pointer", fontSize: 11, fontWeight: 700,
                backgroundColor: direction === d ? (d === "LONG" ? "#22C55E" : "#EF4444") : "#2A2D52",
                color: direction === d ? "#FFFFFF" : "#A0A4B8",
                transition: "all 0.15s",
              }}
            >
              {d === "LONG" ? "▲ LONG" : "▼ SHORT"}
            </button>
          ))}
        </div>
      </div>

      {/* Capital */}
      <div>
        <label style={{ color: "#A0A4B8", fontSize: 10, fontWeight: 600, display: "block", marginBottom: 6 }}>
          CAPITAL ($)
        </label>
        <input
          type="number" value={capital} min="100"
          onChange={(e) => setCapital(e.target.value)}
          style={{ width: "100%", height: 36, backgroundColor: "#2A2D52", border: "1px solid #2A2D52", borderRadius: 6, color: "#FFFFFF", fontSize: 13, padding: "0 10px", outline: "none", boxSizing: "border-box" }}
          onFocus={(e) => { e.target.style.borderColor = "#6366F1"; }}
          onBlur={(e) => { e.target.style.borderColor = "#2A2D52"; }}
        />
      </div>

      {/* Risk % slider */}
      <div>
        <div style={{ display: "flex", justifyContent: "space-between", marginBottom: 6 }}>
          <label style={{ color: "#A0A4B8", fontSize: 10, fontWeight: 600 }}>RIESGO POR OPERACIÓN</label>
          <span style={{ color: "#6366F1", fontSize: 11, fontWeight: 700 }}>{riskPct}%</span>
        </div>
        <input
          type="range" min="0.5" max="3" step="0.5" value={riskPct}
          onChange={(e) => setRiskPct(e.target.value)}
          style={{ width: "100%", accentColor: "#6366F1" }}
        />
        <div style={{ display: "flex", justifyContent: "space-between" }}>
          <span style={{ color: "#A0A4B8", fontSize: 9 }}>0.5%</span>
          <span style={{ color: "#A0A4B8", fontSize: 9 }}>3% (máx)</span>
        </div>
      </div>

      {/* Generate button */}
      <button
        onClick={handleGenerate} disabled={loading}
        style={{
          height: 38, backgroundColor: loading ? "#2A2D52" : "#6366F1",
          border: "none", borderRadius: 8, color: "#FFFFFF", fontSize: 12, fontWeight: 700,
          cursor: loading ? "not-allowed" : "pointer", display: "flex", alignItems: "center",
          justifyContent: "center", gap: 6, transition: "background-color 0.15s",
        }}
      >
        {loading ? <Loader2 size={14} className="animate-spin" /> : null}
        {loading ? "Calculando..." : `Generar Estrategia — ${activeTicker}`}
      </button>

      {error && (
        <div style={{ backgroundColor: "rgba(239,68,68,0.15)", border: "1px solid rgba(239,68,68,0.4)", borderRadius: 6, padding: "8px 12px", color: "#F87171", fontSize: 11 }}>
          {error}
        </div>
      )}

      {result && <StrategyCard s={result} />}
    </div>
  );
}

// ── Right Sidebar ─────────────────────────────────────────────────────────────

export default function RightSidebar() {
  const [activeTab, setActiveTab] = useState<"builder" | "pilot">("builder");

  return (
    <aside className="flex w-80 shrink-0 flex-col bg-hc-bg-sidebar">
      {/* Header + Tabs */}
      <div className="flex flex-col gap-3 p-4">
        <div className="flex items-center justify-between">
          <span className="text-[13px] font-bold text-hc-text-white">TOP Acciones Semana</span>
          <span className="text-[11px] text-hc-text-muted">25/02/26</span>
        </div>
        <div className="flex h-8 overflow-hidden rounded-md">
          <button
            onClick={() => setActiveTab("builder")}
            className={`flex flex-1 items-center justify-center text-[11px] font-medium transition-colors ${
              activeTab === "builder"
                ? "bg-hc-btn-primary font-semibold text-hc-text-white"
                : "bg-hc-bg-input text-hc-text-muted"
            }`}
          >
            HeavenBuilder
          </button>
          <button
            onClick={() => setActiveTab("pilot")}
            className={`flex flex-1 items-center justify-center text-[11px] font-medium transition-colors ${
              activeTab === "pilot"
                ? "bg-hc-btn-primary font-semibold text-hc-text-white"
                : "bg-hc-bg-input text-hc-text-muted"
            }`}
          >
            HeavenPilot
          </button>
        </div>
      </div>

      <div className="h-px bg-hc-border-dark" />

      {/* Tab content */}
      <div className="flex flex-1 flex-col gap-3 overflow-y-auto p-4">
        {activeTab === "builder" ? (
          <>
            <div>
              <span className="text-sm font-bold text-hc-text-white">HeavenBuilder</span>
              <p className="text-[10px] text-hc-text-muted mt-0.5">
                Gestión de riesgo matemática — Python calcula, tú decides.
              </p>
            </div>
            <HeavenBuilderTab />
          </>
        ) : (
          <>
            <div className="flex flex-col gap-1">
              <span className="text-sm font-bold text-hc-text-white">Asistente Heaven</span>
              <span className="text-[10px] text-hc-text-muted">Te quedan 400 mensajes</span>
            </div>

            <div className="flex items-center gap-2">
              <div className="flex h-[18px] w-8 items-center justify-end rounded-full bg-hc-btn-primary p-0.5">
                <div className="h-3.5 w-3.5 rounded-full bg-white" />
              </div>
              <span className="text-[11px] text-hc-text-muted">Respuesta reducida</span>
            </div>

            <div className="flex flex-1 flex-col gap-2.5 overflow-y-auto rounded-lg bg-hc-bg-input p-3">
              <p className="text-[11px] leading-5 text-hc-text-white">
                ¡Hola! Soy tu asistente de inversiones Heaven. Estoy aquí para ayudarte a interpretar
                los reportes de análisis y crear estrategias de inversión.
              </p>
              <p className="text-[11px] font-semibold text-hc-text-white">Puedo ayudarte con:</p>
              <p className="text-[11px] leading-6 text-hc-text-muted">
                • Interpretar reportes de análisis técnico
                <br />• Crear estrategias personalizadas
                <br />• Explicar indicadores y métricas
              </p>
            </div>

            <div className="flex h-10 items-center gap-2">
              <div className="flex flex-1 items-center rounded-lg bg-hc-bg-input px-3 py-2">
                <span className="text-xs text-hc-text-muted">Escribe tu mensaje...</span>
              </div>
              <button className="flex h-10 w-10 shrink-0 items-center justify-center rounded-lg bg-hc-btn-primary">
                <Send className="h-4 w-4 text-white" />
              </button>
            </div>
          </>
        )}
      </div>
    </aside>
  );
}
