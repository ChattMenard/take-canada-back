import { useEffect, useMemo, useState } from "react";
import {
  AlertTriangle,
  ArrowRight,
  BarChart3,
  Building,
  Calendar,
  CheckCircle2,
  Clipboard,
  Download,
  DollarSign,
  ExternalLink,
  FileText,
  GitBranch,
  Loader2,
  Scale,
  Search,
  ShieldCheck,
  TrendingUp,
  Users,
} from "lucide-react";
import { api } from "../api.js";
import { formatDate, shortHash } from "../lib/format.js";

const KIND_COLORS = {
  DONATION: "#34d399",
  CONTRACT: "#60a5fa",
  BOARD_SEAT: "#c084fc",
  OWNERSHIP: "#f59e0b",
  LOBBYING: "#f472b6",
  EMPLOYMENT: "#22d3ee",
  OTHER: "#a1a1aa",
};

const TYPE_COLORS = {
  PERSON: "#f472b6",
  BANK: "#34d399",
  AGENCY: "#60a5fa",
  COMPANY: "#f59e0b",
  OTHER: "#a1a1aa",
};

const KIND_LABELS = {
  DONATION: "Donation",
  CONTRACT: "Contract",
  BOARD_SEAT: "Board seat",
  OWNERSHIP: "Ownership",
  LOBBYING: "Lobbying",
  EMPLOYMENT: "Employment",
  OTHER: "Other",
};

const DEFAULT_POPULATION = 1_000_000;

