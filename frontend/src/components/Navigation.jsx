import {
  Archive,
  ChevronDown,
  FileSearch,
  LayoutDashboard,
  Menu,
  Network,
  ShieldCheck,
  X,
} from "lucide-react";
import React from "react";
import { useState } from "react";

const PRIMARY_ITEMS = [
  { id: "dashboard", label: "Overview", icon: LayoutDashboard },
  { id: "modules", label: "Investigations", icon: Network },
  { id: "vault", label: "Source vault", icon: Archive },
];

const TOOL_ITEMS = [
  ["analysis", "Analysis"],
  ["entities", "Entities"],
  ["relationships", "Relationships"],
  ["timeline", "Timeline"],
  ["admin", "Administration"],
];

export default function Navigation({ activeView, onNavigate, online }) {
  const [mobileOpen, setMobileOpen] = useState(false);
  const [toolsOpen, setToolsOpen] = useState(false);
  const navigate = (id) => {
    onNavigate(id);
    setMobileOpen(false);
    setToolsOpen(false);
  };

  return (
    <header className="relative z-50 border-b border-slate-800/90 bg-[#07101d]/95 backdrop-blur-xl">
      <div className="mx-auto flex h-16 max-w-[1600px] items-center gap-6 px-4 sm:px-6">
        <button
          onClick={() => navigate("dashboard")}
          className="group flex shrink-0 items-center gap-3 text-left"
          aria-label="Go to overview"
        >
          <span className="grid h-9 w-9 place-items-center rounded-xl border border-cyan-400/20 bg-cyan-400/10 text-cyan-300 transition group-hover:border-cyan-300/50">
            <ShieldCheck size={19} aria-hidden="true" />
          </span>
          <span>
            <span className="block text-sm font-semibold tracking-[0.18em] text-white">VERITAS</span>
            <span className="hidden text-[10px] uppercase tracking-[0.2em] text-slate-500 sm:block">
              Public evidence index
            </span>
          </span>
        </button>

        <nav className="hidden items-center gap-1 md:flex" aria-label="Primary navigation">
          {PRIMARY_ITEMS.map(({ id, label, icon: Icon }) => (
            <button
              key={id}
              onClick={() => navigate(id)}
              aria-current={activeView === id ? "page" : undefined}
              className={`flex items-center gap-2 rounded-lg px-3 py-2 text-sm font-medium transition ${
                activeView === id
                  ? "bg-slate-800 text-white shadow-sm"
                  : "text-slate-400 hover:bg-slate-900 hover:text-slate-100"
              }`}
            >
              <Icon size={15} aria-hidden="true" />
              {label}
            </button>
          ))}
          <div className="relative">
            <button
              onClick={() => setToolsOpen((open) => !open)}
              className="flex items-center gap-1.5 rounded-lg px-3 py-2 text-sm font-medium text-slate-400 hover:bg-slate-900 hover:text-slate-100"
              aria-expanded={toolsOpen}
            >
              Data tools <ChevronDown size={14} aria-hidden="true" />
            </button>
            {toolsOpen && (
              <div className="absolute left-0 top-11 w-48 rounded-xl border border-slate-700 bg-slate-900 p-1.5 shadow-2xl">
                {TOOL_ITEMS.map(([id, label]) => (
                  <button
                    key={id}
                    onClick={() => navigate(id)}
                    className="block w-full rounded-lg px-3 py-2 text-left text-sm text-slate-300 hover:bg-slate-800 hover:text-white"
                  >
                    {label}
                  </button>
                ))}
              </div>
            )}
          </div>
        </nav>

        <div className="ml-auto flex items-center gap-3">
          <div
            className="hidden items-center gap-2 rounded-full border border-slate-800 bg-slate-950/70 px-3 py-1.5 text-xs text-slate-400 sm:flex"
            title={online ? "Evidence API connected" : "Showing locally indexed data"}
          >
            <span className={`h-1.5 w-1.5 rounded-full ${online ? "bg-emerald-400" : "bg-amber-400"}`} />
            {online ? "Archive connected" : "Local index"}
          </div>
          <button
            onClick={() => navigate("vault")}
            className="hidden items-center gap-2 rounded-lg border border-slate-700 px-3 py-2 text-sm text-slate-300 transition hover:border-slate-600 hover:bg-slate-800 lg:flex"
          >
            <FileSearch size={15} aria-hidden="true" /> Search sources
            <kbd className="ml-1 rounded border border-slate-700 bg-slate-900 px-1.5 py-0.5 text-[10px] text-slate-500">
              /
            </kbd>
          </button>
          <button
            onClick={() => setMobileOpen((open) => !open)}
            className="rounded-lg border border-slate-800 p-2 text-slate-300 md:hidden"
            aria-label="Toggle navigation"
            aria-expanded={mobileOpen}
          >
            {mobileOpen ? <X size={19} /> : <Menu size={19} />}
          </button>
        </div>
      </div>

      {mobileOpen && (
        <nav className="border-t border-slate-800 bg-slate-950 p-3 md:hidden" aria-label="Mobile navigation">
          {[...PRIMARY_ITEMS, ...TOOL_ITEMS.map(([id, label]) => ({ id, label }))].map(
            ({ id, label, icon: Icon }) => (
              <button
                key={id}
                onClick={() => navigate(id)}
                className={`flex w-full items-center gap-2 rounded-lg px-3 py-2.5 text-left text-sm ${
                  activeView === id ? "bg-slate-800 text-white" : "text-slate-400"
                }`}
              >
                {Icon && <Icon size={15} aria-hidden="true" />}
                {label}
              </button>
            ),
          )}
        </nav>
      )}
    </header>
  );
}
