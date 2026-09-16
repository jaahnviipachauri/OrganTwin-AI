"use client";

import { useEffect, useState } from "react";
import { CartesianGrid, Legend, Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { PageHeader } from "@/components/ui";
import { getJson } from "@/lib/api";

type TrendMap = Record<string, Array<Record<string, number>>>;

export default function AnalyticsPage() {
  const [trends, setTrends] = useState<TrendMap>({});

  useEffect(() => {
    const load = () => getJson<TrendMap>("/api/analytics/trends").then(setTrends).catch(() => undefined);
    load();
    const id = setInterval(load, 3000);
    return () => clearInterval(id);
  }, []);

  const liver = trends.liver ?? [];
  const heart = trends.heart ?? [];
  const kidney = trends.kidney ?? [];
  const panel = liver.map((p, i) => ({
    tick: p.tick ?? i,
    liver: p.health,
    heart: heart[i]?.health,
    kidney: kidney[i]?.health,
  }));

  return (
    <div>
      <PageHeader
        kicker="Translational analytics"
        title="Toxicity trends and drug-response curves"
        subtitle="Compressed perfusion time on the X axis. Overlay oxygen, viability/contractility, and a composite health proxy."
      />
      <div className="grid gap-5">
        <ChartCard title="Organ performance timeline (health proxy)">
          <ResponsiveContainer width="100%" height={280}>
            <LineChart data={panel}>
              <CartesianGrid stroke="rgba(148,163,184,0.15)" />
              <XAxis dataKey="tick" stroke="#94a3b8" />
              <YAxis stroke="#94a3b8" domain={[0, 100]} />
              <Tooltip contentStyle={{ background: "#0b1220", border: "1px solid #164e63" }} />
              <Legend />
              <Line dataKey="liver" name="Liver" stroke="#22d3ee" dot={false} strokeWidth={2} />
              <Line dataKey="heart" name="Heart" stroke="#fb7185" dot={false} strokeWidth={2} />
              <Line dataKey="kidney" name="Kidney" stroke="#38bdf8" dot={false} strokeWidth={2} />
            </LineChart>
          </ResponsiveContainer>
        </ChartCard>
        <ChartCard title="Liver sensor history">
          <ResponsiveContainer width="100%" height={260}>
            <LineChart data={liver}>
              <CartesianGrid stroke="rgba(148,163,184,0.15)" />
              <XAxis dataKey="tick" stroke="#94a3b8" />
              <YAxis stroke="#94a3b8" />
              <Tooltip contentStyle={{ background: "#0b1220", border: "1px solid #164e63" }} />
              <Legend />
              <Line dataKey="oxygen" stroke="#22d3ee" dot={false} />
              <Line dataKey="viability" stroke="#34d399" dot={false} />
              <Line dataKey="lactate" stroke="#fbbf24" dot={false} />
              <Line dataKey="ph" stroke="#c4b5fd" dot={false} />
            </LineChart>
          </ResponsiveContainer>
        </ChartCard>
        <div className="grid lg:grid-cols-2 gap-5">
          <ChartCard title="Heart response curve">
            <ResponsiveContainer width="100%" height={240}>
              <LineChart data={heart}>
                <CartesianGrid stroke="rgba(148,163,184,0.15)" />
                <XAxis dataKey="tick" stroke="#94a3b8" />
                <YAxis stroke="#94a3b8" />
                <Tooltip contentStyle={{ background: "#0b1220", border: "1px solid #164e63" }} />
                <Legend />
                <Line dataKey="heartbeat" stroke="#fb7185" dot={false} />
                <Line dataKey="contractility" stroke="#22d3ee" dot={false} />
                <Line dataKey="oxygen" stroke="#38bdf8" dot={false} />
              </LineChart>
            </ResponsiveContainer>
          </ChartCard>
          <ChartCard title="Kidney filtration vs metabolites">
            <ResponsiveContainer width="100%" height={240}>
              <LineChart data={kidney}>
                <CartesianGrid stroke="rgba(148,163,184,0.15)" />
                <XAxis dataKey="tick" stroke="#94a3b8" />
                <YAxis stroke="#94a3b8" />
                <Tooltip contentStyle={{ background: "#0b1220", border: "1px solid #164e63" }} />
                <Legend />
                <Line dataKey="filtration" stroke="#38bdf8" dot={false} />
                <Line dataKey="toxic_metabolites" stroke="#f97316" dot={false} />
                <Line dataKey="viability" stroke="#34d399" dot={false} />
              </LineChart>
            </ResponsiveContainer>
          </ChartCard>
        </div>
      </div>
    </div>
  );
}

function ChartCard({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <section className="glass rounded-2xl p-5 min-w-0 overflow-hidden">
      <h3 className="mb-4 text-sm uppercase tracking-[0.18em] text-slate-400 font-medium">{title}</h3>
      <div className="w-full min-w-0">
        {children}
      </div>
    </section>
  );
}