export default function AnalysisView() {
  const [data, setData] = useState({
    evidence: [],
    entities: [],
    relationships: [],
    timeline: [],
    stats: null,
  });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [query, setQuery] = useState("");
  const [copiedId, setCopiedId] = useState(null);
  const [selectedEntityId, setSelectedEntityId] = useState(null);
  const [population, setPopulation] = useState(DEFAULT_POPULATION);

  useEffect(() => {
    let cancelled = false;
    async function load() {
      setLoading(true);
      try {
        const [evidence, entities, relationships, timeline, stats] = await Promise.all([
          api.listEvidence(),
          api.listEntities(),
          api.listRelationships(),
          api.listTimeline(),
          api.stats(),
        ]);
        if (!cancelled) {
          setData({ evidence, entities, relationships, timeline, stats });
          setError(null);
        }
      } catch (err) {
        if (!cancelled) setError(err.message || "Analysis data could not be loaded.");
      } finally {
        if (!cancelled) setLoading(false);
      }
    }
    load();
    return () => {
      cancelled = true;
    };
  }, []);

  const model = useMemo(() => buildAnalysisModel(data, population), [data, population]);

  const filteredSources = useMemo(() => {
    const q = query.trim().toLowerCase();
    return data.evidence
      .filter((ev) => !q || [ev.title, ev.source_url, ev.source_description, ev.sha256].some((v) => (v || "").toLowerCase().includes(q)))
      .sort((a, b) => new Date(b.captured_at || b.created_at) - new Date(a.captured_at || a.created_at));
  }, [data.evidence, query]);

  async function copyCitation(ev) {
    const citation = [
      ev.title,
      ev.source_url ? `Source: ${ev.source_url}` : null,
      `Captured: ${formatDate(ev.captured_at || ev.created_at)}`,
      `SHA-256: ${ev.sha256}`,
    ].filter(Boolean).join("\n");
    await navigator.clipboard?.writeText(citation);
    setCopiedId(ev.id);
    setTimeout(() => setCopiedId(null), 1200);
  }

  function exportSources(format) {
    const body = format === "csv" ? sourcesCsv(filteredSources) : sourcesMarkdown(filteredSources);
    downloadText(
      `veritas-sources.${format === "csv" ? "csv" : "md"}`,
      body,
      format === "csv" ? "text/csv" : "text/markdown"
    );
  }

  if (loading) {
    return (
      <div className="flex h-full items-center justify-center text-zinc-600">
        <Loader2 className="animate-spin" size={26} />
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex h-full items-center justify-center p-6">
        <div className="max-w-md rounded-lg border border-zinc-800 bg-zinc-950 p-5 text-center">
          <AlertTriangle className="mx-auto text-amber-300" size={28} />
          <h2 className="mt-3 text-sm font-semibold text-zinc-100">Analysis data unavailable</h2>
          <p className="mt-2 text-sm text-zinc-500">{error}</p>
        </div>
      </div>
    );
  }

  return (
    <div className="flex h-full flex-col overflow-hidden">
      <header className="shrink-0 border-b border-zinc-800 bg-[radial-gradient(circle_at_top_left,rgba(34,211,238,0.14),transparent_34%),linear-gradient(135deg,rgba(9,9,11,1),rgba(24,24,27,0.96))] px-5 py-4">
        <div className="flex flex-wrap items-start justify-between gap-4">
          <div>
            <div className="flex items-center gap-2 text-sm font-semibold text-zinc-100">
              <BarChart3 size={18} className="text-cyan-300" />
              Investigation analysis
            </div>
            <div className="mt-1 max-w-3xl text-sm text-zinc-400">
              Convert evidence-backed relationships into public-impact signals: total exposure, per-person cost, burn rate, and source confidence.
            </div>
            <div className="mt-2 flex flex-wrap gap-2 text-xs text-zinc-500">
              <span>{model.dateRange}</span>
              <span>·</span>
              <span>{model.linkedRelationshipCount} sourced links</span>
              <span>·</span>
              <span>{model.unsourcedAmountCount} amounts need evidence</span>
            </div>
          </div>
          <div className="grid grid-cols-2 gap-px overflow-hidden rounded-lg border border-zinc-800 bg-zinc-800 text-xs sm:grid-cols-5">
            <Metric icon={DollarSign} label="Tracked value" value={formatMoney(model.totalAmount)} tone="text-emerald-300" />
            <Metric icon={Users} label="Per capita" value={formatMoneyPrecise(model.perCapitaTotal)} tone="text-cyan-300" />
            <Metric icon={TrendingUp} label="Per day" value={formatMoneyPrecise(model.dailyBurn)} tone="text-rose-300" />
            <Metric icon={GitBranch} label="Relationships" value={data.stats?.relationship_count ?? 0} tone="text-pink-300" />
            <Metric icon={Building} label="Entities" value={data.stats?.entity_count ?? 0} tone="text-blue-300" />
          </div>
        </div>
      </header>

      <main className="min-h-0 flex-1 overflow-y-auto">
        <section className="grid border-b border-zinc-800 xl:grid-cols-[minmax(0,1.1fr)_minmax(360px,0.9fr)]">
          <div className="border-b border-zinc-800 p-5 xl:border-b-0 xl:border-r">
            <SectionTitle icon={Scale} title="Public impact lens" meta={`${formatPopulation(model.population)} people`} />
            <ImpactLens model={model} population={population} onPopulation={setPopulation} />
          </div>
          <div className="p-5">
            <SectionTitle icon={ShieldCheck} title="Action signals" meta="what to strengthen next" />
            <SignalGrid model={model} />
          </div>
        </section>

        <section className="grid border-b border-zinc-800 lg:grid-cols-[minmax(0,1.45fr)_minmax(360px,0.75fr)]">
          <div className="border-b border-zinc-800 p-5 lg:border-b-0 lg:border-r">
            <SectionTitle icon={DollarSign} title="Citizen wealth transfer over time" meta={`${model.datedAmountCount} dated monetary links`} />
            <MoneyTimeline data={model.amountByYear} perCapita={model.perCapitaByYear} />
          </div>
          <div className="p-5">
            <SectionTitle icon={AlertTriangle} title="Evidence coverage" meta={`${model.coverage}% linked`} />
            <div className="mt-5 space-y-4">
              <CoverageBar coverage={model.coverage} />
              <div className="grid grid-cols-3 gap-px overflow-hidden rounded-lg border border-zinc-800 bg-zinc-800 text-center text-xs">
                <TinyStat label="With sources" value={model.linkedRelationshipCount} />
                <TinyStat label="No source" value={model.unsourcedRelationshipCount} />
                <TinyStat label="No date" value={model.undatedAmountCount} />
              </div>
              <div className="space-y-2">
                {model.topFlows.slice(0, 4).map((rel) => (
                  <FlowRow key={rel.id} rel={rel} entityName={model.entityName} />
                ))}
              </div>
            </div>
          </div>
        </section>

        <section className="grid border-b border-zinc-800 lg:grid-cols-2">
          <div className="border-b border-zinc-800 p-5 lg:border-b-0 lg:border-r">
            <SectionTitle icon={GitBranch} title="Relationship mix" meta="amount by category" />
            <HorizontalBars data={model.amountByKind} colorFor={(k) => KIND_COLORS[k] || KIND_COLORS.OTHER} labelFor={(k) => KIND_LABELS[k] || k} />
          </div>
          <div className="p-5">
            <SectionTitle icon={Building} title="Entity exposure" meta="connected value by institution type" />
            <HorizontalBars data={model.amountByEntityType} colorFor={(k) => TYPE_COLORS[k] || TYPE_COLORS.OTHER} labelFor={(k) => k.toLowerCase()} />
          </div>
        </section>

        <section className="grid border-b border-zinc-800 xl:grid-cols-[minmax(0,1.4fr)_minmax(330px,0.65fr)]">
          <div className="border-b border-zinc-800 p-5 xl:border-b-0 xl:border-r">
            <SectionTitle icon={GitBranch} title="Relationship graph" meta={`${model.graph.nodes.length} nodes / ${model.graph.edges.length} links`} />
            <RelationshipGraph
              graph={model.graph}
              selectedId={selectedEntityId}
              onSelect={setSelectedEntityId}
            />
          </div>
          <GraphInspector
            entity={model.entityById.get(selectedEntityId) || model.graph.nodes[0]}
            relationships={data.relationships}
            entityName={model.entityName}
          />
        </section>

        <section className="grid border-b border-zinc-800 xl:grid-cols-[minmax(360px,0.85fr)_minmax(0,1.15fr)]">
          <div className="border-b border-zinc-800 p-5 xl:border-b-0 xl:border-r">
            <SectionTitle icon={Calendar} title="Narrative anchors" meta={`${data.timeline.length} timeline events`} />
            <div className="mt-4 space-y-3">
              {model.timelineAnchors.slice(0, 8).map((ev) => (
                <div key={ev.id} className="relative border-l border-zinc-800 pl-4">
                  <span className="absolute -left-[5px] top-1.5 h-2.5 w-2.5 rounded-full bg-cyan-300" />
                  <div className="text-sm font-medium text-zinc-200">{ev.title}</div>
                  <div className="mt-1 text-xs text-zinc-500">{formatDate(ev.occurred_at)}</div>
                  {ev.description && <p className="mt-1 line-clamp-2 text-xs text-zinc-400">{ev.description}</p>}
                </div>
              ))}
              {model.timelineAnchors.length === 0 && <EmptyLine text="No timeline events yet." />}
            </div>
          </div>

          <div className="p-5">
            <div className="flex flex-wrap items-center justify-between gap-3">
              <SectionTitle icon={FileText} title="Reference source ledger" meta={`${filteredSources.length} matching records`} />
              <div className="flex w-full flex-wrap justify-end gap-2 sm:w-auto">
                <button
                  onClick={() => exportSources("csv")}
                  className="inline-flex items-center gap-1.5 rounded-lg border border-zinc-700 px-2.5 py-2 text-xs text-zinc-300 hover:bg-zinc-800"
                >
                  <Download size={13} />
                  CSV
                </button>
                <button
                  onClick={() => exportSources("md")}
                  className="inline-flex items-center gap-1.5 rounded-lg border border-zinc-700 px-2.5 py-2 text-xs text-zinc-300 hover:bg-zinc-800"
                >
                  <Download size={13} />
                  MD
                </button>
                <div className="relative min-w-64 flex-1 sm:w-72 sm:flex-none">
                  <Search size={14} className="absolute left-3 top-1/2 -translate-y-1/2 text-zinc-500" />
                  <input
                    value={query}
                    onChange={(e) => setQuery(e.target.value)}
                    placeholder="Filter sources..."
                    className="w-full rounded-lg border border-zinc-700 bg-zinc-900 py-2 pl-9 pr-3 text-sm outline-none focus:border-cyan-500"
                  />
                </div>
              </div>
            </div>
            <div className="mt-4 overflow-hidden rounded-lg border border-zinc-800">
              <div className="max-h-[410px] overflow-y-auto">
                <table className="w-full text-left text-xs">
                  <thead className="sticky top-0 bg-zinc-950 text-zinc-500">
                    <tr className="border-b border-zinc-800">
                      <th className="px-3 py-2 font-medium">Source</th>
                      <th className="px-3 py-2 font-medium">Captured</th>
                      <th className="px-3 py-2 font-medium">Hash</th>
                      <th className="px-3 py-2 text-right font-medium">Actions</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-zinc-900">
                    {filteredSources.map((ev) => (
                      <tr key={ev.id} className="bg-zinc-950/40 align-top hover:bg-zinc-900/70">
                        <td className="max-w-[420px] px-3 py-2">
                          <div className="truncate font-medium text-zinc-200">{ev.title}</div>
                          <div className="mt-0.5 truncate text-zinc-500">{sourceLabel(ev.source_url) || ev.filename}</div>
                        </td>
                        <td className="whitespace-nowrap px-3 py-2 text-zinc-400">{formatDate(ev.captured_at || ev.created_at)}</td>
                        <td className="whitespace-nowrap px-3 py-2 font-mono text-emerald-300">{shortHash(ev.sha256)}</td>
                        <td className="px-3 py-2">
                          <div className="flex justify-end gap-1">
                            {ev.source_url && (
                              <a
                                href={ev.source_url}
                                target="_blank"
                                rel="noreferrer"
                                className="rounded p-1.5 text-zinc-500 hover:bg-zinc-800 hover:text-blue-300"
                                title="Open source"
                              >
                                <ExternalLink size={14} />
                              </a>
                            )}
                            <button
                              onClick={() => copyCitation(ev)}
                              className="rounded p-1.5 text-zinc-500 hover:bg-zinc-800 hover:text-cyan-300"
                              title="Copy citation"
                            >
                              {copiedId === ev.id ? <CheckCircle2 size={14} /> : <Clipboard size={14} />}
                            </button>
                          </div>
                        </td>
                      </tr>
                    ))}
                    {filteredSources.length === 0 && (
                      <tr>
                        <td colSpan="4" className="px-3 py-8 text-center text-zinc-600">No matching sources.</td>
                      </tr>
                    )}
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        </section>
      </main>
    </div>
  );
}

