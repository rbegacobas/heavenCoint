"use client";

import { TriangleAlert, X } from "lucide-react";
import { useState } from "react";

interface ErrorBannerProps {
  message: string;
  onDismiss?: () => void;
}

export function ErrorBanner({ message, onDismiss }: ErrorBannerProps) {
  const [dismissed, setDismissed] = useState(false);

  if (dismissed) return null;

  function handleDismiss() {
    setDismissed(true);
    onDismiss?.();
  }

  return (
    <div className="flex items-center gap-2 bg-red-900/80 px-4 py-2 text-xs text-red-100">
      <TriangleAlert className="h-3.5 w-3.5 shrink-0 text-hc-accent-red" />
      <span className="flex-1">{message}</span>
      {onDismiss && (
        <button
          onClick={handleDismiss}
          className="ml-2 shrink-0 opacity-70 hover:opacity-100"
          aria-label="Cerrar alerta"
        >
          <X className="h-3 w-3" />
        </button>
      )}
    </div>
  );
}

interface StaleBannerProps {
  lastRefreshed: string | null;
}

export function StaleBanner({ lastRefreshed }: StaleBannerProps) {
  const timestamp = lastRefreshed
    ? new Date(lastRefreshed).toLocaleTimeString("es-ES", {
        hour: "2-digit",
        minute: "2-digit",
        second: "2-digit",
      })
    : "desconocido";

  return (
    <ErrorBanner
      message={`⚠️ Datos no actualizados desde ${timestamp}. No opere hasta que se restaure la conexión.`}
    />
  );
}
