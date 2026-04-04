"use client";

import { Send } from "lucide-react";

export default function RightSidebar() {
  return (
    <aside className="flex w-80 shrink-0 flex-col bg-hc-bg-sidebar">
      {/* Top Section: Header + Tabs */}
      <div className="flex flex-col gap-3 p-4">
        <div className="flex items-center justify-between">
          <span className="text-[13px] font-bold text-hc-text-white">TOP Acciones Semana</span>
          <span className="text-[11px] text-hc-text-muted">25/02/26</span>
        </div>
        <div className="flex h-8 overflow-hidden rounded-md">
          <button className="flex flex-1 items-center justify-center bg-hc-bg-input text-[11px] font-medium text-hc-text-muted">
            HeavenBuilder
          </button>
          <button className="flex flex-1 items-center justify-center bg-hc-btn-primary text-[11px] font-semibold text-hc-text-white">
            HeavenPilot
          </button>
        </div>
      </div>

      <div className="h-px bg-hc-border-dark" />

      {/* Chat Section */}
      <div className="flex flex-1 flex-col gap-3 p-4">
        <div className="flex flex-col gap-1">
          <span className="text-sm font-bold text-hc-text-white">Asistente Heaven</span>
          <span className="text-[10px] text-hc-text-muted">Te quedan 400 mensajes</span>
        </div>

        {/* Toggle */}
        <div className="flex items-center gap-2">
          <div className="flex h-[18px] w-8 items-center justify-end rounded-full bg-hc-btn-primary p-0.5">
            <div className="h-3.5 w-3.5 rounded-full bg-white" />
          </div>
          <span className="text-[11px] text-hc-text-muted">Respuesta reducida</span>
        </div>

        {/* Chat content */}
        <div className="flex flex-1 flex-col gap-2.5 overflow-y-auto rounded-lg bg-hc-bg-input p-3">
          <p className="text-[11px] leading-5 text-hc-text-white">
            ¡Hola! Soy tu asistente de inversiones Heaven. Estoy aquí para ayudarte a interpretar
            los reportes de análisis y crear estrategias de inversión.
          </p>
          <p className="text-[11px] font-semibold text-hc-text-white">Puedo ayudarte con:</p>
          <p className="text-[11px] leading-6 text-hc-text-muted">
            • Interpretar reportes de análisis técnico
            <br />
            • Crear estrategias de inversión personalizadas
            <br />
            • Explicar indicadores y métricas
            <br />• Comparar activos y sectores
          </p>
          <p className="text-[11px] font-semibold text-hc-text-white">No puedo:</p>
          <p className="text-[11px] leading-6 text-hc-text-muted">
            • Dar consejos financieros definitivos
            <br />
            • Garantizar rendimientos
            <br />• Ejecutar operaciones directamente
          </p>
        </div>

        {/* Input bar */}
        <div className="flex h-10 items-center gap-2">
          <div className="flex flex-1 items-center rounded-lg bg-hc-bg-input px-3 py-2">
            <span className="text-xs text-hc-text-muted">Escribe tu mensaje...</span>
          </div>
          <button className="flex h-10 w-10 shrink-0 items-center justify-center rounded-lg bg-hc-btn-primary">
            <Send className="h-4 w-4 text-white" />
          </button>
        </div>
      </div>
    </aside>
  );
}