function buildAnalysisModel({ evidence, entities, relationships, timeline }, population = DEFAULT_POPULATION) {
  const normalizedPopulation = Math.max(1, Number(population) || DEFAULT_POPULATION);
  const entityMap = new Map(entities.map((e) => [e.id, e]));
  const entityName = (id) => entityMap.get(id)?.name ?? "Unknown";
  const entityType = (id) => entityMap.get(id)?.type ?? "OTHER";
  const moneyEvents = relationships.filter((r) => Number.isFinite(Number(r.amount)) && Number(r.amount) > 0);
  const totalAmount = sum(moneyEvents.map((r) => Number(r.amount)));
  const linkedRelationshipCount = relationships.filter((r) => r.linked_evidence?.length).length;
  const unsourcedRelationshipCount = relationships.length - linkedRelationshipCount;
  const coverage = relationships.length ? Math.round((linkedRelationshipCount / relationships.length) * 100) : 0;
  const unsourcedAmountCount = moneyEvents.filter((r) => !r.linked_evidence?.length).length;
  const undatedAmountCount = moneyEvents.filter((r) => !r.occurred_at).length;

  const datedMoneyEvents = moneyEvents.filter((r) => r.occurred_at);
  const rawAmountByYear = groupSum(datedMoneyEvents, (r) => new Date(r.occurred_at).getFullYear());
  const amountByYear = fillYearSeries(rawAmountByYear);
  const amountByKind = groupSum(moneyEvents, (r) => r.kind || "OTHER");
  const amountByEntityType = groupSum(
    moneyEvents.flatMap((r) => [
      { type: entityType(r.source_entity_id), amount: Number(r.amount) / 2 },
      { type: entityType(r.target_entity_id), amount: Number(r.amount) / 2 },
    ]),
    (r) => r.type
  );
  const topFlows = [...moneyEvents].sort((a, b) => Number(b.amount) - Number(a.amount));
  const dates = [
    ...relationships.map((r) => r.occurred_at),
    ...timeline.map((ev) => ev.occurred_at),
    ...evidence.map((ev) => ev.captured_at || ev.created_at),
  ].filter(Boolean).map((d) => new Date(d)).filter((d) => !Number.isNaN(d.valueOf()));
  const dateRange = dates.length
    ? `${dates.reduce((a, b) => (a < b ? a : b)).getFullYear()}-${dates.reduce((a, b) => (a > b ? a : b)).getFullYear()}`
    : "No dated records";
  const moneyDates = datedMoneyEvents
    .map((r) => new Date(r.occurred_at))
    .filter((d) => !Number.isNaN(d.valueOf()));
  const minMoneyDate = moneyDates.length ? moneyDates.reduce((a, b) => (a < b ? a : b)) : null;
  const maxMoneyDate = moneyDates.length ? moneyDates.reduce((a, b) => (a > b ? a : b)) : null;
  const spanDays = minMoneyDate && maxMoneyDate
    ? Math.max(1, Math.ceil((maxMoneyDate - minMoneyDate) / 86_400_000) + 1)
    : Math.max(1, amountByYear.length * 365);
  const yearsCovered = amountByYear.length || 1;
  const perCapitaByYear = amountByYear.map((row) => ({ ...row, value: row.value / normalizedPopulation }));
  const cumulativeByYear = amountByYear.reduce((rows, row) => [
    ...rows,
    { key: row.key, value: row.value + (rows.at(-1)?.value || 0) },
  ], []);
  const perCapitaTotal = totalAmount / normalizedPopulation;
  const perCapitaAnnual = perCapitaTotal / yearsCovered;
  const dailyBurn = totalAmount / spanDays;
  const monthlyHouseholdLoad = (perCapitaAnnual * 2.45) / 12;
  const topPerCapitaFlows = topFlows.slice(0, 5).map((rel) => ({
    ...rel,
    perCapita: Number(rel.amount || 0) / normalizedPopulation,
  }));
  const graph = buildGraph(entities, relationships);

  return {
    amountByEntityType,
    amountByKind,
    amountByYear,
    coverage,
    cumulativeByYear,
    dailyBurn,
    dateRange,
    datedAmountCount: datedMoneyEvents.length,
    entityById: entityMap,
    entityName,
    graph,
    linkedRelationshipCount,
    moneyEvents,
    monthlyHouseholdLoad,
    perCapitaAnnual,
    perCapitaByYear,
    perCapitaTotal,
    population: normalizedPopulation,
    spanDays,
    timelineAnchors: [...timeline].sort((a, b) => new Date(a.occurred_at) - new Date(b.occurred_at)),
    topPerCapitaFlows,
    topFlows,
    totalAmount,
    undatedAmountCount,
    unsourcedAmountCount,
    unsourcedRelationshipCount,
  };
}

