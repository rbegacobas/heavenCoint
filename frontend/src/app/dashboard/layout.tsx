"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { getToken } from "@/lib/api";
import TickerBar from "@/components/dashboard/ticker-bar";
import TopNav from "@/components/dashboard/top-nav";
import LeftSidebar from "@/components/dashboard/left-sidebar";
import RightSidebar from "@/components/dashboard/right-sidebar";

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const router = useRouter();

  useEffect(() => {
    if (!getToken()) {
      router.replace("/login");
    }
  }, [router]);

  // Don't flash the dashboard if not authenticated
  if (typeof window !== "undefined" && !getToken()) return null;

  return (
    <div className="flex h-screen flex-col bg-hc-bg-dark">
      <TickerBar />
      <TopNav />
      <div className="flex flex-1 overflow-hidden">
        <LeftSidebar />
        <main className="flex flex-1 flex-col overflow-hidden">{children}</main>
        <RightSidebar />
      </div>
    </div>
  );
}
