"use client";

import { OrganSnapshot } from "@/lib/api";
import { Badge } from "./ui";

const COLORS: Record<string, string> = {
  liver: "#22d3ee",
  heart: "#fb7185",
  kidney: "#38bdf8",
  lungs: "#a78bfa",
};

export function OrganHealthCard({ organ }: { organ: OrganSnapshot }) {
  const color = COLORS[organ.organ] ?? "#22d3ee";
  const pulse = Math.max(0.9, organ.health_score / 100);
  return (
    <div className="glass rounded-2xl p-5 overflow-hidden flex flex-col justify-between h-full">
      <div>
        <div className="flex items-start justify-between gap-3">
          <div>
            <p className="text-[11px] uppercase tracking-[0.2em] text-slate-400">{organ.organ}-on-chip</p>
            <h3 className="text-xl font-semibold capitalize text-white">{organ.organ} twin</h3>
          </div>
          <Badge tone={organ.health_score > 75 ? "ok" : organ.health_score > 55 ? "amber" : "danger"}>
            {organ.condition}
          </Badge>
        </div>
        <div className="relative mx-auto my-6 h-36 w-36">
          <div
            className="pulse-ring absolute inset-0 rounded-full"
            style={{ border: `2px solid ${color}`, transform: `scale(${pulse})` }}
          />
          <div
            className="absolute inset-3 rounded-full grid place-items-center"
            style={{
              background: `radial-gradient(circle at 40% 35%, ${color}55, transparent 55%), rgba(2,8,23,0.9)`,
              boxShadow: `0 0 30px ${color}33`,
            }}
          >
            <div className="text-center">
              <div className="text-3xl font-semibold tabular-nums" style={{ color }}>
                {organ.health_score.toFixed(0)}
              </div>
              <div className="text-[10px] uppercase tracking-widest text-slate-400">health</div>
            </div>
          </div>
        </div>
        <dl className="grid grid-cols-3 gap-2 text-center text-xs">
          <div className="rounded-xl bg-white/5 p-2 border border-white/5">
            <dt className="text-slate-500">Stress</dt>
            <dd className="font-semibold text-amber-200 mt-0.5">{organ.stress_level.toFixed(0)}%</dd>
          </div>
          <div className="rounded-xl bg-white/5 p-2 border border-white/5">
            <dt className="text-slate-500">Survival</dt>
            <dd className="font-semibold text-emerald-200 mt-0.5">{organ.survival_rate.toFixed(0)}%</dd>
          </div>
          <div className="rounded-xl bg-white/5 p-2 border border-white/5">
            <dt className="text-slate-500">Damage</dt>
            <dd className="font-semibold text-rose-200 mt-0.5">{organ.damage_percent.toFixed(0)}%</dd>
          </div>
        </dl>
      </div>
      <div className="mt-4 pt-3 border-t border-white/5 text-xs text-slate-400 flex flex-wrap items-center justify-between gap-1">
        <span>
          <span className="text-slate-500">Exposure:</span> {organ.drug} ({organ.dose_mg} mg)
        </span>
        <span className="tabular-nums text-slate-400">t={organ.exposure_elapsed_h.toFixed(1)}h</span>
        {organ.failure_eta_min ? (
          <div className="w-full mt-1 text-rose-300 font-medium flex items-center gap-1.5">
            <span className="h-1.5 w-1.5 rounded-full bg-rose-400 animate-ping inline-block" />
            Failure watch: ~{organ.failure_eta_min} min
          </div>
        ) : null}
      </div>
    </div>
  );
}
