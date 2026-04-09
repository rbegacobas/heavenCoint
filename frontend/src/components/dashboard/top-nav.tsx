"use client";

import { Bell, Moon, LogOut, Wifi, WifiOff, X, ExternalLink, Copy, Check } from "lucide-react";
import { useRouter } from "next/navigation";
import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { clearToken, schwabApi, request } from "@/lib/api";

interface SchwabStatus {
  connected: boolean;
  refresh_expires_in_days: number | null;
  needs_relogin: boolean;
  message: string;
}

function useSchwabStatus() {
  return useQuery<SchwabStatus>({
    queryKey: ["schwab-status"],
    queryFn: () => request<SchwabStatus>("/schwab/status"),
    staleTime: 60_000,
    refetchInterval: 5 * 60_000,
    retry: false,
  });
}

// ── Schwab Connect Modal ───────────────────────────────────────────────────────

function SchwabModal({ onClose }: { onClose: () => void }) {
  const [step, setStep] = useState<"instructions" | "paste" | "success">("instructions");
  const [authUrl, setAuthUrl] = useState<string>("");
  const [callbackUrl, setCallbackUrl] = useState<string>("");
  const [error, setError] = useState<string>("");
  const [copied, setCopied] = useState(false);
  const queryClient = useQueryClient();

  const getUrlMutation = useMutation({
    mutationFn: () => schwabApi.getAuthUrl(),
    onSuccess: (data) => {
      setAuthUrl(data.auth_url);
      setStep("paste");
    },
    onError: () => setError("No se pudo obtener la URL de autorización."),
  });

  const callbackMutation = useMutation({
    mutationFn: () => schwabApi.callback(callbackUrl.trim()),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["schwab-status"] });
      setStep("success");
    },
    onError: (err: Error) => setError(err.message ?? "Error al conectar con Schwab."),
  });

  const disconnectMutation = useMutation({
    mutationFn: () => schwabApi.disconnect(),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["schwab-status"] });
      onClose();
    },
  });

  function handleCopy() {
    navigator.clipboard.writeText(authUrl);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60">
      <div className="relative w-[480px] rounded-xl bg-white p-6 shadow-2xl">
        {/* Header */}
        <div className="mb-5 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Wifi className="h-5 w-5 text-hc-btn-primary" />
            <span className="text-base font-bold text-hc-text-dark">
              Conectar cuenta Schwab / Thinkorswim
            </span>
          </div>
          <button
            onClick={onClose}
            className="flex h-7 w-7 items-center justify-center rounded-full hover:bg-gray-100"
          >
            <X className="h-4 w-4 text-hc-text-muted" />
          </button>
        </div>

        {/* Step: Instructions */}
        {step === "instructions" && (
          <div className="flex flex-col gap-4">
            <p className="text-sm text-hc-text-secondary">
              Para conectar tu cuenta de corretaje Schwab/Thinkorswim y operar en tiempo real,
              sigue estos pasos:
            </p>
            <ol className="flex flex-col gap-2 text-sm text-hc-text-dark">
              <li className="flex gap-2">
                <span className="flex h-5 w-5 shrink-0 items-center justify-center rounded-full bg-hc-btn-primary text-[10px] font-bold text-white">1</span>
                Haz click en <strong>"Iniciar sesión con Schwab"</strong>
              </li>
              <li className="flex gap-2">
                <span className="flex h-5 w-5 shrink-0 items-center justify-center rounded-full bg-hc-btn-primary text-[10px] font-bold text-white">2</span>
                Se abrirá una URL — ábrela en tu navegador e inicia sesión con tu cuenta Schwab
              </li>
              <li className="flex gap-2">
                <span className="flex h-5 w-5 shrink-0 items-center justify-center rounded-full bg-hc-btn-primary text-[10px] font-bold text-white">3</span>
                Serás redirigido a <code className="rounded bg-gray-100 px-1 text-xs">https://127.0.0.1</code> — puede mostrar error de conexión, eso es <strong>normal</strong>
              </li>
              <li className="flex gap-2">
                <span className="flex h-5 w-5 shrink-0 items-center justify-center rounded-full bg-hc-btn-primary text-[10px] font-bold text-white">4</span>
                Copia la URL completa de la barra del navegador y pégala aquí
              </li>
            </ol>
            {error && <p className="text-xs text-red-500">{error}</p>}
            <button
              onClick={() => getUrlMutation.mutate()}
              disabled={getUrlMutation.isPending}
              className="flex w-full items-center justify-center gap-2 rounded-lg bg-hc-btn-primary py-2.5 text-sm font-semibold text-white transition hover:opacity-90 disabled:opacity-60"
            >
              <ExternalLink className="h-4 w-4" />
              {getUrlMutation.isPending ? "Generando URL..." : "Iniciar sesión con Schwab"}
            </button>
          </div>
        )}

        {/* Step: Paste callback URL */}
        {step === "paste" && (
          <div className="flex flex-col gap-4">
            <div className="rounded-lg border border-dashed border-hc-btn-primary bg-blue-50 p-3">
              <p className="mb-1 text-[11px] font-semibold text-hc-btn-primary">URL de autorización generada</p>
              <p className="break-all text-[10px] text-hc-text-secondary">{authUrl.slice(0, 80)}…</p>
              <div className="mt-2 flex gap-2">
                <a
                  href={authUrl}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="flex items-center gap-1 rounded bg-hc-btn-primary px-2 py-1 text-[10px] font-semibold text-white hover:opacity-90"
                >
                  <ExternalLink className="h-3 w-3" /> Abrir en navegador
                </a>
                <button
                  onClick={handleCopy}
                  className="flex items-center gap-1 rounded border border-hc-btn-primary px-2 py-1 text-[10px] font-semibold text-hc-btn-primary hover:bg-blue-50"
                >
                  {copied ? <Check className="h-3 w-3" /> : <Copy className="h-3 w-3" />}
                  {copied ? "Copiado" : "Copiar"}
                </button>
              </div>
            </div>

            <div className="flex flex-col gap-1.5">
              <label className="text-xs font-semibold text-hc-text-dark">
                Pega aquí la URL de redirección (https://127.0.0.1?code=...)
              </label>
              <textarea
                value={callbackUrl}
                onChange={(e) => setCallbackUrl(e.target.value)}
                placeholder="https://127.0.0.1?code=XXXX&session=YYYY"
                rows={3}
                className="w-full rounded-lg border border-gray-200 p-2.5 text-xs text-hc-text-dark outline-none focus:border-hc-btn-primary"
              />
            </div>

            {error && <p className="text-xs text-red-500">{error}</p>}

            <button
              onClick={() => callbackMutation.mutate()}
              disabled={!callbackUrl.trim() || callbackMutation.isPending}
              className="flex w-full items-center justify-center gap-2 rounded-lg bg-hc-btn-primary py-2.5 text-sm font-semibold text-white transition hover:opacity-90 disabled:opacity-60"
            >
              {callbackMutation.isPending ? "Conectando..." : "Conectar cuenta Schwab"}
            </button>
          </div>
        )}

        {/* Step: Success */}
        {step === "success" && (
          <div className="flex flex-col items-center gap-4 py-4 text-center">
            <div className="flex h-14 w-14 items-center justify-center rounded-full bg-green-100">
              <Wifi className="h-7 w-7 text-hc-accent-green" />
            </div>
            <p className="text-base font-bold text-hc-text-dark">¡Cuenta conectada!</p>
            <p className="text-sm text-hc-text-secondary">
              Tu cuenta Schwab/Thinkorswim está vinculada. Los análisis de acciones US
              ahora usan datos en <span className="font-semibold text-hc-accent-green">tiempo real</span>.
            </p>
            <button
              onClick={onClose}
              className="w-full rounded-lg bg-hc-accent-green py-2.5 text-sm font-semibold text-white hover:opacity-90"
            >
              Ir al dashboard
            </button>
          </div>
        )}

        {/* Disconnect link (only when already connected in instructions step) */}
        {step === "instructions" && (
          <button
            onClick={() => disconnectMutation.mutate()}
            className="mt-3 w-full text-center text-[11px] text-hc-text-muted hover:text-hc-accent-red"
          >
            Desconectar cuenta Schwab
          </button>
        )}
      </div>
    </div>
  );
}

