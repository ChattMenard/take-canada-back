import { AnimatePresence, motion } from "framer-motion";
import { ArrowUpRight, CalendarDays } from "lucide-react";
import { useMemo, useState } from "react";
import fallbackEvents from "../../data/timeline_events.json";
import { useRemoteData } from "../../hooks/useRemoteData.js";

const COLORS = {
  funding: "#34d399",
  patent: "#a78bfa",
  simulation: "#f59e0b",
  agreement: "#fb7185",
  general: "#60a5fa",
};

const clean = (value = "") => value.replace(/\*\*/g, "");

export default function HeroTimeline({ onOpenSource }) {
  const { data, status } = useRemoteData("/api/visualization/timeline", {
    events: fallbackEvents,
  });
  const events = useMemo(
    () =>
      (data.events || [])
        .filter(({ date }) => new Date(date).getFullYear() >= 2013)
        .sort((a, b) => new Date(a.date) - new Date(b.date)),
    [data],
  );
  const [selected, setSelected] = useState(
    () => fallbackEvents.find(({ date }) => date === "2019-12-12") || fallbackEvents[0],
  );
  const start = new Date("2013-01-01").getTime();
  const end = new Date("2020-12-31").getTime();
  const position = (date) =>
    Math.max(1, Math.min(99, ((new Date(date).getTime() - start) / (end - start)) * 100));

  return (
    <article className="flex h-full min-h-[420px] flex-col overflow-hidden rounded-2xl border border-slate-800 bg-slate-900/65">
      <div className="flex items-start justify-between gap-4 border-b border-slate-800/80 p-5 sm:p-6">
        <div>
          <div className="mb-2 flex items-center gap-2 text-xs font-semibold uppercase tracking-[0.16em] text-cyan-300">
            <CalendarDays size={14} aria-hidden="true" /> Chronology
          </div>
          <h2 className="text-lg font-semibold text-white">Pre-pandemic platform timeline</h2>
          <p className="mt-1 text-sm text-slate-400">Funding, patent, simulation and agreement records.</p>
        </div>
        <span className="rounded-full border border-slate-700 px-2.5 py-1 text-xs text-slate-400">
          {events.length} events
        </span>
      </div>

      <div className="flex flex-1 flex-col p-5 sm:p-6">
        <div className="relative mb-7 mt-9 h-16" aria-label="Interactive event timeline">
          <div className="absolute left-0 right-0 top-7 h-px bg-slate-700" />
          <div
            className="absolute top-0 h-14 rounded-md border border-rose-400/40 bg-rose-400/10"
            style={{
              left: `${position("2019-12-12")}%`,
              width: `${Math.max(1.2, position("2019-12-31") - position("2019-12-12"))}%`,
            }}
          />
          <span
            className="absolute -top-7 -translate-x-1/2 whitespace-nowrap rounded bg-rose-400/10 px-2 py-1 text-[10px] font-semibold uppercase tracking-wider text-rose-300"
            style={{ left: `${position("2019-12-21")}%` }}
          >
            19-day interval
          </span>
          {events.map((event, index) => (
            <motion.button
              type="button"
              key={`${event.date}-${index}`}
              initial={{ scale: 0 }}
              animate={{ scale: 1 }}
              transition={{ delay: Math.min(index * 0.025, 0.4) }}
              onClick={() => setSelected(event)}
              className="absolute top-[21px] z-10 -ml-2 grid h-4 w-4 place-items-center rounded-full focus:outline-none focus:ring-2 focus:ring-cyan-300 focus:ring-offset-2 focus:ring-offset-slate-900"
              style={{
                left: `${position(event.date)}%`,
                background: selected === event ? "white" : COLORS[event.category] || COLORS.general,
                boxShadow: selected === event ? `0 0 0 4px ${COLORS[event.category] || COLORS.general}55` : "none",
              }}
              aria-label={`${event.date}: ${clean(event.title)}`}
            />
          ))}
          {["2013", "2015", "2017", "2019", "2021"].map((year, index) => (
            <span
              key={year}
              className="absolute top-11 -translate-x-1/2 text-[10px] text-slate-500"
              style={{ left: `${index * 25}%` }}
            >
              {year}
            </span>
          ))}
        </div>

        <AnimatePresence mode="wait">
          {selected && (
            <motion.div
              key={`${selected.date}-${selected.title}`}
              initial={{ opacity: 0, y: 6 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -4 }}
              className="mt-auto rounded-xl border border-slate-700/80 bg-slate-950/70 p-4"
            >
              <div className="flex items-center justify-between gap-3">
                <span className="font-mono text-xs text-cyan-300">{selected.date}</span>
                <span
                  className="rounded-full px-2 py-0.5 text-[10px] font-semibold uppercase tracking-wider"
                  style={{
                    color: COLORS[selected.category] || COLORS.general,
                    background: `${COLORS[selected.category] || COLORS.general}18`,
                  }}
                >
                  {selected.category}
                </span>
              </div>
              <h3 className="mt-2 text-sm font-medium leading-6 text-slate-100">{clean(selected.title)}</h3>
              <button
                onClick={() => onOpenSource?.(selected.source_document)}
                className="mt-3 inline-flex items-center gap-1.5 text-xs font-medium text-slate-400 transition hover:text-cyan-300"
              >
                Review source <ArrowUpRight size={13} aria-hidden="true" />
              </button>
            </motion.div>
          )}
        </AnimatePresence>

        <div className="mt-4 flex flex-wrap gap-x-4 gap-y-2">
          {Object.entries(COLORS)
            .slice(0, 4)
            .map(([label, color]) => (
              <span key={label} className="flex items-center gap-1.5 text-[11px] capitalize text-slate-500">
                <span className="h-1.5 w-1.5 rounded-full" style={{ background: color }} />
                {label}
              </span>
            ))}
          {status === "fallback" && <span className="ml-auto text-[10px] text-amber-400">Local index</span>}
        </div>
      </div>
    </article>
  );
}
