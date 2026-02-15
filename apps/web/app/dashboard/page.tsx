"use client";

import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import Nav from "../../components/nav";
import { api } from "../../lib/api";
import PetMascot from "../../components/pet-mascot";

export default function DashboardPage() {
  const me = useQuery({ queryKey: ["me"], queryFn: () => api("/me") });
  const rewards = useQuery({
    queryKey: ["rewards"],
    queryFn: () => api("/rewards/history"),
  });

  const [showAllRewards, setShowAllRewards] = useState(false);

  if (!me.data) return null;

  const level = me.data.pet.level;
  const totalXP = me.data.xp_total;

  // ===== XP LOGIC =====
  // Keep in sync with backend LEVEL_THRESHOLDS.
  const LEVEL_THRESHOLDS = [0, 100, 250, 450, 700, 1000, 1400, 1850];
  const levelIndex = Math.max(0, Math.min(level - 1, LEVEL_THRESHOLDS.length - 1));
  const currentThreshold = LEVEL_THRESHOLDS[levelIndex];
  const nextThreshold = LEVEL_THRESHOLDS[levelIndex + 1];
  const isMaxLevel = nextThreshold === undefined;
  const xpNeeded = isMaxLevel ? 0 : nextThreshold - currentThreshold;
  const currentLevelXP = isMaxLevel ? totalXP - currentThreshold : totalXP - currentThreshold;
  const xpProgressPercent = isMaxLevel
    ? 100
    : Math.min(Math.max((currentLevelXP / xpNeeded) * 100, 0), 100);

  // ===== HUNGER + HEALTH =====
  // Assumes backend returns:
  // me.data.pet.hunger (0-100)
  // me.data.financial_health (0-100)

  const hunger = me.data.pet.hunger ?? 75;
  const health = me.data.financial_health ?? 80;

  const rewardList = rewards.data || [];
  const visibleRewards = showAllRewards
    ? rewardList
    : rewardList.slice(0, 1);

  return (
    <div className="space-y-6 pb-10">
      <Nav />
      <p className="warning-banner">
        Simulated trading only. No real money is used.
      </p>

      {/* ================= MAIN PET STATUS PANEL ================= */}
      <section className="glass grid gap-6 p-6 md:grid-cols-[1fr_1.4fr]">
        {/* PET VISUAL */}
        <div className="flex items-center justify-center rounded-2xl bg-white/55 p-6">
          <PetMascot
            stage={me.data.pet.stage}
            name={me.data.pet.name}
            level={level}
          />
        </div>

        {/* PET STATUS */}
        <div className="flex flex-col justify-center space-y-6">
          {/* NAME + LEVEL (LARGER) */}
          <div>
            <h1 className="text-3xl font-bold">
              {me.data.pet.name}
            </h1>
            <p className="text-lg text-slate-600">
              Level {level} • {me.data.pet.stage}
            </p>
          </div>

          {/* XP BAR */}
          <div className="space-y-2">
            <div className="flex justify-between text-sm font-medium">
              <span>XP</span>
              <span>
                {isMaxLevel ? "MAX" : `${currentLevelXP} / ${xpNeeded}`}
              </span>
            </div>
            <div className="h-4 w-full rounded-full bg-slate-200 overflow-hidden">
              <div
                className="h-full bg-gradient-to-r from-indigo-500 to-purple-500 transition-all duration-500"
                style={{ width: `${xpProgressPercent}%` }}
              />
            </div>
          </div>

          {/* HUNGER BAR */}
          <div className="space-y-2">
            <div className="flex justify-between text-sm font-medium">
              <span>Hunger</span>
              <span>{hunger}%</span>
            </div>
            <div className="h-3 w-full rounded-full bg-slate-200 overflow-hidden">
              <div
                className="h-full bg-orange-400 transition-all duration-500"
                style={{ width: `${hunger}%` }}
              />
            </div>
            <p className="text-xs text-slate-500">
              Feed your pet by completing weekly lessons.
            </p>
          </div>

          {/* HEALTH BAR */}
          <div className="space-y-2">
            <div className="flex justify-between text-sm font-medium">
              <span>Health</span>
              <span>{health}%</span>
            </div>
            <div className="h-3 w-full rounded-full bg-slate-200 overflow-hidden">
              <div
                className="h-full bg-green-500 transition-all duration-500"
                style={{ width: `${health}%` }}
              />
            </div>
            <p className="text-xs text-slate-500">
              Reflects your overall financial health.
            </p>
          </div>
        </div>
      </section>

      {/* ================= KPI SECTION ================= */}
      <div className="grid gap-4 md:grid-cols-3">
        <div className="kpi hover:scale-[1.02] transition">
          <p className="text-sm text-slate-500">Cash Balance</p>
          <p className="text-2xl font-semibold">
            ${me.data.cash_balance.toFixed(2)}
          </p>
        </div>

        <div className="kpi hover:scale-[1.02] transition">
          <p className="text-sm text-slate-500">Coins</p>
          <p className="text-2xl font-semibold">
            {me.data.coins_balance}
          </p>
        </div>

        <div className="kpi hover:scale-[1.02] transition">
          <p className="text-sm text-slate-500">Total XP Earned</p>
          <p className="text-2xl font-semibold">
            {totalXP}
          </p>
        </div>
      </div>

      {/* ================= RECENT REWARDS ================= */}
      <section className="glass p-6">
        <div className="mb-4 flex items-center justify-between">
          <h2 className="text-lg font-semibold">
            Recent Rewards
          </h2>

          {rewardList.length > 1 && (
            <button
              onClick={() =>
                setShowAllRewards(!showAllRewards)
              }
              className="text-sm font-medium text-indigo-600 hover:underline"
            >
              {showAllRewards ? "Show Less" : "Show More"}
            </button>
          )}
        </div>

        {rewardList.length === 0 && (
          <p className="text-sm text-slate-500">
            No rewards yet.
          </p>
        )}

        <ul className="space-y-3">
          {visibleRewards.map((event: any) => (
            <li
              key={`${event.ref_id}-${event.created_at}`}
              className="flex items-center justify-between rounded-xl bg-white/80 p-4 shadow-sm"
            >
              <div>
                <p className="font-medium capitalize">
                  {event.source.replace("_", " ")}
                </p>
                <p className="text-xs text-slate-500">
                  {new Date(
                    event.created_at
                  ).toLocaleString()}
                </p>
              </div>

              <div className="text-sm font-medium text-right">
                <p className="text-green-600">
                  +{event.xp_delta} XP
                </p>
                <p className="text-yellow-600">
                  +{event.coin_delta} Coins
                </p>
              </div>
            </li>
          ))}
        </ul>
      </section>
    </div>
  );
}
