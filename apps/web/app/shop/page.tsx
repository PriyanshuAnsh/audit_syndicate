"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import Nav from "../../components/nav";
import { api } from "../../lib/api";

export default function ShopPage() {
  const qc = useQueryClient();
  const items = useQuery({ queryKey: ["shop"], queryFn: () => api("/shop/items") });
  const inventory = useQuery({ queryKey: ["inventory"], queryFn: () => api("/inventory") });

  const purchase = useMutation({
    mutationFn: (itemId: number) => api("/shop/purchase", { method: "POST", body: JSON.stringify({ item_id: itemId }) }),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["inventory"] });
      qc.invalidateQueries({ queryKey: ["me"] });
    },
  });

  const equip = useMutation({
    mutationFn: (itemId: number) => api("/pet/equip", { method: "POST", body: JSON.stringify({ item_id: itemId }) }),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["inventory"] }),
  });

  const owned = new Set((inventory.data || []).map((i: any) => i.item_id));

  return (
    <div className="space-y-4">
      <Nav />
      <div className="glass p-5">
        <h1 className="page-title">Pet Shop</h1>
        <p className="page-subtitle">Spend coins on cosmetics, toys, and habitats.</p>
      </div>
      <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
        {(items.data || []).map((item: any) => (
          <div key={item.id} className="glass p-4">
            <div className="mb-2 flex items-center justify-between">
              <p className="font-semibold">{item.name}</p>
              <span className="stat-chip">{item.type}</span>
            </div>
            <p className="text-sm text-slate-600">Slot: {item.slot}</p>
            <p className="mb-3 text-sm text-slate-600">Cost: {item.coin_cost} coins</p>
            {!owned.has(item.id) ? (
              <button className="btn-primary" onClick={() => purchase.mutate(item.id)}>Buy</button>
            ) : (
              <button className="btn-secondary" onClick={() => equip.mutate(item.id)}>Equip</button>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}
