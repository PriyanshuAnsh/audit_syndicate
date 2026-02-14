import Link from "next/link";

export default function OnboardingPage() {
  return (
    <div className="mx-auto max-w-2xl space-y-4">
      <div className="glass p-6">
        <h1 className="page-title text-3xl">You&apos;re Ready</h1>
        <p className="page-subtitle mt-2">Your pet is created, and your starter capital is waiting on the dashboard.</p>
        <div className="mt-4">
          <Link className="btn-primary" href="/dashboard">Go to Dashboard</Link>
        </div>
      </div>
    </div>
  );
}
