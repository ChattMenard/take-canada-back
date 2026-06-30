import {
  Banknote,
  Building2,
  ChevronRight,
  FileWarning,
  Network,
  PackageSearch,
  Users,
} from "lucide-react";
import { useState } from "react";
import PlatformExplorer from "./PlatformExplorer/index.jsx";

const MODULES = [
  { id: "platform", number: "01", label: "Platform explorer", icon: Network, status: "Active" },
  { id: "contracts", number: "02", label: "Contract analyzer", icon: PackageSearch, status: "Staged" },
  { id: "revolving", number: "03", label: "Revolving door", icon: Users, status: "Staged" },
  { id: "money", number: "04", label: "Political money", icon: Banknote, status: "Staged" },
  { id: "family", number: "05", label: "Family networks", icon: Building2, status: "Staged" },
  { id: "lobbying", number: "06", label: "Lobbying intelligence", icon: FileWarning, status: "Staged" },
];

export default function Modules({ onOpenSource }) {
  const [active, setActive] = useState("platform");
  const selected = MODULES.find(({ id }) => id === active);

  return (
    <div className="min-h-full bg-[#07101d] lg:grid lg:grid-cols-[220px_1fr]">
      <aside className="border-b border-slate-800 bg-slate-950/45 p-3 lg:border-b-0 lg:border-r lg:p-4">
        <div className="hidden px-3 pb-4 pt-2 text-[10px] font-semibold uppercase tracking-[0.18em] text-slate-600 lg:block">
          Investigation desk
        </div>
        <nav className="flex gap-2 overflow-x-auto lg:block lg:space-y-1" aria-label="Investigation modules">
          {MODULES.map(({ id, number, label, icon: Icon, status }) => (
            <button
              key={id}
              onClick={() => setActive(id)}
              className={`flex shrink-0 items-center gap-3 rounded-xl px-3 py-2.5 text-left transition lg:w-full ${
                active === id ? "bg-slate-800 text-white" : "text-slate-500 hover:bg-slate-900 hover:text-slate-300"
              }`}
            >
              <Icon size={15} className={active === id ? "text-cyan-300" : ""} />
              <span className="min-w-0">
                <span className="block truncate text-xs font-medium">{label}</span>
                <span className="hidden text-[9px] uppercase tracking-wider text-slate-600 lg:block">
                  {number} · {status}
                </span>
              </span>
              <ChevronRight size={13} className="ml-auto hidden lg:block" />
            </button>
          ))}
        </nav>
      </aside>

      <main className="min-w-0">
        {active === "platform" ? (
          <PlatformExplorer onOpenSource={onOpenSource} />
        ) : (
          <div className="grid min-h-[calc(100vh-64px)] place-items-center p-6">
            <div className="max-w-lg rounded-2xl border border-slate-800 bg-slate-900/60 p-8 text-center">
              <selected.icon className="mx-auto text-slate-600" size={32} />
              <div className="mt-5 font-mono text-xs text-cyan-300">INVESTIGATION {selected.number}</div>
              <h1 className="mt-2 text-2xl font-semibold text-white">{selected.label}</h1>
              <p className="mt-3 text-sm leading-6 text-slate-500">
                The dataset is staged in the archive. This module is queued for the next implementation phase;
                source records remain available in the vault.
              </p>
              <button
                onClick={() => setActive("platform")}
                className="mt-6 rounded-lg border border-slate-700 px-4 py-2 text-sm text-slate-300 hover:bg-slate-800"
              >
                Return to active module
              </button>
            </div>
          </div>
        )}
      </main>
    </div>
  );
}
