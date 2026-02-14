"use client";

import { useQuery } from "@tanstack/react-query";
import Nav from "../../components/nav";
import { api, clearTokens } from "../../lib/api";

export default function ProfilePage() {
  const me = useQuery({ queryKey: ["me"], queryFn: () => api("/me") });

  return (
    <div className="space-y-4">
      <Nav />
      <div className="glass p-5">
        <h1 className="page-title">Profile</h1>
        <p className="page-subtitle">Manage account and review your current progression.</p>
      </div>
      {me.data && (
        <div className="glass p-4">
          <p><span className="font-semibold">Email:</span> {me.data.email}</p>
          <p><span className="font-semibold">Pet:</span> {me.data.pet.name} ({me.data.pet.species})</p>
          <p><span className="font-semibold">Level:</span> {me.data.pet.level} • {me.data.pet.stage}</p>
          <p><span className="font-semibold">XP:</span> {me.data.xp_total}</p>
        </div>
      )}
      <button className="btn-secondary" onClick={() => { clearTokens(); window.location.href = "/"; }}>
        Logout
      </button>
    </div>
  );
}
