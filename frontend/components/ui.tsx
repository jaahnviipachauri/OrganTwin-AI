"use client";

import { ReactNode } from "react";

export function PageHeader({
  kicker,
  title,
  subtitle,
  action,
}: {
  kicker: string;
  title: string;
  subtitle: string;
  action?: ReactNode;
}) {
  return (
    <header className="mb-8 flex flex-col sm:flex-row sm:items-end justify-between gap-4">
      <div>
        <p className="text-xs uppercase tracking-[0.28em] text-cyan-300/80">{kicker}</p>
        <h2 className="mt-2 text-2xl sm:text-3xl font-semibold text-white tracking-tight">{title}</h2>
        <p className="mt-2 max-w-3xl text-sm text-slate-400 leading-relaxed">{subtitle}</p>
      </div>
      {action ? <div className="shrink-0">{action}</div> : null}
    </header>
  );
}

export function MetricCard({
  label,
  value,
  hint,
  tone = "cyan",
}: {
  label: string;
  value: ReactNode;
  hint?: string;
  tone?: "cyan" | "ok" | "danger" | "amber";
}) {
  const map = {
    cyan: "text-cyan-300",
    ok: "text-emerald-300",
    danger: "text-rose-300",
    amber: "text-amber-300",
  };
  return (
    <div className="glass rounded-2xl p-5 flex flex-col justify-between h-full">
      <div>
        <p className="text-[11px] uppercase tracking-[0.2em] text-slate-400">{label}</p>
        <div className={`mt-2 text-2xl sm:text-3xl font-semibold tabular-nums ${map[tone]}`}>{value}</div>
      </div>
      {hint ? <p className="mt-3 text-xs text-slate-500 pt-2 border-t border-white/5">{hint}</p> : null}
    </div>
  );
}

export function Badge({ children, tone = "cyan" }: { children: ReactNode; tone?: string }) {
  const tones: Record<string, string> = {
    cyan: "border-cyan-400/30 bg-cyan-400/10 text-cyan-200",
    ok: "border-emerald-400/30 bg-emerald-400/10 text-emerald-200",
    danger: "border-rose-400/30 bg-rose-400/10 text-rose-200",
    amber: "border-amber-400/30 bg-amber-400/10 text-amber-200",
  };
  return (
    <span className={`inline-flex rounded-full border px-2.5 py-0.5 text-[11px] ${tones[tone] ?? tones.cyan}`}>
      {children}
    </span>
  );
}
