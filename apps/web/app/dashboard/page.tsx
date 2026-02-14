"use client";

import { useQuery } from "@tanstack/react-query";
import Nav from "../../components/nav";
import { api } from "../../lib/api";
import PetMascot from "../../components/pet-mascot";

export default function DashboardPage() {
  const me = useQuery({ queryKey: ["me"], queryFn: () => api("/me") });
  const rewards = useQuery({ queryKey: ["rewards"], queryFn: () => api("/rewards/history") });

  return (
    <div className="space-y-4">
      <Nav />
      <p className="warning-banner">Simulated trading only. No real money is used.</p>
      <section className="glass grid gap-4 p-5 md:grid-cols-[1fr_1.1fr]">
        {me.data && (
          <div className="rounded-2xl bg-white/55">
            <PetMascot stage={me.data.pet.stage} name={me.data.pet.name} level={me.data.pet.level} />
          </div>
        )}
        <div>
          <h1 className="page-title">Dashboard</h1>
          <p className="page-subtitle">Your pet status now leads the experience. Finance actions are the fuel for growth.</p>
          {me.data && <p className="mt-3 stat-chip inline-flex">{me.data.pet.name} • Level {me.data.pet.level} • {me.data.pet.stage}</p>}
        </div>
      </section>

      {me.data && (
        <div className="grid gap-3 md:grid-cols-3">
          <div className="kpi"><p className="text-sm text-slate-500">Cash Balance</p><p className="text-2xl font-semibold">${me.data.cash_balance.toFixed(2)}</p></div>
          <div className="kpi"><p className="text-sm text-slate-500">Coins</p><p className="text-2xl font-semibold">{me.data.coins_balance}</p></div>
          <div className="kpi"><p className="text-sm text-slate-500">Total XP</p><p className="text-2xl font-semibold">{me.data.xp_total}</p></div>
        </div>
      )}

      <section className="glass p-4">
        <h2 className="mb-3 text-lg font-semibold">Recent Rewards</h2>
        <ul className="space-y-2">
          {(rewards.data || []).slice(0, 6).map((event: any) => (
            <li className="flex items-center justify-between rounded-xl bg-white/80 p-3" key={`${event.ref_id}-${event.created_at}`}>
              <span className="font-medium capitalize">{event.source.replace("_", " ")}</span>
              <span className="text-sm text-slate-600">+{event.xp_delta} XP • +{event.coin_delta} coins</span>
            </li>
          ))}
        </ul>
      </section>
    </div>
  );
}
