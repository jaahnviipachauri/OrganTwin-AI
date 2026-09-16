"use client";

import { OrganHealthCard } from "@/components/OrganHealthCard";
import { Badge, MetricCard, PageHeader } from "@/components/ui";
import { useLive } from "@/lib/useLive";

export default function DashboardPage() {
  const { data, error } = useLive();

  if (error) {
    return (
      <div className="glass rounded-2xl p-8 text-rose-200">
        Cannot reach the OrganTwin API at {process.env.NEXT_PUBLIC_API_URL ?? "http://127.0.0.1:8000"}. Start the FastAPI backend first.
      </div>
    );
  }
  if (!data) {
    return <div className="glass rounded-2xl p-10 text-cyan-200 animate-pulse">Calibrating organ chips…</div>;
  }

  const liveOrgans = data.organs;

  return (
    <div>
      <PageHeader
        kicker="Live operations"
        title="Digital monitoring command center"
        subtitle="Panel health, perfusion sensors, and AI toxicity calls update every few seconds from the organ-on-chip twins."
      />
      <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4 mb-6">
        <MetricCard label="Organ health score" value={data.mean_health.toFixed(1)} hint="Mean across liver, heart, kidney, lungs" tone="ok" />
        <MetricCard label="Active experiments" value={data.active_experiments} hint="Chips currently under drug perfusion" />
        <MetricCard label="Toxicity alerts" value={data.toxicity_alerts} hint="Critical anomaly count in the live buffer" tone={data.toxicity_alerts ? "danger" : "ok"} />
        <MetricCard
          label="Drug exposure"
          value={liveOrgans.some((o) => o.drug !== "None") ? "ON" : "IDLE"}
          hint={liveOrgans.map((o) => `${o.organ}:${o.drug}`).join(" · ")}
          tone="amber"
        />
      </div>
      <div className="grid sm:grid-cols-2 xl:grid-cols-4 gap-4 sm:gap-6 mb-6">
        {liveOrgans.map((organ) => (
          <OrganHealthCard key={organ.organ} organ={organ} />
        ))}
      </div>
      <div className="grid lg:grid-cols-2 gap-6">
        <section className="glass rounded-2xl p-5 flex flex-col">
          <div className="flex items-center justify-between mb-4 pb-2 border-b border-white/5">
            <h3 className="text-sm uppercase tracking-[0.18em] text-slate-400">Live sensor feed</h3>
            <span className="text-xs text-cyan-400/80 font-mono">Telemetry</span>
          </div>
          <div className="space-y-2.5 max-h-[360px] overflow-y-auto pr-1">
            {liveOrgans.flatMap((organ) =>
              Object.values(organ.sensors).map((sensor) => (
                <div key={`${organ.organ}-${sensor.metric}`} className="flex items-center justify-between text-sm py-1.5 px-2 rounded-lg hover:bg-white/5 transition border-b border-white/5 last:border-0">
                  <span className="text-slate-400 capitalize flex items-center gap-2">
                    <span className="h-1.5 w-1.5 rounded-full bg-cyan-400/60" />
                    {organ.organ} · {sensor.metric.replace("_", " ")}
                  </span>
                  <span className="tabular-nums text-cyan-100 font-medium">
                    {sensor.value.toFixed(2)} <span className="text-slate-500 text-xs">{sensor.unit}</span>
                  </span>
                </div>
              ))
            )}
          </div>
        </section>
        <section className="glass rounded-2xl p-5 flex flex-col">
          <div className="flex items-center justify-between mb-4 pb-2 border-b border-white/5">
            <h3 className="text-sm uppercase tracking-[0.18em] text-slate-400">AI + anomaly stream</h3>
            <span className="text-xs text-cyan-400/80 font-mono">Inference</span>
          </div>
          <div className="space-y-3 max-h-[360px] overflow-y-auto pr-1">
            {Object.values(data.predictions).map((p) => (
              <div key={p.organ} className="rounded-xl bg-white/5 p-3.5 border border-white/5">
                <div className="flex items-center justify-between gap-2">
                  <span className="capitalize font-medium text-white flex items-center gap-2">
                    <span className="h-2 w-2 rounded-full bg-cyan-400" />
                    {p.organ}
                  </span>
                  <Badge tone={p.risk_level === "High" ? "danger" : p.risk_level === "Moderate" ? "amber" : "ok"}>
                    {p.label} · {Math.round(p.confidence * 100)}%
                  </Badge>
                </div>
                <div className="mt-2 flex items-center justify-between text-xs text-slate-400">
                  <span>Toxicity probability</span>
                  <span className="text-cyan-200 tabular-nums">{(p.toxicity_probability * 100).toFixed(1)}%</span>
                </div>
              </div>
            ))}
            {data.alerts.length === 0 ? (
              <div className="rounded-xl bg-white/5 p-3 text-center text-sm text-slate-500">
                No active perfusion anomalies detected.
              </div>
            ) : (
              data.alerts.map((alert, i) => (
                <div
                  key={alert.id ?? i}
                  className={`rounded-xl p-3 text-sm flex items-start gap-2 border ${
                    alert.severity === "critical"
                      ? "bg-rose-500/10 border-rose-500/30 text-rose-300"
                      : "bg-amber-500/10 border-amber-500/30 text-amber-200"
                  }`}
                >
                  <span className="shrink-0 mt-0.5 font-bold">!</span>
                  <span>{alert.message}</span>
                </div>
              ))
            )}
          </div>
        </section>
      </div>
    </div>
  );
}
