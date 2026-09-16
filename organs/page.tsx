"use client";

import { OrganHealthCard } from "@/components/OrganHealthCard";
import { PageHeader } from "@/components/ui";
import { useLive } from "@/lib/useLive";

export default function OrgansPage() {
  const { data, error } = useLive();
  if (error || !data) {
    return <div className="glass rounded-2xl p-8">{error ?? "Loading organ models…"}</div>;
  }
  return (
    <div>
      <PageHeader
        kicker="Simulation module"
        title="Liver, heart, and kidney chips"
        subtitle="Each twin streams organ-specific sensors. Apply a compound in Drug simulator to watch physiology diverge."
      />
      <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-6">
        {data.organs.map((organ) => (
          <div key={organ.organ} className="flex flex-col space-y-4">
            <div className="flex-1">
              <OrganHealthCard organ={organ} />
            </div>
            <div className="glass rounded-2xl p-4 space-y-2.5 border border-white/5">
              <div className="text-[11px] uppercase tracking-wider text-slate-500 font-medium pb-1 border-b border-white/5">
                Chip Sensor Readouts
              </div>
              {Object.values(organ.sensors).map((s) => (
                <div key={s.metric} className="flex justify-between text-sm py-0.5">
                  <span className="capitalize text-slate-400">{s.metric.replace("_", " ")}</span>
                  <span className="tabular-nums text-cyan-100 font-medium">
                    {s.value.toFixed(2)} <span className="text-slate-500 text-xs">{s.unit}</span>
                  </span>
                </div>
              ))}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