function buildGraph(entities, relationships) {
  const width = 900;
  const height = 420;
  const cx = width / 2;
  const cy = height / 2;
  const byType = ["BANK", "AGENCY", "COMPANY", "PERSON", "OTHER"];
  const sorted = [...entities].sort((a, b) =>
    byType.indexOf(a.type) - byType.indexOf(b.type) || a.name.localeCompare(b.name)
  );
  const amountByEntity = relationships.reduce((m, rel) => {
    const amount = Number(rel.amount || 0);
    m.set(rel.source_entity_id, (m.get(rel.source_entity_id) || 0) + amount);
    m.set(rel.target_entity_id, (m.get(rel.target_entity_id) || 0) + amount);
    return m;
  }, new Map());
  const degreeByEntity = relationships.reduce((m, rel) => {
    m.set(rel.source_entity_id, (m.get(rel.source_entity_id) || 0) + 1);
    m.set(rel.target_entity_id, (m.get(rel.target_entity_id) || 0) + 1);
    return m;
  }, new Map());
  const maxExposure = Math.max(...[...amountByEntity.values()], 1);
  const nodes = sorted.map((entity, i) => {
    const angle = -Math.PI / 2 + (i / Math.max(sorted.length, 1)) * Math.PI * 2;
    const exposure = amountByEntity.get(entity.id) || 0;
    const degree = degreeByEntity.get(entity.id) || 0;
    return {
      ...entity,
      exposure,
      degree,
      r: 12 + Math.sqrt(exposure / maxExposure) * 22 + Math.min(degree, 6),
      x: cx + Math.cos(angle) * (sorted.length > 8 ? 330 : 250),
      y: cy + Math.sin(angle) * (sorted.length > 8 ? 145 : 120),
    };
  });
  const nodeMap = new Map(nodes.map((node) => [node.id, node]));
  const maxAmount = Math.max(...relationships.map((rel) => Number(rel.amount || 0)), 1);
  return {
    edges: relationships
      .map((rel) => ({
        ...rel,
        source: nodeMap.get(rel.source_entity_id),
        target: nodeMap.get(rel.target_entity_id),
        weight: 1.5 + (Number(rel.amount || 0) / maxAmount) * 7,
      }))
      .filter((edge) => edge.source && edge.target),
    height,
    nodes,
    width,
  };
}

function groupSum(rows, keyFor) {
  return [...rows.reduce((m, row) => m.set(keyFor(row), (m.get(keyFor(row)) || 0) + Number(row.amount || 0)), new Map())]
    .map(([key, value]) => ({ key, value }))
    .sort((a, b) => String(a.key).localeCompare(String(b.key)));
}

function fillYearSeries(rows) {
  if (!rows.length) return [];
  const years = rows.map((row) => Number(row.key));
  const byYear = new Map(rows.map((row) => [Number(row.key), row.value]));
  return Array.from({ length: Math.max(...years) - Math.min(...years) + 1 }, (_, i) => {
    const key = Math.min(...years) + i;
    return { key, value: byYear.get(key) || 0 };
  });
}

function sum(values) {
  return values.reduce((acc, value) => acc + Number(value || 0), 0);
}

function SectionTitle({ icon: Icon, title, meta }) {
  return (
    <div className="flex items-center justify-between gap-3">
      <div className="flex items-center gap-2">
        <Icon size={16} className="text-zinc-400" />
        <h2 className="text-sm font-semibold text-zinc-100">{title}</h2>
      </div>
      <span className="text-xs text-zinc-500">{meta}</span>
    </div>
  );
}

