"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useMemo, useState } from "react";
import Nav from "../../components/nav";
import { api } from "../../lib/api";

type Quote = {
  symbol: string;
  price: number;
  as_of: string;
};

export default function TradePage() {
  const qc = useQueryClient();
  const quotes = useQuery<Quote[]>({ queryKey: ["quotes"], queryFn: () => api("/market/quotes") });
  const [symbol, setSymbol] = useState("AAPL");
  const [quantity, setQuantity] = useState("1");
  const [lastAction, setLastAction] = useState<"buy" | "sell" | null>(null);

  const trade = useMutation({
    mutationFn: ({ side }: { side: "buy" | "sell" }) =>
      api(`/trades/${side}`, {
        method: "POST",
        body: JSON.stringify({ symbol, quantity: Number(quantity) }),
      }),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["quotes"] });
      qc.invalidateQueries({ queryKey: ["portfolio"] });
      qc.invalidateQueries({ queryKey: ["me"] });
    },
  });

  const selectedQuote = useMemo(
    () => (quotes.data || []).find((quote) => quote.symbol === symbol.toUpperCase()),
    [quotes.data, symbol]
  );
  const quantityNumber = Number(quantity) || 0;
  const notional = (selectedQuote?.price || 0) * quantityNumber;

  return (
    <div className="space-y-4">
      <Nav />
      <div className="glass p-5 md:p-6">
        <div className="flex flex-wrap items-start justify-between gap-4">
          <div>
            <h1 className="page-title">Trade Terminal</h1>
            <p className="page-subtitle">Execute simulated market orders with real-time quote context and clean order controls.</p>
          </div>
          <div className="grid min-w-[240px] grid-cols-2 gap-2 text-sm">
            <div className="rounded-xl bg-white/80 p-3">
              <p className="text-slate-500">Selected Symbol</p>
              <p className="text-lg font-semibold">{symbol.toUpperCase()}</p>
            </div>
            <div className="rounded-xl bg-white/80 p-3">
              <p className="text-slate-500">Last Price</p>
              <p className="text-lg font-semibold">{selectedQuote ? `$${selectedQuote.price.toFixed(2)}` : "--"}</p>
            </div>
          </div>
        </div>
      </div>

      <div className="grid gap-4 xl:grid-cols-[1.3fr_1fr]">
        <div className="glass overflow-hidden">
          <div className="border-b border-slate-200/70 bg-white/70 px-4 py-3">
            <h2 className="text-lg font-semibold">Market Watchlist</h2>
          </div>
          <div className="max-h-[560px] overflow-auto">
            <table className="w-full min-w-[520px] text-sm">
              <thead className="sticky top-0 bg-[#f8f8f2] text-left text-slate-500">
                <tr>
                  <th className="px-4 py-3 font-medium">Symbol</th>
                  <th className="px-4 py-3 font-medium">Price</th>
                  <th className="px-4 py-3 font-medium">Type</th>
                  <th className="px-4 py-3 font-medium">Action</th>
                </tr>
              </thead>
              <tbody>
                {(quotes.data || []).map((quote) => {
                  const isActive = quote.symbol === symbol.toUpperCase();
                  return (
                    <tr key={quote.symbol} className={`border-t border-slate-200/70 ${isActive ? "bg-emerald-50/70" : "bg-transparent"}`}>
                      <td className="px-4 py-3 font-semibold">{quote.symbol}</td>
                      <td className="px-4 py-3">${quote.price.toFixed(2)}</td>
                      <td className="px-4 py-3 text-slate-600">{quote.symbol.length <= 4 ? "Stock" : "Crypto"}</td>
                      <td className="px-4 py-3">
                        <button
                          className={isActive ? "rounded-lg bg-emerald-700 px-3 py-1.5 text-xs font-semibold text-white" : "rounded-lg border border-slate-300 bg-white px-3 py-1.5 text-xs font-semibold"}
                          onClick={() => setSymbol(quote.symbol)}
                        >
                          {isActive ? "Selected" : "Select"}
                        </button>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </div>

        <div className="space-y-4">
          <div className="glass p-4">
            <h2 className="mb-3 text-lg font-semibold">Order Ticket</h2>
            <label className="mb-1 block text-xs font-semibold uppercase tracking-wide text-slate-500">Symbol</label>
            <input className="input mb-3" value={symbol} onChange={(e) => setSymbol(e.target.value.toUpperCase())} placeholder="AAPL" />

            <label className="mb-1 block text-xs font-semibold uppercase tracking-wide text-slate-500">Quantity</label>
            <input className="input mb-3" value={quantity} onChange={(e) => setQuantity(e.target.value)} placeholder="1" type="number" min="0.0001" step="0.0001" />

            <div className="mb-3 rounded-xl bg-white/80 p-3 text-sm">
              <div className="flex items-center justify-between">
                <span className="text-slate-500">Order Type</span>
                <span className="font-medium">Market</span>
              </div>
              <div className="mt-1 flex items-center justify-between">
                <span className="text-slate-500">Estimated Notional</span>
                <span className="font-semibold">{notional > 0 ? `$${notional.toFixed(2)}` : "--"}</span>
              </div>
            </div>

            <div className="flex gap-2">
              <button
                className="flex-1 rounded-xl bg-emerald-700 px-4 py-2 font-medium text-white transition hover:bg-emerald-800"
                onClick={() => {
                  setLastAction("buy");
                  trade.mutate({ side: "buy" });
                }}
              >
                Buy
              </button>
              <button
                className="flex-1 rounded-xl bg-rose-700 px-4 py-2 font-medium text-white transition hover:bg-rose-800"
                onClick={() => {
                  setLastAction("sell");
                  trade.mutate({ side: "sell" });
                }}
              >
                Sell
              </button>
            </div>

            {trade.isPending && <p className="mt-2 text-sm text-slate-600">Submitting order...</p>}
            {trade.isSuccess && lastAction && <p className="mt-2 text-sm text-emerald-700">Order filled: {lastAction.toUpperCase()} {quantityNumber} {symbol.toUpperCase()}.</p>}
            {trade.error && <p className="mt-2 text-sm text-red-700">{(trade.error as Error).message}</p>}
          </div>

          <div className="glass p-4">
            <h3 className="mb-2 text-sm font-semibold uppercase tracking-wide text-slate-500">Execution Notes</h3>
            <ul className="space-y-2 text-sm text-slate-700">
              <li className="rounded-lg bg-white/75 px-3 py-2">Prices are simulated and refreshed in near real-time.</li>
              <li className="rounded-lg bg-white/75 px-3 py-2">Orders execute as market fills using current quote.</li>
              <li className="rounded-lg bg-white/75 px-3 py-2">No leverage or short selling in this environment.</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
}
