import Link from "next/link";
import PetMascot from "../components/pet-mascot";
import MascotSpeech from "../components/mascot-speech";

export default function Landing() {
  return (
    <div className="space-y-10">
      <section className="grid items-center gap-6 lg:grid-cols-[1.05fr_1fr]">
        <div className="glass dot-grid landing-mascot-wrap p-4 md:p-6">
          <MascotSpeech text="Hey there, I'm really happy to see you!" />
          <PetMascot stage="baby" name="Sprout" level={1} />
        </div>
        <div className="space-y-5">
          <p className="stat-chip inline-flex">InvestiPet Platform</p>
          <h1 className="page-title">Learn Investing Through Play, Not Pressure</h1>
          <p className="page-subtitle max-w-2xl">
            InvestiPet combines financial education, paper trading, and pet progression into one guided experience. Build knowledge and discipline without risking real money.
          </p>
          <div className="flex flex-wrap gap-3">
            <Link className="btn-primary" href="/auth/register">Create Free Account</Link>
            <Link className="btn-secondary" href="/auth/login">Sign In</Link>
          </div>
          <p className="warning-banner max-w-2xl">Simulation environment only. No real-money trading, deposits, or withdrawals.</p>
          <div className="grid gap-3 sm:grid-cols-3">
            <div className="kpi">
              <p className="text-xs font-semibold uppercase tracking-wide text-slate-500">Education</p>
              <p className="mt-1 text-base font-semibold">Interactive lessons and guided quizzes</p>
            </div>
            <div className="kpi">
              <p className="text-xs font-semibold uppercase tracking-wide text-slate-500">Practice</p>
              <p className="mt-1 text-base font-semibold">Live quote paper trading experience</p>
            </div>
            <div className="kpi">
              <p className="text-xs font-semibold uppercase tracking-wide text-slate-500">Retention</p>
              <p className="mt-1 text-base font-semibold">Pet progression tied to healthy habits</p>
            </div>
          </div>
        </div>
      </section>

      <section className="grid gap-4 md:grid-cols-3">
        <div className="glass p-5">
          <h2 className="text-lg font-semibold">Built for Beginners</h2>
          <p className="mt-2 text-sm text-slate-600">No jargon-first onboarding. Learn concepts, then apply them in realistic simulations.</p>
        </div>
        <div className="glass p-5">
          <h2 className="text-lg font-semibold">Behavior-First Design</h2>
          <p className="mt-2 text-sm text-slate-600">Progress is rewarded for consistency, risk awareness, and portfolio discipline.</p>
        </div>
        <div className="glass p-5">
          <h2 className="text-lg font-semibold">Operationally Safe</h2>
          <p className="mt-2 text-sm text-slate-600">No real funds involved. Explore market decisions in a controlled environment.</p>
        </div>
      </section>

      <section className="glass flex flex-col items-start justify-between gap-4 p-5 md:flex-row md:items-center">
        <div>
          <h3 className="text-xl font-semibold">Start your first lesson and first simulated trade in under 5 minutes.</h3>
          <p className="mt-1 text-sm text-slate-600">Adopt your pet, answer one quiz, and execute your first paper order.</p>
        </div>
        <Link className="btn-primary" href="/auth/register">Get Started</Link>
      </section>
    </div>
  );
}
