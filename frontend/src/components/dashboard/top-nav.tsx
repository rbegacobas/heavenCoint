"use client";

import { Bell, Moon } from "lucide-react";

export default function TopNav() {
  return (
    <div className="flex h-12 items-center justify-between bg-hc-bg-sidebar px-4">
      <span className="text-sm font-bold text-hc-text-white">
        HeavenCoint <span className="font-normal text-hc-text-muted">v2.0</span>
      </span>
      <div className="flex items-center gap-4">
        <Bell className="h-4 w-4 text-hc-text-muted" />
        <Moon className="h-4 w-4 text-hc-text-muted" />
        <div className="flex items-center gap-2">
          <div className="flex h-7 w-7 items-center justify-center rounded-full bg-hc-btn-primary text-[10px] font-bold text-hc-text-white">
            F
          </div>
          <span className="text-xs text-hc-text-white">Fernando</span>
        </div>
      </div>
    </div>
  );
}
