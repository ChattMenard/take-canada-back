import { motion } from "framer-motion";
import { lazy, Suspense } from "react";
import {
  ArrowRight,
  CheckCircle2,
  Clock3,
  Database,
  FileCheck2,
  Fingerprint,
  Network,
} from "lucide-react";
import HeroTimeline from "./HeroTimeline.jsx";
import LobbyingHeatmap from "./LobbyingHeatmap.jsx";
import MoneyFlowSankey from "./MoneyFlowSankey.jsx";

const VaccineWasteChart = lazy(() => import("./VaccineWasteChart.jsx"));

const MODULES = [
  ["01", "Platform explorer", "Funding, patents and pre-pandemic agreements", "24 events"],
  ["02", "Contract analyzer", "Procurement terms, cost and disposition", "In review"],
  ["03", "Revolving door", "Personnel movement and conflict indicators", "1 profile"],
  ["04", "Political money", "Contributions connected to public decisions", "Data indexed"],
  ["05", "Family networks", "Corporate and familial relationship mapping", "In progress"],
  ["06", "Lobbying intelligence", "Contacts, subjects and decision proximity", "9 contacts"],
];

export default function Dashboard({ stats, online, merkleRoot, onNavigate, onOpenSource }) {
  const metrics = [
    { label: "Preserved records", value: stats?.evidence_count ?? "53+", icon: Database },
    { label: "Timeline events", value: 24, icon: Clock3 },
    { label: "Indexed entities", value: stats?.entity_count ?? 35, icon: Network },
    { label: "Integrity manifest", value: "Indexed", icon: FileCheck2 },
  ];

  return (
    <div className="min-h-full bg-[#07101d]">
      <section className="relative overflow-hidden border-b border-slate-800">
        <div className="evidence-grid absolute inset-0 opacity-35" />
        <div className="absolute left-1/3 top-0 h-80 w-80 rounded-full bg-cyan-400/[0.07] blur-3xl" />
        <div className="relative mx-auto max-w-[1600px] px-4 pb-10 pt-12 sm:px-6 lg:pb-14 lg:pt-16">
          <div className="grid items-end gap-10 lg:grid-cols-[1fr_420px]">
            <div>
              <div className="mb-5 flex items-center gap-3">
                <span className="h-px w-8 bg-cyan-300" />
                <span className="text-xs font-semibold uppercase tracking-[0.2em] text-cyan-300">
                  Executive evidence brief
                </span>
              </div>
              <motion.h1
                initial={{ opacity: 0, y: 12 }}
                animate={{ opacity: 1, y: 0 }}
                className="max-w-4xl text-4xl font-semibold tracking-[-0.04em] text-white sm:text-5xl lg:text-6xl"
              >
                Follow the record.
                <span className="block text-slate-500">Inspect every connection.</span>
              </motion.h1>
              <p className="mt-6 max-w-2xl text-base leading-7 text-slate-400">
                A source-first workspace for examining public records, financial flows, lobbying contacts and
                institutional relationships. Claims remain connected to the material used to support them.
              </p>
              <div className="mt-8 flex flex-wrap gap-3">
                <button
                  onClick={() => onNavigate("modules")}
                  className="inline-flex items-center gap-2 rounded-lg bg-cyan-300 px-4 py-2.5 text-sm font-semibold text-slate-950 transition hover:bg-cyan-200"
                >
                  Open investigations <ArrowRight size={16} aria-hidden="true" />
                </button>
                <button
                  onClick={() => onNavigate("vault")}
                  className="inline-flex items-center gap-2 rounded-lg border border-slate-700 bg-slate-900/70 px-4 py-2.5 text-sm font-semibold text-slate-200 transition hover:border-slate-600 hover:bg-slate-800"
                >
                  Search source vault
                </button>
              </div>
            </div>

            <div className="rounded-2xl border border-slate-700/80 bg-slate-900/75 p-5 shadow-2xl backdrop-blur">
              <div className="flex items-center justify-between gap-4">
                <div className="flex items-center gap-2 text-sm font-medium text-white">
                  <Fingerprint size={17} className="text-emerald-300" aria-hidden="true" />
                  Archive integrity
                </div>
                <span className="flex items-center gap-1.5 text-xs text-emerald-300">
                  <CheckCircle2 size={13} aria-hidden="true" /> Manifest present
                </span>
              </div>
              <div className="mt-5 rounded-xl border border-slate-800 bg-slate-950 p-4">
                <div className="text-[10px] font-semibold uppercase tracking-[0.18em] text-slate-500">Merkle root</div>
                <code className="mt-2 block break-all font-mono text-xs leading-5 text-slate-300">{merkleRoot}</code>
              </div>
              <div className="mt-4 flex items-center justify-between text-xs text-slate-500">
                <span>SHA-256 · Ed25519</span>
                <span>{online ? "API connected" : "Local manifest"}</span>
              </div>
            </div>
          </div>

          <div className="mt-12 grid grid-cols-2 overflow-hidden rounded-2xl border border-slate-800 bg-slate-900/50 lg:grid-cols-4">
            {metrics.map(({ label, value, icon: Icon }, index) => (
              <div
                key={label}
                className={`p-4 sm:p-5 ${index % 2 ? "border-l border-slate-800" : ""} ${
                  index > 1 ? "border-t border-slate-800 lg:border-t-0 lg:border-l" : ""
                }`}
              >
                <Icon size={15} className="mb-5 text-slate-500" aria-hidden="true" />
                <div className="font-mono text-2xl font-semibold text-white">{value}</div>
                <div className="mt-1 text-xs text-slate-500">{label}</div>
              </div>
            ))}
          </div>
        </div>
      </section>

      <section className="mx-auto max-w-[1600px] px-4 py-12 sm:px-6 lg:py-16">
        <div className="mb-7 flex flex-col justify-between gap-3 sm:flex-row sm:items-end">
          <div>
            <div className="text-xs font-semibold uppercase tracking-[0.18em] text-cyan-300">Evidence signals</div>
            <h2 className="mt-2 text-2xl font-semibold tracking-tight text-white">The archive at a glance</h2>
          </div>
          <p className="max-w-xl text-sm leading-6 text-slate-500">
            Select any event, flow or contact to trace it back to the source vault.
          </p>
        </div>

        <div className="grid gap-5 xl:grid-cols-2">
          <HeroTimeline onOpenSource={onOpenSource} />
          <Suspense fallback={<ChartPlaceholder />}>
            <VaccineWasteChart />
          </Suspense>
          <MoneyFlowSankey onOpenSource={onOpenSource} />
          <LobbyingHeatmap onOpenSource={onOpenSource} />
        </div>
      </section>

      <section className="border-t border-slate-800 bg-slate-950/35">
        <div className="mx-auto max-w-[1600px] px-4 py-12 sm:px-6 lg:py-16">
          <div className="mb-7 flex items-end justify-between gap-4">
            <div>
              <div className="text-xs font-semibold uppercase tracking-[0.18em] text-violet-300">Deep dive</div>
              <h2 className="mt-2 text-2xl font-semibold text-white">Investigation modules</h2>
            </div>
            <button
              onClick={() => onNavigate("modules")}
              className="hidden items-center gap-2 text-sm font-medium text-slate-400 hover:text-white sm:flex"
            >
              View all <ArrowRight size={15} aria-hidden="true" />
            </button>
          </div>
          <div className="grid gap-px overflow-hidden rounded-2xl border border-slate-800 bg-slate-800 md:grid-cols-2 xl:grid-cols-3">
            {MODULES.map(([number, title, description, status]) => (
              <button
                key={number}
                onClick={() => onNavigate("modules")}
                className="group bg-[#091321] p-5 text-left transition hover:bg-slate-900"
              >
                <div className="flex items-center justify-between">
                  <span className="font-mono text-xs text-slate-600">{number}</span>
                  <span className="rounded-full border border-slate-800 px-2 py-0.5 text-[10px] text-slate-500">
                    {status}
                  </span>
                </div>
                <h3 className="mt-8 font-medium text-slate-100 group-hover:text-cyan-300">{title}</h3>
                <p className="mt-2 text-xs leading-5 text-slate-500">{description}</p>
              </button>
            ))}
          </div>
        </div>
      </section>
    </div>
  );
}

function ChartPlaceholder() {
  return (
    <div className="grid min-h-[420px] place-items-center rounded-2xl border border-slate-800 bg-slate-900/65">
      <span className="h-2 w-2 animate-pulse rounded-full bg-cyan-300" />
    </div>
  );
}