// ── TopNav ────────────────────────────────────────────────────────────────────

export default function TopNav() {
  const router = useRouter();
  const [showSchwabModal, setShowSchwabModal] = useState(false);
  const { data: schwab } = useSchwabStatus();

  function handleLogout() {
    clearToken();
    router.push("/login");
  }

  const schwabConnected = schwab?.connected ?? false;
  const schwabWarning = schwab?.needs_relogin ?? false;

  return (
    <>
      <div className="flex h-12 items-center justify-between bg-hc-bg-sidebar px-4">
        <span className="text-sm font-bold text-hc-text-white">
          HeavenCoint <span className="font-normal text-hc-text-muted">v2.0</span>
        </span>
        <div className="flex items-center gap-4">

          {/* Schwab connection indicator — click to open modal */}
          {schwabConnected ? (
            <button
              onClick={() => setShowSchwabModal(true)}
              className="flex cursor-pointer items-center gap-1.5 rounded-md px-2 py-1 transition hover:bg-hc-bg-input"
              title={schwab?.message ?? "Gestionar conexión Schwab"}
            >
              <Wifi className={`h-4 w-4 ${schwabWarning ? "text-hc-accent-yellow" : "text-hc-accent-green"}`} />
              <span className={`text-[10px] font-semibold ${schwabWarning ? "text-hc-accent-yellow" : "text-hc-accent-green"}`}>
                {schwabWarning
                  ? `Schwab ⚠ ${schwab?.refresh_expires_in_days?.toFixed(0)}d`
                  : `Schwab ✓ ${schwab?.refresh_expires_in_days?.toFixed(1)}d`}
              </span>
            </button>
          ) : (
            <button
              onClick={() => setShowSchwabModal(true)}
              className="group flex cursor-pointer items-center gap-1.5 rounded-md border border-red-400/40 bg-red-500/10 px-2.5 py-1 transition hover:bg-red-500/20 animate-pulse hover:animate-none"
              title="Schwab desconectado — click para conectar"
            >
              <WifiOff className="h-4 w-4 text-red-400 group-hover:text-red-300" />
              <span className="text-[10px] font-semibold text-red-400 group-hover:text-red-300">
                Conectar Schwab
              </span>
            </button>
          )}

          <Bell className="h-4 w-4 text-hc-text-muted" />
          <Moon className="h-4 w-4 text-hc-text-muted" />
          <div className="flex items-center gap-3">
            <div className="flex h-7 w-7 items-center justify-center rounded-full bg-hc-btn-primary text-[10px] font-bold text-hc-text-white">
              F
            </div>
            <span className="text-xs text-hc-text-white">Fernando</span>
            <button
              onClick={handleLogout}
              title="Cerrar sesión"
              className="flex h-7 w-7 items-center justify-center rounded hover:bg-hc-bg-input transition-colors"
            >
              <LogOut className="h-4 w-4 text-hc-text-muted hover:text-hc-accent-red" />
            </button>
          </div>
        </div>
      </div>

      {showSchwabModal && <SchwabModal onClose={() => setShowSchwabModal(false)} />}
    </>
  );
}
