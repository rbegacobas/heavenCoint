"use client";

import { Bell, Moon, LogOut } from "lucide-react";
import { useRouter } from "next/navigation";
import { clearToken } from "@/lib/api";

export default function TopNav() {
  const router = useRouter();

  function handleLogout() {
    clearToken();
    router.push("/login");
  }

  return (
    <div className="flex h-12 items-center justify-between bg-hc-bg-sidebar px-4">
      <span className="text-sm font-bold text-hc-text-white">
        HeavenCoint <span className="font-normal text-hc-text-muted">v2.0</span>
      </span>
      <div className="flex items-center gap-4">
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
