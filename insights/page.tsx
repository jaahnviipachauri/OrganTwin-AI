"use client";

import { useEffect, useState } from "react";
import { Badge, PageHeader } from "@/components/ui";
import { getJson } from "@/lib/api";
import { useLive } from "@/lib/useLive";

type Insights = {
  headline: string;
  insights: string[];
  failure_watch: { organ: string; eta_min: number | null; condition: string }[];
};

export default function InsightsPage() {
  const { data } = useLive();
  const [pack, setPack] = useState<Insights | null>(null);
  useEffect(() => {
    getJson<Insights>("/api/insights").then(setPack).catch(() => undefined);
  }, [data?.ticks]);

  return (
    <div>
      <PageHeader
        kicker="Model room"
        title="AI-generated research insights"
        subtitle="Random Forest class probabilities, Isolation Forest novelty flags, and failure-ahead estimates from viability/oxygen slope."
      />
      <p className="glass rounded-2xl p-5 mb-6 text-cyan-100">{pack?.headline ?? "Collecting traces…"}</p>
      <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-6 mb-8">
        {data &&
          Object.values(data.predictions).map((p) => (
            <div key={p.organ} className="glass rounded-2xl p-5 flex flex-col justify-between h-full border border-white/5">
              <div>
                <div className="flex justify-between items-center pb-2 border-b border-white/5">
                  <h3 className="capitalize font-medium text-white text-base">{p.organ}</h3>
                  <Badge tone={p.risk_level === "High" ? "danger" : p.risk_level === "Moderate" ? "amber" : "ok"}>
                    {p.risk_level} risk
                  </Badge>
                </div>
                <p className="mt-3 text-2xl font-semibold text-white tracking-tight">{p.label}</p>
                <div className="mt-2 space-y-1 text-xs text-slate-400">
                  <div className="flex justify-between">
                    <span>Model Confidence</span>
                    <span className="text-slate-200 tabular-nums font-medium">{(p.confidence * 100).toFixed(1)}%</span>
                  </div>
                  <div className="flex justify-between">
                    <span>Toxicity P</span>
                    <span className="text-cyan-300 tabular-nums font-medium">{(p.toxicity_probability * 100).toFixed(1)}%</span>
                  </div>
                </div>
                <div className="mt-4 pt-3 border-t border-white/5 space-y-1 text-xs text-slate-400">
                  <span className="text-[10px] uppercase tracking-wider text-slate-500 font-medium block mb-1.5">Class Probabilities</span>
                  {Object.entries(p.probabilities).map(([k, v]) => (
                    <div key={k} className="flex justify-between">
                      <span className="capitalize">{k}</span>
                      <span className="tabular-nums text-slate-300">{(v * 100).toFixed(1)}%</span>
                    </div>
                  ))}
                </div>
              </div>
              {p.is_anomaly ? (
                <div className="mt-4 pt-2 border-t border-white/5 text-amber-300 text-xs flex items-center gap-1.5">
                  <span className="h-1.5 w-1.5 rounded-full bg-amber-400 animate-ping inline-block" />
                  Anomaly detector: novel physiology vector
                </div>
              ) : null}
            </div>
          ))}
      </div>
      {pack?.failure_watch?.length ? (
        <section className="glass rounded-2xl p-5 mb-6 border border-rose-400/30">
          <h3 className="text-rose-200 mb-2">Predicted organ failure (pre-tox collapse)</h3>
          {pack.failure_watch.map((f) => (
            <p key={f.organ}>
              {f.organ}: {f.condition} · ETA {f.eta_min} min
            </p>
          ))}
        </section>
      ) : null}
      <ul className="space-y-2">
        {pack?.insights.map((line, i) => (
          <li key={i} className="glass rounded-xl px-4 py-3 text-sm text-slate-300">
            {line}
          </li>
        ))}
      </ul>
    </div>
  );
}
