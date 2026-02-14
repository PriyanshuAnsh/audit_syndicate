"use client";

import { useQuery } from "@tanstack/react-query";
import Nav from "../../components/nav";
import { api } from "../../lib/api";

export default function PortfolioPage() {
  const portfolio = useQuery({ queryKey: ["portfolio"], queryFn: () => api("/portfolio") });

  return (
    <div className="space-y-4">
      <Nav />
      <div className="glass p-5">
        <h1 className="page-title">Portfolio</h1>
        <p className="page-subtitle">Monitor value, allocation mix, and diversification health.</p>
      </div>
      {portfolio.data && (
        <>
          <div className="grid gap-3 md:grid-cols-4">
            <div className="kpi"><p className="text-sm text-slate-500">Cash</p><p className="text-2xl font-semibold">${portfolio.data.cash.toFixed(2)}</p></div>
            <div className="kpi"><p className="text-sm text-slate-500">Total Value</p><p className="text-2xl font-semibold">${portfolio.data.total_value.toFixed(2)}</p></div>
            <div className="kpi"><p className="text-sm text-slate-500">Unrealized P/L</p><p className={`text-2xl font-semibold ${portfolio.data.total_pl >= 0 ? "text-emerald-700" : "text-red-700"}`}>${portfolio.data.total_pl.toFixed(2)}</p></div>
            <div className="kpi"><p className="text-sm text-slate-500">Diversification</p><p className="text-2xl font-semibold">{portfolio.data.diversification_score}%</p></div>
          </div>
          <div className="glass overflow-x-auto p-3">
            <table className="w-full min-w-[680px] text-sm">
              <thead>
                <tr className="text-left text-slate-600">
                  <th className="p-2">Symbol</th><th className="p-2">Qty</th><th className="p-2">Avg Cost</th><th className="p-2">Price</th><th className="p-2">Value</th><th className="p-2">P/L</th><th className="p-2">Allocation</th>
                </tr>
              </thead>
              <tbody>
                {portfolio.data.positions.map((p: any) => (
                  <tr key={p.symbol} className="border-t border-slate-200/70">
                    <td className="p-2 font-semibold">{p.symbol}</td>
                    <td className="p-2">{p.quantity}</td>
                    <td className="p-2">${p.avg_cost.toFixed(2)}</td>
                    <td className="p-2">${p.market_price.toFixed(2)}</td>
                    <td className="p-2">${p.market_value.toFixed(2)}</td>
                    <td className={`p-2 ${p.unrealized_pl >= 0 ? "text-emerald-700" : "text-red-700"}`}>${p.unrealized_pl.toFixed(2)}</td>
                    <td className="p-2">{p.allocation_pct}%</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </>
      )}
    </div>
  );
}