function Metric({ icon: Icon, label, value, tone }) {
  return (
    <div className="min-w-28 bg-zinc-950 px-3 py-2">
      <div className={`flex items-center gap-1.5 font-semibold ${tone}`}>
        <Icon size={13} />
        {value}
      </div>
      <div className="mt-0.5 text-zinc-600">{label}</div>
    </div>
  );
}

function TinyStat({ label, value }) {
  return (
    <div className="bg-zinc-950 px-2 py-3">
      <div className="text-base font-semibold text-zinc-100">{value}</div>
      <div className="mt-0.5 text-zinc-600">{label}</div>
    </div>
  );
}

function CoverageBar({ coverage }) {
  return (
    <div>
      <div className="mb-2 flex justify-between text-xs">
        <span className="text-zinc-500">Relationship source coverage</span>
        <span className="font-medium text-zinc-200">{coverage}%</span>
      </div>
      <div className="h-2 overflow-hidden rounded-full bg-zinc-800">
        <div className="h-full bg-cyan-300" style={{ width: `${coverage}%` }} />
      </div>
    </div>
  );
}

function ImpactLens({ model, population, onPopulation }) {
  const quickPops = [100_000, 1_000_000, 5_000_000];

  return (
    <div className="mt-5 grid gap-5 lg:grid-cols-[minmax(250px,0.42fr)_minmax(0,0.58fr)]">
      <div className="space-y-4">
        <div className="rounded-lg border border-zinc-800 bg-zinc-950 p-4">
          <label className="text-xs font-medium text-zinc-500" htmlFor="population-lens">Affected population</label>
          <div className="mt-2 flex items-center gap-2">
            <Users size={16} className="text-cyan-300" />
            <input
              id="population-lens"
              min="1"
              step="1000"
              type="number"
              value={population}
              onChange={(e) => onPopulation(e.target.value)}
              className="min-w-0 flex-1 rounded-md border border-zinc-700 bg-zinc-900 px-3 py-2 text-sm font-semibold text-zinc-100 outline-none focus:border-cyan-400"
            />
          </div>
          <div className="mt-3 flex flex-wrap gap-2">
            {quickPops.map((value) => (
              <button
                key={value}
                onClick={() => onPopulation(value)}
                className="rounded-md border border-zinc-800 px-2 py-1 text-xs text-zinc-400 hover:border-cyan-500 hover:text-cyan-200"
              >
                {formatPopulation(value)}
              </button>
            ))}
          </div>
        </div>

        <div className="grid grid-cols-2 gap-px overflow-hidden rounded-lg border border-zinc-800 bg-zinc-800 text-xs">
          <TinyStat label="per person" value={formatMoneyPrecise(model.perCapitaTotal)} />
          <TinyStat label="per person/year" value={formatMoneyPrecise(model.perCapitaAnnual)} />
          <TinyStat label="per household/mo" value={formatMoneyPrecise(model.monthlyHouseholdLoad)} />
          <TinyStat label="days covered" value={model.spanDays.toLocaleString()} />
        </div>
      </div>

      <div className="rounded-lg border border-zinc-800 bg-zinc-950 p-4">
        <div className="mb-3 flex items-center justify-between gap-3">
          <div className="text-xs font-medium text-zinc-500">$/capita by year</div>
          <div className="text-xs text-zinc-600">derived from dated monetary relationships</div>
        </div>
        <PerCapitaBars data={model.perCapitaByYear} />
      </div>
    </div>
  );
}

function SignalGrid({ model }) {
  const sourcedMoney = sum(model.moneyEvents.filter((r) => r.linked_evidence?.length).map((r) => r.amount));
  const sourcedMoneyShare = model.totalAmount ? Math.round((sourcedMoney / model.totalAmount) * 100) : 0;
  const undatedShare = model.moneyEvents.length ? Math.round((model.undatedAmountCount / model.moneyEvents.length) * 100) : 0;

  return (
    <div className="mt-5 grid gap-3 sm:grid-cols-3 xl:grid-cols-1 2xl:grid-cols-3">
      <InsightCard
        label="Evidence strength"
        value={`${sourcedMoneyShare}%`}
        text={`${formatMoney(sourcedMoney)} of tracked value has source links.`}
        tone="cyan"
      />
      <InsightCard
        label="Timing clarity"
        value={`${100 - undatedShare}%`}
        text={`${model.undatedAmountCount} monetary links still need dates.`}
        tone="amber"
      />
      <InsightCard
        label="Biggest per-person flow"
        value={formatMoneyPrecise(model.topPerCapitaFlows[0]?.perCapita || 0)}
        text={model.topPerCapitaFlows[0] ? `${model.entityName(model.topPerCapitaFlows[0].source_entity_id)} -> ${model.entityName(model.topPerCapitaFlows[0].target_entity_id)}` : "Add amounts to rank flows."}
        tone="emerald"
      />
      <div className="sm:col-span-3 xl:col-span-1 2xl:col-span-3">
        <CumulativeImpact data={model.cumulativeByYear} population={model.population} />
      </div>
    </div>
  );
}

function InsightCard({ label, value, text, tone }) {
  const colors = {
    amber: "border-amber-300/30 text-amber-200",
    cyan: "border-cyan-300/30 text-cyan-200",
    emerald: "border-emerald-300/30 text-emerald-200",
  };

  return (
    <div className={`rounded-lg border bg-zinc-950 p-4 ${colors[tone] || colors.cyan}`}>
      <div className="text-xs font-medium text-zinc-500">{label}</div>
      <div className="mt-2 text-2xl font-semibold">{value}</div>
      <p className="mt-2 line-clamp-2 text-xs text-zinc-500">{text}</p>
    </div>
  );
}

