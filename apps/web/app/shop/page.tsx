"use client";

import Nav from "../../components/nav";

export default function ShopPage() {
  return (
    <div className="space-y-4">
      <Nav />
      <div className="glass p-5">
        <h1 className="page-title">Pet Shop</h1>
        <p className="page-subtitle">Shop is currently disabled.</p>
      </div>
      <div className="glass p-5 text-sm text-slate-700">
        <p>Shop and equipment flows have been commented out for now.</p>
      </div>
    </div>
  );
}
