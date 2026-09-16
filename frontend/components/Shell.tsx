"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useState, useEffect } from "react";
import {
  Activity,
  Beaker,
  FileBarChart,
  GitCompare,
  LayoutDashboard,
  LineChart,
  Sparkles,
  Menu,
  X,
  Radio,
  Cpu,
} from "lucide-react";

const NAV = [
  { href: "/", label: "Command center", icon: LayoutDashboard },
  { href: "/organs", label: "Organ twins", icon: Activity },
  { href: "/drug-lab", label: "Drug simulator", icon: Beaker },
  { href: "/analytics", label: "Research analytics", icon: LineChart },
  { href: "/compare", label: "Multi-organ", icon: GitCompare },
  { href: "/insights", label: "AI insights", icon: Sparkles },
  { href: "/reports", label: "Reports", icon: FileBarChart },
];

export function Shell({ children }: { children: React.ReactNode }) {
  const path = usePathname();
  const [mobileOpen, setMobileOpen] = useState(false);

  // Close mobile drawer on route change
  useEffect(() => {
    setMobileOpen(false);
  }, [path]);

  // Lock body scroll when mobile menu is open
  useEffect(() => {
    if (mobileOpen) {
      document.body.style.overflow = "hidden";
    } else {
      document.body.style.overflow = "";
    }
    return () => {
      document.body.style.overflow = "";
    };
  }, [mobileOpen]);

  const currentNav = NAV.find((n) => n.href === path) ?? NAV[0];

  return (
    <div className="min-h-screen grid lg:grid-cols-[260px_1fr]">
      {/* Mobile Top Header */}
      <header className="lg:hidden sticky top-0 z-30 flex items-center justify-between border-b border-cyan-500/20 bg-slate-950/90 px-4 py-3 backdrop-blur-md">
        <Link href="/" className="flex items-center gap-2.5">
          <div className="h-9 w-9 rounded-xl bg-cyan-400/15 border border-cyan-400/40 grid place-items-center shadow-glow">
            <Activity className="h-5 w-5 text-cyan-300" />
          </div>
          <div>
            <span className="text-[10px] uppercase tracking-[0.2em] text-cyan-300/80 block">Biotech OS</span>
            <span className="text-sm font-semibold text-white">OrganTwin AI</span>
          </div>
        </Link>
        <div className="flex items-center gap-2">
          <div className="flex items-center gap-1.5 px-2 py-1 rounded-full bg-cyan-400/10 border border-cyan-400/20 text-[11px] text-cyan-300">
            <span className="h-2 w-2 rounded-full bg-emerald-400 animate-pulse" />
            <span className="hidden sm:inline">Telemetry</span> Live
          </div>
          <button
            type="button"
            onClick={() => setMobileOpen(!mobileOpen)}
            className="p-2 rounded-xl text-slate-300 hover:text-white hover:bg-white/10 transition"
            aria-label="Toggle Navigation Menu"
          >
            {mobileOpen ? <X className="h-5 w-5" /> : <Menu className="h-5 w-5" />}
          </button>
        </div>
      </header>

      {/* Mobile Drawer Backdrop */}
      {mobileOpen ? (
        <div
          className="lg:hidden fixed inset-0 z-40 bg-slate-950/80 backdrop-blur-sm transition-opacity"
          onClick={() => setMobileOpen(false)}
        />
      ) : null}

      {/* Mobile Navigation Drawer */}
      <div
        className={`lg:hidden fixed inset-y-0 left-0 z-50 w-72 max-w-[85vw] bg-slate-950 border-r border-cyan-500/20 p-5 flex flex-col justify-between transform transition-transform duration-300 ease-in-out ${
          mobileOpen ? "translate-x-0" : "-translate-x-full"
        }`}
      >
        <div>
          <div className="flex items-center justify-between mb-6">
            <div className="flex items-center gap-3">
              <div className="h-9 w-9 rounded-xl bg-cyan-400/15 border border-cyan-400/40 grid place-items-center shadow-glow">
                <Activity className="h-5 w-5 text-cyan-300" />
              </div>
              <div>
                <p className="text-[10px] uppercase tracking-[0.22em] text-cyan-300/80">Biotech OS</p>
                <h2 className="font-semibold text-slate-50 text-sm">OrganTwin AI</h2>
              </div>
            </div>
            <button
              onClick={() => setMobileOpen(false)}
              className="p-1.5 rounded-lg text-slate-400 hover:text-white hover:bg-white/10"
              aria-label="Close menu"
            >
              <X className="h-5 w-5" />
            </button>
          </div>
          <nav className="space-y-1">
            {NAV.map((item) => {
              const active = path === item.href;
              const Icon = item.icon;
              return (
                <Link
                  key={item.href}
                  href={item.href}
                  onClick={() => setMobileOpen(false)}
                  className={`flex items-center gap-3 rounded-xl px-3 py-2.5 text-sm transition font-medium ${
                    active
                      ? "bg-cyan-400/15 text-cyan-100 border border-cyan-400/30"
                      : "text-slate-400 hover:text-slate-100 hover:bg-white/5"
                  }`}
                >
                  <Icon className={`h-4 w-4 ${active ? "text-cyan-300" : "text-slate-400"}`} />
                  {item.label}
                </Link>
              );
            })}
          </nav>
        </div>
        <div className="pt-6 border-t border-cyan-500/15">
          <div className="flex items-center gap-2 text-xs text-cyan-300 mb-2">
            <Radio className="h-3.5 w-3.5 animate-pulse text-cyan-400" />
            <span>3 Organ Twins Active</span>
          </div>
          <p className="text-[11px] leading-relaxed text-slate-500">
            Human-relevant organ-on-chip twins. Built to cut sentinel animal testing in early tox.
          </p>
        </div>
      </div>

      {/* Desktop Sticky Sidebar */}
      <aside className="hidden lg:flex lg:flex-col lg:justify-between lg:sticky lg:top-0 lg:h-screen lg:overflow-y-auto border-r border-cyan-500/15 bg-slate-950/70 p-5">
        <div>
          <Link href="/" className="flex items-center gap-3 mb-8 group">
            <div className="h-10 w-10 rounded-xl bg-cyan-400/15 border border-cyan-400/40 grid place-items-center shadow-glow group-hover:border-cyan-300/70 transition">
              <Activity className="h-5 w-5 text-cyan-300" />
            </div>
            <div>
              <p className="text-[11px] uppercase tracking-[0.22em] text-cyan-300/80">Biotech OS</p>
              <h1 className="font-semibold text-slate-50 leading-tight">OrganTwin AI</h1>
            </div>
          </Link>
          <nav className="space-y-1">
            {NAV.map((item) => {
              const active = path === item.href;
              const Icon = item.icon;
              return (
                <Link
                  key={item.href}
                  href={item.href}
                  className={`flex items-center gap-3 rounded-xl px-3 py-2.5 text-sm transition font-medium ${
                    active
                      ? "bg-cyan-400/15 text-cyan-100 border border-cyan-400/30 shadow-[0_0_15px_rgba(34,211,238,0.1)]"
                      : "text-slate-400 hover:text-slate-100 hover:bg-white/5"
                  }`}
                >
                  <Icon className={`h-4 w-4 ${active ? "text-cyan-300" : "text-slate-400"}`} />
                  {item.label}
                </Link>
              );
            })}
          </nav>
        </div>
        <div className="pt-6 border-t border-cyan-500/15">
          <div className="flex items-center justify-between mb-2">
            <div className="flex items-center gap-2 text-xs text-cyan-300">
              <span className="h-2 w-2 rounded-full bg-emerald-400 animate-pulse" />
              <span>Real-time stream</span>
            </div>
            <span className="text-[10px] tracking-wider uppercase px-1.5 py-0.5 rounded bg-cyan-500/10 text-cyan-400 border border-cyan-500/20">
              v1.0
            </span>
          </div>
          <p className="text-[11px] leading-relaxed text-slate-500">
            Human-relevant organ-on-chip twins. Built to cut sentinel animal testing in early tox.
          </p>
        </div>
      </aside>

      {/* Main Content Area */}
      <main className="relative scanline min-w-0 flex-1 overflow-x-hidden">
        <div className="pointer-events-none absolute inset-0 bg-grid bg-[size:42px_42px] opacity-40" />

        {/* Desktop Top Bar */}
        <div className="hidden lg:flex items-center justify-between border-b border-cyan-500/10 px-8 py-3 bg-slate-950/40 backdrop-blur-sm sticky top-0 z-20">
          <div className="flex items-center gap-2 text-xs text-slate-400">
            <span className="text-slate-500">Workspace /</span>
            <span className="text-cyan-300 font-medium">{currentNav.label}</span>
          </div>
          <div className="flex items-center gap-3">
            <div className="flex items-center gap-2 px-3 py-1 rounded-full bg-cyan-400/10 border border-cyan-400/20 text-xs text-cyan-300">
              <Cpu className="h-3.5 w-3.5 text-cyan-300" />
              <span>Chip Telemetry Engine</span>
              <span className="h-1.5 w-1.5 rounded-full bg-emerald-400 animate-pulse" />
            </div>
          </div>
        </div>

        {/* Page Content Container */}
        <div className="relative p-4 sm:p-6 lg:p-8 max-w-7xl mx-auto w-full">
          {children}
        </div>
      </main>
    </div>
  );
}
