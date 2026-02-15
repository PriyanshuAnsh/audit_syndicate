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

  const quotes = useQuery<Quote[]>({
    queryKey: ["quotes"],
    queryFn: () => api("/market/quotes"),
  });

  const me = useQuery({
    queryKey: ["me"],
    queryFn: () => api("/me"),
  });

  const [symbol, setSymbol] = useState("AAPL");
  const [quantity, setQuantity] = useState("1");
  const [lastAction, setLastAction] = useState<"buy" | "sell" | null>(null);
  const [confirmOpen, setConfirmOpen] = useState(false);
  const [pendingSide, setPendingSide] = useState<"buy" | "sell" | null>(null);

  const trade = useMutation({
    mutationFn: ({ side }: { side: "buy" | "sell" }) =>
      api(`/trades/${side}`, {
        method: "POST",
        body: JSON.stringify({
          symbol,
          quantity: Number(quantity),
        }),
      }),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["quotes"] });
      qc.invalidateQueries({ queryKey: ["portfolio"] });
      qc.invalidateQueries({ queryKey: ["me"] });
    },
  });

  const selectedQuote = useMemo(
    () =>
      (quotes.data || []).find(
        (quote) => quote.symbol === symbol.toUpperCase()
      ),
    [quotes.data, symbol]
  );

  const quantityNumber = Number(quantity) || 0;
  const notional = (selectedQuote?.price || 0) * quantityNumber;
  const availableCash = me.data?.cash_balance ?? 0;
  const insufficientFunds = notional > availableCash;
  const isLargeTrade = notional > availableCash * 0.5;

  const isInvalid = !selectedQuote || quantityNumber <= 0;

  return (
    <div className="space-y-4">
      <Nav />

      <div className="glass p-5 md:p-6">
        <div className="flex flex-wrap items-start justify-between gap-4">
          <div>
            <h1 className="page-title">Trade Terminal</h1>
            <p className="page-subtitle">
              Execute simulated market orders with real-time quote context.
            </p>
          </div>
          <div className="grid min-w-[240px] grid-cols-2 gap-2 text-sm">
            <div className="rounded-xl bg-white/80 p-3">
              <p className="text-slate-500">Selected Symbol</p>
              <p className="text-lg font-semibold">{symbol.toUpperCase()}</p>
            </div>
            <div className="rounded-xl bg-white/80 p-3">
              <p className="text-slate-500">Last Price</p>
              <p className="text-lg font-semibold">
                {selectedQuote
                  ? `$${selectedQuote.price.toFixed(2)}`
                  : "--"}
              </p>
            </div>
          </div>
        </div>
      </div>

      <div className="grid gap-4 xl:grid-cols-[1.3fr_1fr]">
        {/* LEFT SIDE */}
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
                  const isActive =
                    quote.symbol === symbol.toUpperCase();
                  return (
                    <tr
                      key={quote.symbol}
                      className={`border-t border-slate-200/70 ${
                        isActive
                          ? "bg-emerald-50/70"
                          : "bg-transparent"
                      }`}
                    >
                      <td className="px-4 py-3 font-semibold">
                        {quote.symbol}
                      </td>
                      <td className="px-4 py-3">
                        ${quote.price.toFixed(2)}
                      </td>
                      <td className="px-4 py-3 text-slate-600">
                        {quote.symbol.length <= 4
                          ? "Stock"
                          : "Crypto"}
                      </td>
                      <td className="px-4 py-3">
                        <button
                          className={
                            isActive
                              ? "rounded-lg bg-emerald-700 px-3 py-1.5 text-xs font-semibold text-white"
                              : "rounded-lg border border-slate-300 bg-white px-3 py-1.5 text-xs font-semibold"
                          }
                          onClick={() =>
                            setSymbol(quote.symbol)
                          }
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

        {/* RIGHT SIDE */}
        <div className="space-y-4">
          <div className="glass p-4">
            <h2 className="mb-3 text-lg font-semibold">
              Order Ticket
            </h2>

            <input
              className="input mb-3"
              value={symbol}
              onChange={(e) =>
                setSymbol(e.target.value.toUpperCase())
              }
            />

            <input
              className="input mb-3"
              value={quantity}
              onChange={(e) =>
                setQuantity(e.target.value)
              }
              type="number"
              min="1"
            />

            <div className="mb-3 rounded-xl bg-white/80 p-3 text-sm">
              <div className="flex items-center justify-between">
                <span className="text-slate-500">
                  Estimated Notional
                </span>
                <span className="font-semibold">
                  {notional > 0
                    ? `$${notional.toFixed(2)}`
                    : "--"}
                </span>
              </div>
            </div>

            <div className="flex gap-2">
              <button
                disabled={isInvalid || insufficientFunds}
                className="flex-1 rounded-xl bg-emerald-700 px-4 py-2 font-medium text-white transition hover:bg-emerald-800 disabled:bg-slate-400"
                onClick={() => {
                  setPendingSide("buy");
                  setConfirmOpen(true);
                }}
              >
                Buy
              </button>

              <button
                disabled={isInvalid}
                className="flex-1 rounded-xl bg-rose-700 px-4 py-2 font-medium text-white transition hover:bg-rose-800 disabled:bg-slate-400"
                onClick={() => {
                  setPendingSide("sell");
                  setConfirmOpen(true);
                }}
              >
                Sell
              </button>
            </div>

            {insufficientFunds && (
              <p className="mt-2 text-sm text-rose-600">
                Insufficient funds. Available: $
                {availableCash.toFixed(2)}
              </p>
            )}

            {trade.isPending && (
              <p className="mt-2 text-sm text-slate-600">
                Submitting order...
              </p>
            )}

            {trade.isSuccess && lastAction && (
              <p className="mt-2 text-sm text-emerald-700">
                Order filled: {lastAction.toUpperCase()}{" "}
                {quantityNumber} {symbol.toUpperCase()}.
              </p>
            )}
          </div>
        </div>
      </div>

      {confirmOpen && pendingSide && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 backdrop-blur-sm">
          <div className="w-full max-w-md rounded-2xl bg-white p-6 shadow-xl">
            <h2 className="text-lg font-semibold mb-2">
              Confirm {pendingSide.toUpperCase()} Order
            </h2>

            <p className="text-sm text-slate-700">
              {pendingSide.toUpperCase()} {quantityNumber}{" "}
              {symbol.toUpperCase()} for{" "}
              {notional > 0
                ? `$${notional.toFixed(2)}`
                : "--"}
              ?
            </p>

            {isLargeTrade && (
              <div className="mt-3 rounded-lg bg-yellow-100 p-3 text-sm text-yellow-800">
                ⚠ This order uses more than 50% of your available
                capital. Consider diversification.
              </div>
            )}

            <div className="mt-6 flex gap-2">
              <button
                className="flex-1 rounded-xl border border-slate-300 px-4 py-2 font-medium"
                onClick={() => {
                  setConfirmOpen(false);
                  setPendingSide(null);
                }}
              >
                Cancel
              </button>

              <button
                className={`flex-1 rounded-xl px-4 py-2 font-medium text-white ${
                  pendingSide === "buy"
                    ? "bg-emerald-700 hover:bg-emerald-800"
                    : "bg-rose-700 hover:bg-rose-800"
                }`}
                onClick={() => {
                  setLastAction(pendingSide);
                  trade.mutate({ side: pendingSide });
                  setConfirmOpen(false);
                  setPendingSide(null);
                }}
              >
                Confirm
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}