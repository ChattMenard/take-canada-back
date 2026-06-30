import { motion } from "framer-motion";
import { ArrowRight, Banknote } from "lucide-react";
import { useMemo } from "react";
import fallbackFlows from "../../data/financial_flows.json";
import { useRemoteData } from "../../hooks/useRemoteData.js";

export default function MoneyFlowSankey({ onOpenSource }) {
  const { data, status } = useRemoteData("/api/visualization/financial-flow", {
    flows: fallbackFlows,
  });
  const flows = useMemo(() => data.flows || [], [data]);
  const max = Math.max(...flows.map(({ amount }) => amount), 1);

  return (
    <article className="flex h-full min-h-[420px] flex-col overflow-hidden rounded-2xl border border-slate-800 bg-slate-900/65">
      <div className="flex items-start justify-between border-b border-slate-800/80 p-5 sm:p-6">
        <div>
          <div className="mb-2 flex items-center gap-2 text-xs font-semibold uppercase tracking-[0.16em] text-emerald-300">
            <Banknote size={14} aria-hidden="true" /> Capital
          </div>
          <h2 className="text-lg font-semibold text-white">Documented funding flows</h2>
          <p className="mt-1 text-sm text-slate-400">Amounts extracted from indexed source material.</p>
        </div>
        <span className="rounded-full border border-slate-700 px-2.5 py-1 text-xs text-slate-400">
          {flows.length} records
        </span>
      </div>

      <div className="flex flex-1 flex-col gap-3 p-5 sm:p-6">
        {flows.map((flow, index) => {
          const strength = 22 + (Math.log10(flow.amount + 1) / Math.log10(max + 1)) * 78;
          return (
            <button
              key={`${flow.source}-${flow.target}-${index}`}
              onClick={() => onOpenSource?.(flow.source_document)}
              className="group rounded-xl border border-slate-800 bg-slate-950/55 p-4 text-left transition hover:border-slate-700 hover:bg-slate-950"
            >
              <div className="flex items-center gap-3">
                <div className="min-w-0 flex-1">
                  <div className="flex items-center justify-between gap-3 text-sm">
                    <span className="truncate font-medium text-slate-100">{flow.source}</span>
                    <ArrowRight size={14} className="shrink-0 text-slate-600" aria-hidden="true" />
                    <span className="truncate text-right font-medium text-slate-100">{flow.target}</span>
                  </div>
                  <div className="mt-3 h-1.5 overflow-hidden rounded-full bg-slate-800">
                    <motion.div
                      initial={{ width: 0 }}
                      animate={{ width: `${strength}%` }}
                      transition={{ duration: 0.65, delay: index * 0.08 }}
                      className="h-full rounded-full bg-gradient-to-r from-cyan-400 via-emerald-400 to-amber-300"
                    />
                  </div>
                </div>
                <span className="w-24 shrink-0 text-right font-mono text-xs font-semibold text-emerald-300">
                  {flow.amount_display}
                </span>
              </div>
            </button>
          );
        })}

        <div className="mt-auto rounded-xl border border-amber-300/20 bg-amber-300/[0.06] p-4">
          <div className="text-xs font-semibold uppercase tracking-[0.14em] text-amber-300">Reading note</div>
          <p className="mt-1.5 text-xs leading-5 text-slate-400">
            Values use the units stated by each source. They are displayed as documented, not summed across
            currencies or reporting periods.
          </p>
        </div>
        {status === "fallback" && <span className="text-[10px] text-amber-400">Using locally indexed records</span>}
      </div>
    </article>
  );
}
