"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

const links = [
  ["Dashboard", "/dashboard"],
  ["Trade", "/trade"],
  ["Portfolio", "/portfolio"],
  ["Learn", "/learn"],
  // ["Shop", "/shop"],
  ["Profile", "/profile"],
] as const;

export default function Nav() {
  const pathname = usePathname();

  return (
    <div className="glass mb-4 flex flex-wrap items-center justify-between gap-3 p-3">
      <Link href="/" className="rounded-xl bg-white px-3 py-2 text-sm font-semibold">
        InvestiPet
      </Link>
      <nav className="flex flex-wrap gap-2 text-sm">
        {links.map(([label, href]) => {
          const active = pathname === href;
          return (
            <Link
              className={
                active
                  ? "rounded-xl bg-emerald-700 px-3 py-2 font-medium text-white"
                  : "rounded-xl bg-white/75 px-3 py-2 font-medium text-slate-700 hover:bg-white"
              }
              key={href}
              href={href}
            >
              {label}
            </Link>
          );
        })}
      </nav>
    </div>
  );
}
