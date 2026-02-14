"use client";

import { FormEvent, useState } from "react";
import { useRouter } from "next/navigation";
import { api, setTokens } from "../../../lib/api";

export default function RegisterPage() {
  const router = useRouter();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [petName, setPetName] = useState("Buddy");
  const [error, setError] = useState<string | null>(null);

  async function submit(e: FormEvent) {
    e.preventDefault();
    setError(null);
    try {
      const data = await api("/auth/register", {
        method: "POST",
        body: JSON.stringify({ email, password, pet_name: petName }),
      });
      setTokens(data.access_token, data.refresh_token);
      router.push("/dashboard");
    } catch (err) {
      setError((err as Error).message);
    }
  }

  return (
    <div className="mx-auto max-w-md">
      <form className="glass space-y-4 p-6" onSubmit={submit}>
        <h1 className="page-title text-2xl">Create Your InvestiPet</h1>
        <p className="page-subtitle">You&apos;ll get starter cash and coins to begin safely.</p>
        <input className="input" value={email} onChange={(e) => setEmail(e.target.value)} placeholder="Email" />
        <input className="input" value={password} onChange={(e) => setPassword(e.target.value)} placeholder="Password" type="password" />
        <input className="input" value={petName} onChange={(e) => setPetName(e.target.value)} placeholder="Pet name" />
        {error && <p className="text-sm text-red-700">{error}</p>}
        <button className="btn-primary w-full" type="submit">Register</button>
      </form>
    </div>
  );
}
