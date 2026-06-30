import { Building2, Users } from "lucide-react";
import { useMemo, useState } from "react";
import fallbackMeetings from "../../data/lobbying_meetings.json";
import { useRemoteData } from "../../hooks/useRemoteData.js";

const MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];

export default function LobbyingHeatmap({ onOpenSource }) {
  const { data } = useRemoteData("/api/visualization/lobbying", { meetings: fallbackMeetings });
  const meetings = data.meetings || [];
  const years = useMemo(() => [...new Set(meetings.map(({ date }) => date.slice(0, 4)))].sort(), [meetings]);
  const [selected, setSelected] = useState(() => fallbackMeetings[3]);
  const countAt = (year, month) =>
    meetings.filter(({ date }) => date.startsWith(`${year}-${String(month + 1).padStart(2, "0")}`)).length;

  return (
    <article className="flex h-full min-h-[420px] flex-col overflow-hidden rounded-2xl border border-slate-800 bg-slate-900/65">
      <div className="flex items-start justify-between border-b border-slate-800/80 p-5 sm:p-6">
        <div>
          <div className="mb-2 flex items-center gap-2 text-xs font-semibold uppercase tracking-[0.16em] text-violet-300">
            <Building2 size={14} aria-hidden="true" /> Access
          </div>
          <h2 className="text-lg font-semibold text-white">Lobbying contact density</h2>
          <p className="mt-1 text-sm text-slate-400">Innovative Medicines Canada meetings in the index.</p>
        </div>
        <span className="rounded-full border border-slate-700 px-2.5 py-1 text-xs text-slate-400">
          {meetings.length} contacts
        </span>
      </div>

      <div className="flex flex-1 flex-col p-5 sm:p-6">
        <div className="overflow-x-auto pb-2">
          <div className="min-w-[520px]">
            <div className="grid grid-cols-[48px_repeat(12,minmax(24px,1fr))] gap-1">
              <span />
              {MONTHS.map((month) => (
                <span key={month} className="pb-1 text-center text-[9px] text-slate-600">
                  {month}
                </span>
              ))}
              {years.flatMap((year) => [
                <span key={`${year}-label`} className="self-center font-mono text-[10px] text-slate-500">
                  {year}
                </span>,
                ...MONTHS.map((_, month) => {
                  const count = countAt(year, month);
                  const indexed = meetings.find(
                    ({ date }) => date.startsWith(`${year}-${String(month + 1).padStart(2, "0")}`),
                  );
                  return (
                    <button
                      key={`${year}-${month}`}
                      onClick={() => indexed && setSelected(indexed)}
                      disabled={!count}
                      className={`h-8 rounded transition focus:outline-none focus:ring-2 focus:ring-violet-300 ${
                        count > 1
                          ? "bg-violet-400 text-slate-950"
                          : count === 1
                            ? "bg-violet-400/45 text-white hover:bg-violet-400/65"
                            : "cursor-default bg-slate-800/65"
                      }`}
                      aria-label={`${MONTHS[month]} ${year}: ${count} indexed meetings`}
                    >
                      {count || ""}
                    </button>
                  );
                }),
              ])}
            </div>
          </div>
        </div>

        {selected && (
          <button
            onClick={() => onOpenSource?.(selected.source_document)}
            className="mt-5 rounded-xl border border-slate-700/80 bg-slate-950/65 p-4 text-left transition hover:border-violet-400/40"
          >
            <div className="flex items-center justify-between gap-3">
              <span className="font-mono text-xs text-violet-300">{selected.date}</span>
              <span className="flex items-center gap-1.5 text-[10px] uppercase tracking-wider text-slate-500">
                <Users size={12} aria-hidden="true" /> {selected.attendees.length || 1} indexed
              </span>
            </div>
            <div className="mt-2 text-sm font-medium text-slate-100">{selected.subject}</div>
            <p className="mt-1 line-clamp-2 text-xs leading-5 text-slate-400">{selected.description}</p>
          </button>
        )}

        <div className="mt-auto flex items-center gap-4 pt-4 text-[10px] text-slate-500">
          <span>Fewer</span>
          <span className="h-3 w-3 rounded-sm bg-slate-800" />
          <span className="h-3 w-3 rounded-sm bg-violet-400/45" />
          <span className="h-3 w-3 rounded-sm bg-violet-400" />
          <span>More</span>
        </div>
      </div>
    </article>
  );
}
