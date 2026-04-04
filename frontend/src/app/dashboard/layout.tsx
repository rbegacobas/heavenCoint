import TickerBar from "@/components/dashboard/ticker-bar";
import TopNav from "@/components/dashboard/top-nav";
import LeftSidebar from "@/components/dashboard/left-sidebar";
import RightSidebar from "@/components/dashboard/right-sidebar";

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
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
