import Link from "next/link";
import PetMascot from "../components/pet-mascot";

export default function Landing() {
  return (
    <div className="space-y-8">
      <section className="grid items-center gap-6 md:grid-cols-[1.05fr_1fr]">
        <div className="glass dot-grid p-4 md:p-6">
          <PetMascot stage="baby" name="Sprout" level={1} />
        </div>
        <div className="space-y-4">
          <p className="stat-chip inline-flex">Pet-First Investing Experience</p>
          <h1 className="page-title">Your Pet Is The Core Of The Journey</h1>
          <p className="page-subtitle max-w-xl">
            InvestiPet is not a regular trading dashboard. Every lesson, trade, and healthy habit directly animates and evolves your companion.
          </p>
          <div className="flex flex-wrap gap-3">
            <Link className="btn-primary" href="/auth/register">Start Free</Link>
            <Link className="btn-secondary" href="/auth/login">I Already Have an Account</Link>
          </div>
          <p className="warning-banner max-w-lg">Simulated trading only. No real money is used or at risk.</p>
          <div className="space-y-2">
            <p className="text-sm font-medium text-slate-500">Pet Growth Loop</p>
            <div className="kpi"><p className="text-sm text-slate-500">1. Learn</p><p className="text-lg font-semibold">Finish a lesson quiz</p></div>
            <div className="kpi"><p className="text-sm text-slate-500">2. Trade</p><p className="text-lg font-semibold">Simulate a diversified buy</p></div>
            <div className="kpi"><p className="text-sm text-slate-500">3. Progress</p><p className="text-lg font-semibold">Spend coins in the pet shop</p></div>
          </div>
        </div>
      </section>
    </div>
  );
}
