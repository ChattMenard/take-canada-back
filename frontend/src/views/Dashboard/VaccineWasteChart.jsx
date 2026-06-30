import { BarChart3 } from "lucide-react";
import { Bar, BarChart, CartesianGrid, Cell, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { useRemoteData } from "../../hooks/useRemoteData.js";

const FALLBACK = {
  purchased: 169000000,
  administered: 85000000,
  wasted: 40000000,
  expired: 13600000,
  donated: 15300000,
  waste_cost_billion: 1.2,
  per_dose_cost: 25,
  source: "Auditor General reports 6 (2022) and 1 (2023)",
};

const COLORS = ["#22d3ee", "#34d399", "#fb7185", "#f59e0b", "#a78bfa"];

export default function VaccineWasteChart() {
  const { data } = useRemoteData("/api/visualization/vaccine-waste", FALLBACK);
  const chartData = [
    ["Purchased", data.purchased],
    ["Administered", data.administered],
    ["Wasted", data.wasted],
    ["Expired", data.expired],
    ["Donated", data.donated],
  ].map(([name, value]) => ({ name, value }));

  return (
    <article className="flex h-full min-h-[420px] flex-col overflow-hidden rounded-2xl border border-slate-800 bg-slate-900/65">
      <div className="flex items-start justify-between border-b border-slate-800/80 p-5 sm:p-6">
        <div>
          <div className="mb-2 flex items-center gap-2 text-xs font-semibold uppercase tracking-[0.16em] text-rose-300">
            <BarChart3 size={14} aria-hidden="true" /> Procurement
          </div>
          <h2 className="text-lg font-semibold text-white">Vaccine inventory outcome</h2>
          <p className="mt-1 text-sm text-slate-400">Reported doses, grouped by disposition.</p>
        </div>
        <div className="text-right">
          <div className="font-mono text-xl font-semibold text-rose-300">${data.waste_cost_billion}B</div>
          <div className="text-[10px] uppercase tracking-wider text-slate-500">reported waste cost</div>
        </div>
      </div>

      <div className="flex flex-1 flex-col p-5 sm:p-6">
        <div className="h-[230px] min-h-0">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={chartData} margin={{ top: 8, right: 4, left: -18, bottom: 8 }}>
              <CartesianGrid vertical={false} stroke="#1e293b" />
              <XAxis dataKey="name" axisLine={false} tickLine={false} tick={{ fill: "#64748b", fontSize: 10 }} />
              <YAxis
                axisLine={false}
                tickLine={false}
                tick={{ fill: "#64748b", fontSize: 10 }}
                tickFormatter={(value) => `${value / 1000000}M`}
              />
              <Tooltip
                cursor={{ fill: "rgba(148,163,184,.05)" }}
                contentStyle={{
                  background: "#07101d",
                  border: "1px solid #334155",
                  borderRadius: 10,
                  color: "#e2e8f0",
                  fontSize: 12,
                }}
                formatter={(value) => [`${(value / 1000000).toFixed(1)} million`, "Doses"]}
              />
              <Bar dataKey="value" radius={[5, 5, 0, 0]} maxBarSize={46} isAnimationActive={false}>
                {chartData.map((entry, index) => (
                  <Cell key={entry.name} fill={COLORS[index]} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>
        <div className="mt-auto grid grid-cols-2 gap-3">
          <div className="rounded-xl border border-slate-800 bg-slate-950/55 p-3">
            <div className="text-[10px] uppercase tracking-wider text-slate-500">Cost per dose</div>
            <div className="mt-1 font-mono text-lg font-semibold text-white">${data.per_dose_cost}</div>
          </div>
          <div className="rounded-xl border border-slate-800 bg-slate-950/55 p-3">
            <div className="text-[10px] uppercase tracking-wider text-slate-500">Reported wasted</div>
            <div className="mt-1 font-mono text-lg font-semibold text-white">
              {(data.wasted / 1000000).toFixed(0)}M
            </div>
          </div>
        </div>
        <p className="mt-3 truncate text-[10px] text-slate-500" title={data.source}>
          Source: {data.source}
        </p>
      </div>
    </article>
  );
}
