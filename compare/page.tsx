"use client";

import { useEffect, useState } from "react";
import { OrganHealthCard } from "@/components/OrganHealthCard";
import { Badge, PageHeader } from "@/components/ui";
import { getJson } from "@/lib/api";
import { useLive } from "@/lib/useLive";

type Rank = { drug: string; display: string; toxicity_score: number; safety_class: string; note: string };

export default function ComparePage() {
  const { data } = useLive();
  const [rank, setRank] = useState<Rank[]>([]);
  useEffect(() => {
    getJson<Rank[]>("/api/drugs/ranking").then(setRank).catch(() => undefined);
  }, [data?.ticks]);

  return (
    <div>
      <PageHeader
        kicker="Portfolio view"
        title="Multi-organ comparison"
        subtitle="Read liver, heart, kidney, and lungs in parallel — the same way a pharma safety panel would triage a lead series."
      />
      <div className="grid sm:grid-cols-2 xl:grid-cols-4 gap-6 mb-8">
        {data?.organs.map((o) => (
          <OrganHealthCard key={o.organ} organ={o} />
        ))}
      </div>
      <section className="glass rounded-2xl p-5">
        <h3 className="text-sm uppercase tracking-[0.18em] text-slate-400 mb-4">Drug ranking by toxicity score</h3>
        <div className="space-y-3">
          {rank.map((item, i) => (
            <div key={item.drug} className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 rounded-xl bg-white/5 p-3">
              <div>
                <p className="font-medium">
                  #{i + 1} {item.display}
                </p>
                <p className="text-xs text-slate-400">{item.note}</p>
              </div>
              <div className="flex items-center gap-3">
                <Badge tone={item.safety_class === "safe" ? "ok" : item.safety_class === "moderate" ? "amber" : "danger"}>
                  {item.safety_class}
                </Badge>
                <span className="tabular-nums text-cyan-100">{item.toxicity_score.toFixed(1)}</span>
              </div>
            </div>
          ))}
        </div>
      </section>
    </div>
  );
}
