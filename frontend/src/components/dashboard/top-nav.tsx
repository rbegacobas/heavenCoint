"use client";

import { Bell, Moon, LogOut, Wifi, WifiOff } from "lucide-react";
import { useRouter } from "next/navigation";
import { useQuery } from "@tanstack/react-query";
import { clearToken, request } from "@/lib/api";

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
    refetchInterval: 5 * 60_000, // check every 5 min
    retry: false,
  });
}

export default function TopNav() {
  const router = useRouter();
  const { data: schwab } = useSchwabStatus();

  function handleLogout() {
    clearToken();
    router.push("/login");
  }

  const schwabConnected = schwab?.connected ?? false;
  const schwabWarning = schwab?.needs_relogin ?? false;

  return (
    <div className="flex h-12 items-center justify-between bg-hc-bg-sidebar px-4">
      <span className="text-sm font-bold text-hc-text-white">
        HeavenCoint <span className="font-normal text-hc-text-muted">v2.0</span>
      </span>
      <div className="flex items-center gap-4">

        {/* Schwab connection indicator */}
        <div
          className="flex items-center gap-1.5 cursor-default"
          title={schwab?.message ?? "Verificando conexión Schwab..."}
        >
          {schwabConnected ? (
            <>
              <Wifi
                className={`h-4 w-4 ${schwabWarning ? "text-hc-accent-yellow" : "text-hc-accent-green"}`}
              />
              <span
                className={`text-[10px] font-semibold ${schwabWarning ? "text-hc-accent-yellow" : "text-hc-accent-green"}`}
              >
                {schwabWarning
                  ? `Schwab — relogin ${schwab?.refresh_expires_in_days?.toFixed(0)}d`
                  : `Schwab — ${schwab?.refresh_expires_in_days?.toFixed(1)}d`}
              </span>
            </>
          ) : (
            <>
              <WifiOff className="h-4 w-4 text-hc-text-muted" />
              <span className="text-[10px] text-hc-text-muted">Schwab — desconectado</span>
            </>
          )}
        </div>

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
  );
}
