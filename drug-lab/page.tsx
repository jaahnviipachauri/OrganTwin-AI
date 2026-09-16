"use client";

import { FormEvent, useEffect, useState } from "react";
import { Badge, PageHeader } from "@/components/ui";
import { DrugInfo, postJson } from "@/lib/api";
import { getJson } from "@/lib/api";
import { useLive } from "@/lib/useLive";

export default function DrugLabPage() {
  const { data } = useLive();
  const [drugs, setDrugs] = useState<DrugInfo[]>([]);
  const [organ, setOrgan] = useState("all");
  const [ageGroup, setAgeGroup] = useState("18-64");
  const [selectedDrugs, setSelectedDrugs] = useState<string[]>(["Paracetamol"]);
  const [dose, setDose] = useState(25);
  const [duration, setDuration] = useState(720);
  const [status, setStatus] = useState<string | null>(null);

  useEffect(() => {
    getJson<DrugInfo[]>("/api/drugs").then(setDrugs).catch(() => undefined);
  }, []);

  async function onSubmit(e: FormEvent) {
    e.preventDefault();
    if (selectedDrugs.length === 0) {
      setStatus("Please select at least one compound.");
      return;
    }
    setStatus("Perfusing…");
    try {
      await postJson("/api/drugs/apply", {
        organ,
        drug: selectedDrugs,
        dose_mg: dose,
        duration_h: duration / 60,
        age_group: ageGroup,
        experiment_name: `${selectedDrugs.join(" + ")} on ${organ} (${ageGroup})`,
      });
      setStatus("Exposure started. Watch live sensors and AI risk shift within a few ticks.");
    } catch (err) {
      setStatus(err instanceof Error ? err.message : "Failed to apply drug");
    }
  }

  return (
    <div>
      <PageHeader
        kicker="Assay designer"
        title="Drug testing simulator"
        subtitle="Select compound(s), dose, and duration. The twins remap oxygen, pH, viability, and organ-specific readouts in compressed experimental time."
      />
      <div className="grid lg:grid-cols-12 gap-6">
        <div className="lg:col-span-5">
          <form onSubmit={onSubmit} className="glass rounded-2xl p-6 space-y-5">
            <div className="pb-3 border-b border-white/5">
              <h3 className="font-medium text-white text-base">Perfusion Configuration</h3>
              <p className="text-xs text-slate-400 mt-1">Configure candidate compound dosing and target organ chip.</p>
            </div>
            <div>
              <label className="block text-sm text-slate-400 mb-1.5 font-medium">Target chip</label>
              <select className="w-full rounded-xl bg-slate-950/70 border border-cyan-500/20 p-2.5 text-sm text-white focus:outline-none focus:border-cyan-400" value={organ} onChange={(e) => setOrgan(e.target.value)}>
                <option value="all">All organs (Systemic)</option>
                <option value="liver">Liver-on-chip</option>
                <option value="heart">Heart-on-chip</option>
                <option value="kidney">Kidney-on-chip</option>
                <option value="lungs">Lungs-on-chip</option>
              </select>
            </div>
            <div>
              <label className="block text-sm text-slate-400 mb-1.5 font-medium">Patient age group</label>
              <select className="w-full rounded-xl bg-slate-950/70 border border-cyan-500/20 p-2.5 text-sm text-white focus:outline-none focus:border-cyan-400" value={ageGroup} onChange={(e) => setAgeGroup(e.target.value)}>
                <option value="0-1">0-1 (Infant)</option>
                <option value="1-3">1-3 (Toddler)</option>
                <option value="3-12">3-12 (Child)</option>
                <option value="12-18">12-18 (Adolescent)</option>
                <option value="18-64">18-64 (Adult)</option>
                <option value="65+">65+ (Senior)</option>
              </select>
            </div>
            <div>
              <label className="block text-sm text-slate-400 mb-1.5 font-medium">Test compound(s)</label>
              <select 
                multiple
                className="w-full h-40 rounded-xl bg-slate-950/70 border border-cyan-500/20 p-2.5 text-sm text-white focus:outline-none focus:border-cyan-400 custom-scrollbar"
                value={selectedDrugs} 
                onChange={(e) => {
                  const options = Array.from(e.target.selectedOptions);
                  setSelectedDrugs(options.map(o => o.value));
                }}
              >
                {drugs.map((d) => (
                  <option key={d.id} value={d.id} className="p-1.5 hover:bg-cyan-500/20 cursor-pointer rounded">
                    {d.display} ({d.class})
                  </option>
                ))}
              </select>
              <p className="text-[10px] text-slate-500 mt-1.5 px-1">Hold Cmd/Ctrl to select multiple</p>
            </div>
            <div className="space-y-1.5">
              <div className="flex justify-between text-sm">
                <span className="text-slate-400 font-medium">Dose</span>
                <span className="font-semibold text-cyan-300 tabular-nums px-2 py-0.5 rounded bg-cyan-400/10 border border-cyan-400/20 text-xs">
                  {dose} mg
                </span>
              </div>
              <input type="range" min={50} max={5000} step={50} value={dose} onChange={(e) => setDose(Number(e.target.value))} className="w-full accent-cyan-400 cursor-pointer" />
              <div className="flex justify-between text-[10px] text-slate-500">
                <span>50 mg</span>
                <span>5000 mg</span>
              </div>
            </div>
            <div className="space-y-1.5">
              <div className="flex justify-between text-sm">
                <span className="text-slate-400 font-medium">Exposure duration</span>
                <span className="font-semibold text-cyan-300 tabular-nums px-2 py-0.5 rounded bg-cyan-400/10 border border-cyan-400/20 text-xs">
                  {duration < 60 
                    ? `${duration < 1 ? duration * 60 + ' sec' : duration + ' min'}`
                    : `${(duration / 60).toFixed(1)} h`}
                </span>
              </div>
              <input type="range" min={0.5} max={1440} step={0.5} value={duration} onChange={(e) => setDuration(Number(e.target.value))} className="w-full accent-cyan-400 cursor-pointer" />
              <div className="flex justify-between text-[10px] text-slate-500">
                <span>30 sec</span>
                <span>24 h</span>
              </div>
            </div>
            <button className="w-full rounded-xl bg-cyan-400/20 border border-cyan-300/40 py-3 text-cyan-50 font-medium hover:bg-cyan-400/30 transition shadow-[0_0_20px_rgba(34,211,238,0.15)]">
              Start perfusion run
            </button>
            {status ? (
              <p className="text-xs text-cyan-200 p-3 rounded-xl bg-cyan-400/10 border border-cyan-400/20">
                {status}
              </p>
            ) : null}
          </form>
        </div>
        <div className="lg:col-span-7 space-y-5">
          <div className="glass rounded-2xl p-5 border border-white/5">
            <div className="flex items-center justify-between mb-3 pb-2 border-b border-white/5">
              <h3 className="text-sm uppercase tracking-[0.18em] text-slate-400 font-medium">Live Organ Effects</h3>
              <span className="text-xs text-cyan-400 font-mono">Active Perfusion</span>
            </div>
            <div className="grid sm:grid-cols-3 gap-3">
              {data?.organs.map((o) => (
                <div key={o.organ} className="rounded-xl bg-white/5 p-3 border border-white/5 flex flex-col justify-between">
                  <div className="flex items-center justify-between">
                    <span className="capitalize font-medium text-white text-sm">{o.organ}</span>
                    <Badge tone={o.health_score > 75 ? "ok" : o.health_score > 55 ? "amber" : "danger"}>
                      {o.health_score.toFixed(0)}
                    </Badge>
                  </div>
                  <div className="mt-2 text-xs text-slate-400 space-y-0.5">
                    <p className="truncate">Drug: <span className="text-slate-200">{o.drug}</span></p>
                    <p>Dose: <span className="text-slate-200">{o.dose_mg} mg</span></p>
                  </div>
                </div>
              ))}
            </div>
          </div>
          <div>
            <h3 className="text-sm uppercase tracking-[0.18em] text-slate-400 font-medium mb-3">Compound Library</h3>
            <div className="grid sm:grid-cols-2 gap-3">
              {drugs.map((d) => (
                <div key={String(d.id)} className="glass rounded-2xl p-4 border border-white/5 flex flex-col justify-between">
                  <div>
                    <div className="flex items-center justify-between gap-2">
                      <h4 className="font-medium text-white text-sm">{String(d.display)}</h4>
                      <Badge tone={d.class === "safe" ? "ok" : d.class === "moderate" ? "amber" : "danger"}>
                        {String(d.class)}
                      </Badge>
                    </div>
                    <p className="text-xs text-slate-400 mt-2 leading-relaxed">{String(d.note)}</p>
                  </div>
                  <div className="mt-3 pt-2 border-t border-white/5 text-[11px] text-slate-500 flex justify-between">
                    <span>Base toxicity</span>
                    <span className="text-slate-300 font-medium">{String(d.toxicity)}</span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