function PerCapitaBars({ data }) {
  const max = Math.max(...data.map((d) => d.value), 0.01);

  return data.length ? (
    <div className="flex h-56 items-end gap-2">
      {data.map((d) => (
        <div key={d.key} className="flex min-w-0 flex-1 flex-col items-center gap-2">
          <div className="flex h-44 w-full items-end rounded-t-md bg-zinc-900">
            <div
              className="w-full rounded-t-md bg-gradient-to-t from-cyan-500 to-emerald-300"
              style={{ height: `${Math.max(3, (d.value / max) * 100)}%` }}
              title={`${d.key}: ${formatMoneyPrecise(d.value)} per person`}
            />
          </div>
          <div className="max-w-full truncate text-[11px] text-zinc-600">{d.key}</div>
          <div className="max-w-full truncate text-[11px] font-medium text-zinc-300">{formatMoneyPrecise(d.value)}</div>
        </div>
      ))}
    </div>
  ) : (
    <EmptyLine text="Add dated monetary relationships to calculate per-capita time impact." />
  );
}

function CumulativeImpact({ data, population }) {
  const width = 620;
  const height = 170;
  const pad = 24;
  const max = Math.max(...data.map((d) => d.value), 1);
  const points = data.map((d, i) => ({
    ...d,
    x: data.length === 1 ? width / 2 : pad + (i * (width - pad * 2)) / (data.length - 1),
    y: height - pad - (d.value / max) * (height - pad * 2),
  }));
  const line = points.map((p) => `${p.x},${p.y}`).join(" ");

  return (
    <div className="rounded-lg border border-zinc-800 bg-zinc-950 p-4">
      <div className="mb-3 flex items-center justify-between gap-3">
        <div className="text-xs font-medium text-zinc-500">Cumulative pressure</div>
        <div className="text-xs text-zinc-600">{formatPopulation(population)} population lens</div>
      </div>
      {points.length ? (
        <svg viewBox={`0 0 ${width} ${height}`} className="h-44 w-full" role="img" aria-label="Cumulative public cost">
          {[0, 0.5, 1].map((t) => {
            const y = pad + t * (height - pad * 2);
            return <line key={t} x1={pad} x2={width - pad} y1={y} y2={y} stroke="#27272a" />;
          })}
          <polyline points={line} fill="none" stroke="#f59e0b" strokeWidth="4" strokeLinecap="round" strokeLinejoin="round" />
          {points.map((p) => (
            <g key={p.key}>
              <circle cx={p.x} cy={p.y} r="4" fill="#09090b" stroke="#fbbf24" strokeWidth="2" />
              <text x={p.x} y={height - 6} textAnchor="middle" fill="#71717a" fontSize="11">{p.key}</text>
              <text x={p.x} y={Math.max(14, p.y - 9)} textAnchor="middle" fill="#d4d4d8" fontSize="11">
                {formatMoneyPrecise(p.value / population)}
              </text>
            </g>
          ))}
        </svg>
      ) : (
        <EmptyLine text="No dated monetary records yet." />
      )}
    </div>
  );
}

function MoneyTimeline({ data, perCapita }) {
  const width = 860;
  const height = 250;
  const pad = 32;
  const max = Math.max(...data.map((d) => d.value), 1);
  const points = data.map((d, i) => ({
    ...d,
    x: data.length === 1 ? width / 2 : pad + (i * (width - pad * 2)) / (data.length - 1),
    y: height - pad - (d.value / max) * (height - pad * 2),
  }));
  const line = points.map((p) => `${p.x},${p.y}`).join(" ");
  const area = points.length ? `${pad},${height - pad} ${line} ${width - pad},${height - pad}` : "";

  return (
    <div className="mt-5 rounded-lg border border-zinc-800 bg-zinc-950 p-3">
      {points.length ? (
        <svg viewBox={`0 0 ${width} ${height}`} className="h-[290px] w-full" role="img" aria-label="Wealth transfer over time">
          <defs>
            <linearGradient id="moneyArea" x1="0" x2="0" y1="0" y2="1">
              <stop offset="0%" stopColor="#34d399" stopOpacity="0.34" />
              <stop offset="100%" stopColor="#22d3ee" stopOpacity="0.03" />
            </linearGradient>
          </defs>
          {[0, 0.25, 0.5, 0.75, 1].map((t) => {
            const y = pad + t * (height - pad * 2);
            return <line key={t} x1={pad} x2={width - pad} y1={y} y2={y} stroke="#27272a" strokeWidth="1" />;
          })}
          <polygon points={area} fill="url(#moneyArea)" />
          <polyline points={line} fill="none" stroke="#34d399" strokeWidth="4" strokeLinecap="round" strokeLinejoin="round" />
          {points.map((p) => (
            <g key={p.key}>
              <circle cx={p.x} cy={p.y} r="5" fill="#0a0a0a" stroke="#67e8f9" strokeWidth="3" />
              <text x={p.x} y={height - 8} textAnchor="middle" fill="#a1a1aa" fontSize="14">{p.key}</text>
              <text x={p.x} y={Math.max(16, p.y - 12)} textAnchor="middle" fill="#d4d4d8" fontSize="13">{formatMoney(p.value)}</text>
              <text x={p.x} y={Math.min(height - 24, p.y + 18)} textAnchor="middle" fill="#67e8f9" fontSize="11">
                {formatMoneyPrecise(perCapita.find((row) => row.key === p.key)?.value || 0)}/cap
              </text>
            </g>
          ))}
        </svg>
      ) : (
        <EmptyLine text="Add relationship amounts and dates to populate the chart." />
      )}
    </div>
  );
}

