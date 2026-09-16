"use client";

import { API } from "@/lib/api";
import { PageHeader } from "@/components/ui";
import { FileDown, FileText } from "lucide-react";

export default function ReportsPage() {
  return (
    <div>
      <PageHeader
        kicker="Evidence pack"
        title="Experiment and FDA-style reports"
        subtitle="Downloadable PDFs assemble live sensors, AI calls, and a simulated Module-4 safety narrative. For demo and education — not an official submission."
      />
      <div className="grid md:grid-cols-2 gap-6">
        <a
          href={`${API}/api/reports/experiment.pdf`}
          target="_blank"
          rel="noopener noreferrer"
          className="glass rounded-2xl p-6 hover:border-cyan-300/40 block transition group border border-white/5"
        >
          <div className="flex items-center justify-between">
            <span className="px-2.5 py-1 rounded-md bg-cyan-400/10 text-cyan-300 text-xs font-mono font-medium border border-cyan-400/20 flex items-center gap-1.5">
              <FileText className="h-3.5 w-3.5" />
              PDF Document
            </span>
            <span className="p-2 rounded-xl bg-white/5 text-slate-400 group-hover:text-cyan-300 group-hover:bg-cyan-400/10 transition">
              <FileDown className="h-4 w-4" />
            </span>
          </div>
          <h3 className="text-xl font-semibold text-white mt-4 group-hover:text-cyan-200 transition">
            Experiment report
          </h3>
          <p className="text-sm text-slate-400 mt-2 leading-relaxed">
            Drug tested, latest sensor vector, toxicity assessment, and AI recommendations formatted as an analytical laboratory record.
          </p>
          <div className="mt-4 pt-3 border-t border-white/5 flex items-center text-xs text-cyan-400/80 font-medium">
            <span>Download experiment run summary →</span>
          </div>
        </a>
        <a
          href={`${API}/api/reports/fda.pdf`}
          target="_blank"
          rel="noopener noreferrer"
          className="glass rounded-2xl p-6 hover:border-cyan-300/40 block transition group border border-white/5"
        >
          <div className="flex items-center justify-between">
            <span className="px-2.5 py-1 rounded-md bg-emerald-400/10 text-emerald-300 text-xs font-mono font-medium border border-emerald-400/20 flex items-center gap-1.5">
              <FileText className="h-3.5 w-3.5" />
              Regulatory Dossier
            </span>
            <span className="p-2 rounded-xl bg-white/5 text-slate-400 group-hover:text-emerald-300 group-hover:bg-emerald-400/10 transition">
              <FileDown className="h-4 w-4" />
            </span>
          </div>
          <h3 className="text-xl font-semibold text-white mt-4 group-hover:text-emerald-200 transition">
            Simulated FDA safety package
          </h3>
          <p className="text-sm text-slate-400 mt-2 leading-relaxed">
            Ranking, NOAEL-style interpretation, and a 3Rs statement replacing sentinel animal acute tox for investigational new drug filing.
          </p>
          <div className="mt-4 pt-3 border-t border-white/5 flex items-center text-xs text-emerald-400/80 font-medium">
            <span>Download IND safety dossier →</span>
          </div>
        </a>
      </div>
    </div>
  );
}
