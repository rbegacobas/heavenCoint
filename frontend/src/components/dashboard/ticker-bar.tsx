"use client";

import { TrendingUp, TrendingDown } from "lucide-react";

type TickerItem = {
  name: string;
  price: string;
  change: string;
  positive: boolean;
};

const tickers: TickerItem[] = [
  { name: "Bitcoin USD", price: "65,019.77", change: "+1.47%", positive: true },
  { name: "GBP/JPY", price: "210.92", change: "+1.07%", positive: true },
  { name: "HCA Healthcare", price: "526.52", change: "-1.76%", positive: false },
  { name: "Palantir", price: "128.84", change: "-1.35%", positive: false },
  { name: "Uber", price: "71.38", change: "+0.93%", positive: true },
  { name: "Gold", price: "5,206.70", change: "+0.99%", positive: true },
  { name: "Visa", price: "307.22", change: "+0.23%", positive: true },
];

export default function TickerBar() {
  return (
    <div className="flex h-8 items-center gap-6 overflow-x-auto bg-hc-bg-ticker px-4">
      {tickers.map((t) => (
        <div key={t.name} className="flex shrink-0 items-center gap-2">
          <span className="text-[11px] font-medium text-hc-text-white">{t.name}</span>
          <span className="text-[11px] text-hc-text-muted">{t.price}</span>
          <span
            className={`flex items-center gap-0.5 text-[11px] font-medium ${
              t.positive ? "text-hc-accent-green" : "text-hc-accent-red"
            }`}
          >
            {t.positive ? (
              <TrendingUp className="h-3 w-3" />
            ) : (
              <TrendingDown className="h-3 w-3" />
            )}
            {t.change}
          </span>
        </div>
      ))}
    </div>
  );
}