function HorizontalBars({ data, colorFor, labelFor }) {
  const max = Math.max(...data.map((d) => d.value), 1);
  return (
    <div className="mt-5 space-y-3">
      {data.length ? data.sort((a, b) => b.value - a.value).map((d) => (
        <div key={d.key}>
          <div className="mb-1 flex justify-between gap-3 text-xs">
            <span className="capitalize text-zinc-300">{labelFor(d.key)}</span>
            <span className="font-medium text-zinc-100">{formatMoney(d.value)}</span>
          </div>
          <div className="h-3 overflow-hidden rounded-full bg-zinc-800">
            <div className="h-full rounded-full" style={{ width: `${Math.max(4, (d.value / max) * 100)}%`, backgroundColor: colorFor(d.key) }} />
          </div>
        </div>
      )) : <EmptyLine text="No monetary relationships yet." />}
    </div>
  );
}

function RelationshipGraph({ graph, selectedId, onSelect }) {
  if (!graph.nodes.length) return <div className="mt-5"><EmptyLine text="Add entities and relationships to populate the graph." /></div>;

  return (
    <div className="mt-5 overflow-hidden rounded-lg border border-zinc-800 bg-zinc-950">
      <svg viewBox={`0 0 ${graph.width} ${graph.height}`} className="h-[430px] w-full" role="img" aria-label="Entity relationship graph">
        <defs>
          <marker id="graphArrow" markerHeight="8" markerWidth="8" orient="auto" refX="7" refY="4">
            <path d="M0,0 L8,4 L0,8 Z" fill="#52525b" />
          </marker>
          <radialGradient id="nodeGlow">
            <stop offset="0%" stopColor="#ffffff" stopOpacity="0.2" />
            <stop offset="100%" stopColor="#ffffff" stopOpacity="0" />
          </radialGradient>
        </defs>
        {graph.edges.map((edge) => {
          const color = KIND_COLORS[edge.kind] || KIND_COLORS.OTHER;
          const selected = selectedId && [edge.source.id, edge.target.id].includes(selectedId);
          return (
            <g key={edge.id} opacity={selectedId && !selected ? 0.16 : 0.82}>
              <line
                x1={edge.source.x}
                y1={edge.source.y}
                x2={edge.target.x}
                y2={edge.target.y}
                stroke={color}
                strokeLinecap="round"
                strokeWidth={edge.weight}
                markerEnd="url(#graphArrow)"
              />
              {edge.amount != null && (
                <text
                  x={(edge.source.x + edge.target.x) / 2}
                  y={(edge.source.y + edge.target.y) / 2 - 6}
                  textAnchor="middle"
                  fill="#d4d4d8"
                  fontSize="12"
                  paintOrder="stroke"
                  stroke="#09090b"
                  strokeWidth="5"
                >
                  {formatMoney(edge.amount)}
                </text>
              )}
            </g>
          );
        })}
        {graph.nodes.map((node) => {
          const selected = selectedId === node.id;
          return (
            <g
              key={node.id}
              onClick={() => onSelect(selected ? null : node.id)}
              className="cursor-pointer"
              opacity={selectedId && !selected ? 0.48 : 1}
            >
              <circle cx={node.x} cy={node.y} r={node.r + 16} fill="url(#nodeGlow)" />
              <circle
                cx={node.x}
                cy={node.y}
                r={node.r}
                fill="#09090b"
                stroke={TYPE_COLORS[node.type] || TYPE_COLORS.OTHER}
                strokeWidth={selected ? 5 : 3}
              />
              <circle cx={node.x - node.r / 3} cy={node.y - node.r / 3} r={Math.max(3, node.r / 5)} fill={TYPE_COLORS[node.type] || TYPE_COLORS.OTHER} opacity="0.85" />
              <text
                x={node.x}
                y={node.y + node.r + 18}
                textAnchor="middle"
                fill="#e4e4e7"
                fontSize="13"
                fontWeight={selected ? "700" : "500"}
                paintOrder="stroke"
                stroke="#09090b"
                strokeWidth="5"
              >
                {compactName(node.name)}
              </text>
              {node.exposure > 0 && (
                <text
                  x={node.x}
                  y={node.y + 4}
                  textAnchor="middle"
                  fill="#d4d4d8"
                  fontSize="11"
                  fontWeight="700"
                >
                  {formatMoney(node.exposure)}
                </text>
              )}
            </g>
          );
        })}
      </svg>
      <div className="flex flex-wrap gap-3 border-t border-zinc-800 px-4 py-3 text-xs text-zinc-500">
        {Object.entries(TYPE_COLORS).map(([type, color]) => (
          <span key={type} className="inline-flex items-center gap-1.5">
            <span className="h-2.5 w-2.5 rounded-full" style={{ backgroundColor: color }} />
            {type.toLowerCase()}
          </span>
        ))}
      </div>
    </div>
  );
}

function GraphInspector({ entity, relationships, entityName }) {
  const related = entity
    ? relationships
        .filter((rel) => rel.source_entity_id === entity.id || rel.target_entity_id === entity.id)
        .sort((a, b) => Number(b.amount || 0) - Number(a.amount || 0))
    : [];

  return (
    <aside className="p-5">
      <SectionTitle icon={Building} title="Selected entity" meta={entity?.type?.toLowerCase() || "none"} />
      {entity ? (
        <div className="mt-5">
          <div className="rounded-lg border border-zinc-800 bg-zinc-950 p-4">
            <div className="flex items-start justify-between gap-3">
              <div>
                <div className="text-lg font-semibold text-zinc-100">{entity.name}</div>
                <div className="mt-1 text-xs uppercase tracking-wide text-zinc-500">{entity.type}</div>
              </div>
              <div className="rounded-md border border-zinc-800 px-2 py-1 text-right text-xs">
                <div className="font-semibold text-emerald-300">{formatMoney(entity.exposure || 0)}</div>
                <div className="text-zinc-600">exposure</div>
              </div>
            </div>
            {entity.description && <p className="mt-3 text-sm text-zinc-400">{entity.description}</p>}
          </div>
          <div className="mt-4 space-y-2">
            {related.slice(0, 7).map((rel) => (
              <div key={rel.id} className="rounded-lg border border-zinc-800 bg-zinc-950 p-3">
                <div className="flex items-center gap-2 text-xs">
                  <span className="truncate text-zinc-200">{entityName(rel.source_entity_id)}</span>
                  <ArrowRight size={12} className="shrink-0 text-zinc-600" />
                  <span className="truncate text-zinc-200">{entityName(rel.target_entity_id)}</span>
                </div>
                <div className="mt-2 flex items-center justify-between gap-3">
                  <span className="text-xs text-zinc-500">{KIND_LABELS[rel.kind] || rel.kind}</span>
                  <span className="text-xs font-semibold text-emerald-300">{rel.amount != null ? formatMoney(rel.amount) : "No amount"}</span>
                </div>
                {rel.linked_evidence?.length > 0 && (
                  <div className="mt-2 flex flex-wrap gap-1">
                    {rel.linked_evidence.slice(0, 2).map((ev) => (
                      <span key={ev.id} className="inline-flex items-center gap-1 rounded bg-zinc-900 px-1.5 py-0.5 text-[11px] text-zinc-400">
                        <FileText size={10} />
                        {ev.title.length > 28 ? `${ev.title.slice(0, 28)}...` : ev.title}
                      </span>
                    ))}
                  </div>
                )}
              </div>
            ))}
            {related.length === 0 && <EmptyLine text="No relationships for this entity." />}
          </div>
        </div>
      ) : (
        <div className="mt-5"><EmptyLine text="Select a graph node to inspect evidence-backed links." /></div>
      )}
    </aside>
  );
}

function FlowRow({ rel, entityName }) {
  return (
    <div className="rounded-lg border border-zinc-800 bg-zinc-950 p-3">
      <div className="flex items-center gap-2 text-xs text-zinc-500">
        <span className="truncate text-zinc-200">{entityName(rel.source_entity_id)}</span>
        <ArrowRight size={13} className="shrink-0 text-zinc-600" />
        <span className="truncate text-zinc-200">{entityName(rel.target_entity_id)}</span>
      </div>
      <div className="mt-2 flex items-center justify-between gap-3">
        <span className="text-sm font-semibold text-emerald-300">{formatMoney(Number(rel.amount))}</span>
        <span className="text-xs text-zinc-500">{KIND_LABELS[rel.kind] || rel.kind}</span>
      </div>
      <div className="mt-2 flex items-center gap-1 text-xs text-zinc-600">
        {rel.linked_evidence?.length ? <CheckCircle2 size={12} className="text-cyan-300" /> : <AlertTriangle size={12} className="text-amber-300" />}
        {rel.linked_evidence?.length || 0} source{rel.linked_evidence?.length === 1 ? "" : "s"}
      </div>
    </div>
  );
}

function compactName(name) {
  return name.length > 20 ? `${name.slice(0, 18)}...` : name;
}

function EmptyLine({ text }) {
  return <div className="rounded-lg border border-dashed border-zinc-800 px-4 py-8 text-center text-sm text-zinc-600">{text}</div>;
}

function formatMoney(value) {
  const n = Math.abs(Number(value || 0));
  const sign = Number(value || 0) < 0 ? "-" : "";
  if (n >= 1_000_000_000) return `${sign}$${(n / 1_000_000_000).toFixed(1)}B`;
  if (n >= 1_000_000) return `${sign}$${(n / 1_000_000).toFixed(1)}M`;
  if (n >= 1_000) return `${sign}$${(n / 1_000).toFixed(1)}K`;
  return `${sign}$${n.toLocaleString()}`;
}

function formatMoneyPrecise(value) {
  const n = Math.abs(Number(value || 0));
  const sign = Number(value || 0) < 0 ? "-" : "";
  if (n >= 1_000_000) return formatMoney(value);
  if (n >= 1_000) return `${sign}$${Math.round(n).toLocaleString()}`;
  if (n >= 10) return `${sign}$${n.toFixed(1)}`;
  return `${sign}$${n.toFixed(2)}`;
}

function formatPopulation(value) {
  const n = Number(value || 0);
  if (n >= 1_000_000) return `${(n / 1_000_000).toLocaleString(undefined, { maximumFractionDigits: 1 })}M`;
  if (n >= 1_000) return `${(n / 1_000).toLocaleString(undefined, { maximumFractionDigits: 0 })}K`;
  return n.toLocaleString();
}

function sourcesCsv(sources) {
  return [
    ["title", "source_url", "captured_at", "sha256", "filename"].map(csvCell).join(","),
    ...sources.map((ev) =>
      [ev.title, ev.source_url || "", ev.captured_at || ev.created_at || "", ev.sha256, ev.filename].map(csvCell).join(",")
    ),
  ].join("\n");
}

function sourcesMarkdown(sources) {
  return [
    "# Veritas Source Ledger",
    "",
    ...sources.flatMap((ev, i) => [
      `## ${i + 1}. ${ev.title}`,
      "",
      ev.source_url ? `- Source: ${ev.source_url}` : `- File: ${ev.filename}`,
      `- Captured: ${formatDate(ev.captured_at || ev.created_at)}`,
      `- SHA-256: \`${ev.sha256}\``,
      "",
    ]),
  ].join("\n");
}

function csvCell(value) {
  return `"${String(value ?? "").replaceAll('"', '""')}"`;
}

function downloadText(filename, text, type) {
  const url = URL.createObjectURL(new Blob([text], { type }));
  const a = document.createElement("a");
  a.href = url;
  a.download = filename;
  a.click();
  URL.revokeObjectURL(url);
}

function sourceLabel(url) {
  if (!url) return "";
  try {
    const u = new URL(url);
    return `${u.hostname}${u.pathname}`;
  } catch (_) {
    return url;
  }
}
