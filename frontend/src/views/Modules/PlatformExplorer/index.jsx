import { useMemo, useState } from "react";
import ReactFlow, { Background, Controls, MarkerType } from "reactflow";
import "reactflow/dist/style.css";
import {
  CalendarRange,
  Download,
  ExternalLink,
  FileImage,
  Filter,
  Network,
  Printer,
} from "lucide-react";
import fallbackEvents from "../../../data/timeline_events.json";
import fallbackFlows from "../../../data/financial_flows.json";
import fallbackNodes from "../../../data/network_nodes.json";
import { useRemoteData } from "../../../hooks/useRemoteData.js";
import { useVisualizationStore } from "../../../store/useVisualizationStore.js";

const TRACKS = [
  ["funding", "Funding", "#34d399"],
  ["patent", "Patents", "#a78bfa"],
  ["simulation", "Simulations", "#f59e0b"],
  ["agreement", "Agreements", "#fb7185"],
  ["general", "Personnel / other", "#60a5fa"],
];
const NETWORK_LAYERS = ["DARPA", "Gates", "NIH", "Private"];
const clean = (value = "") => value.replace(/\*\*/g, "");
const escapeXml = (value) =>
  String(value).replace(/[<>&'"]/g, (char) => ({ "<": "&lt;", ">": "&gt;", "&": "&amp;", "'": "&apos;", '"': "&quot;" })[char]);

function saveBlob(blob, filename) {
  const url = URL.createObjectURL(blob);
  const link = Object.assign(document.createElement("a"), { href: url, download: filename });
  link.click();
  URL.revokeObjectURL(url);
}

function exportCsv(events) {
  const quote = (value) => `"${String(value ?? "").replaceAll('"', '""')}"`;
  const rows = [
    ["date", "category", "title", "source_document"],
    ...events.map(({ date, category, title, source_document }) => [
      date,
      category,
      clean(title),
      source_document,
    ]),
  ];
  saveBlob(new Blob([rows.map((row) => row.map(quote).join(",")).join("\n")], { type: "text/csv" }), "platform-timeline.csv");
}

function exportPng(events) {
  const lines = events.slice(0, 10);
  const svg = `<svg xmlns="http://www.w3.org/2000/svg" width="1400" height="900">
    <rect width="1400" height="900" fill="#07101d"/>
    <text x="72" y="90" fill="#67e8f9" font-family="sans-serif" font-size="18" letter-spacing="3">VERITAS / EVIDENCE EXPORT</text>
    <text x="72" y="150" fill="#f8fafc" font-family="sans-serif" font-size="44" font-weight="600">Pre-pandemic platform timeline</text>
    <text x="72" y="195" fill="#64748b" font-family="sans-serif" font-size="18">${events.length} filtered events</text>
    ${lines
      .map(
        (event, index) => `<circle cx="86" cy="${260 + index * 58}" r="6" fill="#22d3ee"/>
        <text x="112" y="${266 + index * 58}" fill="#94a3b8" font-family="monospace" font-size="15">${escapeXml(event.date)}</text>
        <text x="240" y="${266 + index * 58}" fill="#e2e8f0" font-family="sans-serif" font-size="17">${escapeXml(clean(event.title).slice(0, 100))}</text>`,
      )
      .join("")}
  </svg>`;
  const image = new Image();
  const url = URL.createObjectURL(new Blob([svg], { type: "image/svg+xml" }));
  image.onload = () => {
    const canvas = Object.assign(document.createElement("canvas"), { width: 1400, height: 900 });
    canvas.getContext("2d").drawImage(image, 0, 0);
    canvas.toBlob((blob) => blob && saveBlob(blob, "platform-timeline.png"), "image/png");
    URL.revokeObjectURL(url);
  };
  image.src = url;
}

export default function PlatformExplorer({ onOpenSource }) {
  const { data: timelinePayload } = useRemoteData("/api/visualization/timeline", { events: fallbackEvents });
  useRemoteData("/api/visualization/network", { nodes: fallbackNodes, edges: fallbackFlows });
  const { data: flowPayload } = useRemoteData("/api/visualization/financial-flow", {
    flows: fallbackFlows,
  });
  const {
    timelineRange,
    timelineTracks,
    networkLayers,
    setTimelineRange,
    toggleTimelineTrack,
    toggleNetworkLayer,
  } = useVisualizationStore();
  const [selectedEvent, setSelectedEvent] = useState(fallbackEvents[15]);
  const [activePanel, setActivePanel] = useState("timeline");

  const events = useMemo(
    () =>
      (timelinePayload.events || [])
        .filter((event) => {
          const year = Number(event.date.slice(0, 4));
          return year >= timelineRange[0] && year <= timelineRange[1] && timelineTracks.includes(event.category);
        })
        .sort((a, b) => new Date(a.date) - new Date(b.date)),
    [timelinePayload, timelineRange, timelineTracks],
  );
  const sourceFlows = flowPayload.flows || [];
  const visibleFlows = sourceFlows.filter((flow) => {
    const layer = flow.source.toUpperCase().includes("DARPA") ? "DARPA" : "Private";
    return networkLayers.includes(layer);
  });
  const graph = useMemo(() => {
    const entities = [...new Set(visibleFlows.flatMap(({ source, target }) => [source, target]))];
    const nodes = entities.map((name, index) => ({
      id: name.toLowerCase().replaceAll(" ", "_"),
      position: { x: index % 2 ? 460 : 40, y: Math.floor(index / 2) * 130 + 40 },
      data: { label: name },
      style: {
        background: name === "DARPA" || name === "Penn" ? "#123047" : "#182336",
        border: "1px solid #475569",
        color: "#e2e8f0",
        borderRadius: 12,
        padding: 12,
        width: 160,
        fontSize: 12,
      },
    }));
    const edges = visibleFlows.map((flow, index) => ({
      id: `flow-${index}`,
      source: flow.source.toLowerCase().replaceAll(" ", "_"),
      target: flow.target.toLowerCase().replaceAll(" ", "_"),
      label: flow.amount_display,
      animated: true,
      markerEnd: { type: MarkerType.ArrowClosed, color: "#22d3ee" },
      style: { stroke: "#22d3ee", strokeWidth: 2 },
      labelStyle: { fill: "#94a3b8", fontSize: 10 },
      labelBgStyle: { fill: "#07101d" },
    }));
    return { nodes, edges };
  }, [visibleFlows]);

  const left = `${((timelineRange[0] - 2005) / 18) * 100}%`;
  const width = `${((timelineRange[1] - timelineRange[0]) / 18) * 100}%`;

  return (
    <div>
      <div className="border-b border-slate-800 px-4 py-7 sm:px-6 lg:px-8">
        <div className="flex flex-col justify-between gap-5 xl:flex-row xl:items-end">
          <div>
            <div className="text-xs font-semibold uppercase tracking-[0.18em] text-cyan-300">
              Investigation 01
            </div>
            <h1 className="mt-2 text-3xl font-semibold tracking-tight text-white">Pre-pandemic platform explorer</h1>
            <p className="mt-2 max-w-3xl text-sm leading-6 text-slate-400">
              Examine the documented sequence of funding, patent licensing, simulations and institutional
              agreements. Filters change the view; source records remain unchanged.
            </p>
          </div>
          <div className="flex flex-wrap gap-2">
            <button onClick={() => exportCsv(events)} className="module-action">
              <Download size={14} /> CSV
            </button>
            <button onClick={() => exportPng(events)} className="module-action">
              <FileImage size={14} /> PNG
            </button>
            <button onClick={() => window.print()} className="module-action">
              <Printer size={14} /> Print / PDF
            </button>
          </div>
        </div>
      </div>

      <div className="grid min-h-[720px] lg:grid-cols-[250px_1fr]">
        <aside className="border-b border-slate-800 bg-slate-950/30 p-5 lg:border-b-0 lg:border-r">
          <div className="flex items-center gap-2 text-xs font-semibold uppercase tracking-[0.14em] text-slate-400">
            <Filter size={14} /> View controls
          </div>

          <fieldset className="mt-7">
            <legend className="text-xs font-medium text-slate-300">Timeline layers</legend>
            <div className="mt-3 space-y-2">
              {TRACKS.map(([id, label, color]) => (
                <label key={id} className="flex cursor-pointer items-center gap-2.5 rounded-lg px-2 py-1.5 hover:bg-slate-900">
                  <input
                    type="checkbox"
                    checked={timelineTracks.includes(id)}
                    onChange={() => toggleTimelineTrack(id)}
                    className="h-3.5 w-3.5 rounded border-slate-600 bg-slate-900 text-cyan-400 focus:ring-cyan-300"
                  />
                  <span className="h-2 w-2 rounded-full" style={{ background: color }} />
                  <span className="text-xs text-slate-400">{label}</span>
                </label>
              ))}
            </div>
          </fieldset>

          <fieldset className="mt-8">
            <legend className="text-xs font-medium text-slate-300">Funding layers</legend>
            <div className="mt-3 flex flex-wrap gap-2">
              {NETWORK_LAYERS.map((layer) => (
                <button
                  key={layer}
                  onClick={() => toggleNetworkLayer(layer)}
                  className={`rounded-full border px-2.5 py-1 text-[10px] transition ${
                    networkLayers.includes(layer)
                      ? "border-cyan-300/40 bg-cyan-300/10 text-cyan-300"
                      : "border-slate-800 text-slate-600"
                  }`}
                >
                  {layer}
                </button>
              ))}
            </div>
          </fieldset>

          <div className="mt-8 rounded-xl border border-slate-800 bg-slate-900/60 p-4">
            <div className="text-[10px] uppercase tracking-wider text-slate-500">Current result</div>
            <div className="mt-2 font-mono text-2xl text-white">{events.length}</div>
            <div className="text-xs text-slate-500">events in range</div>
          </div>
        </aside>

        <div className="min-w-0 p-4 sm:p-6 lg:p-8">
          <div className="mb-5 flex gap-1 rounded-xl border border-slate-800 bg-slate-950/50 p-1">
            {[
              ["timeline", CalendarRange, "Parallel timeline"],
              ["network", Network, "Funding network"],
            ].map(([id, Icon, label]) => (
              <button
                key={id}
                onClick={() => setActivePanel(id)}
                className={`flex flex-1 items-center justify-center gap-2 rounded-lg px-3 py-2 text-xs font-medium transition ${
                  activePanel === id ? "bg-slate-800 text-white" : "text-slate-500 hover:text-slate-300"
                }`}
              >
                <Icon size={14} /> {label}
              </button>
            ))}
          </div>

          {activePanel === "timeline" ? (
            <div className="rounded-2xl border border-slate-800 bg-slate-900/50">
              <div className="border-b border-slate-800 p-5">
                <div className="flex items-center justify-between">
                  <h2 className="font-medium text-white">Evidence chronology</h2>
                  <span className="font-mono text-xs text-cyan-300">
                    {timelineRange[0]}—{timelineRange[1]}
                  </span>
                </div>
                <div className="relative mt-5 h-7">
                  <div className="absolute left-0 right-0 top-3 h-1 rounded bg-slate-800" />
                  <div className="absolute top-3 h-1 bg-cyan-300" style={{ left, width }} />
                  <input
                    aria-label="Start year"
                    type="range"
                    min="2005"
                    max="2022"
                    value={timelineRange[0]}
                    onChange={(event) =>
                      setTimelineRange([Math.min(Number(event.target.value), timelineRange[1] - 1), timelineRange[1]])
                    }
                    className="timeline-range absolute inset-0 w-full"
                  />
                  <input
                    aria-label="End year"
                    type="range"
                    min="2006"
                    max="2023"
                    value={timelineRange[1]}
                    onChange={(event) =>
                      setTimelineRange([timelineRange[0], Math.max(Number(event.target.value), timelineRange[0] + 1)])
                    }
                    className="timeline-range absolute inset-0 w-full"
                  />
                </div>
                <div className="flex justify-between font-mono text-[10px] text-slate-600">
                  <span>2005</span>
                  <span>2011</span>
                  <span>2017</span>
                  <span>2023</span>
                </div>
              </div>

              <div className="max-h-[560px] overflow-y-auto p-4 sm:p-6">
                {TRACKS.filter(([id]) => timelineTracks.includes(id)).map(([id, label, color]) => {
                  const trackEvents = events.filter(({ category }) => category === id);
                  return (
                    <section key={id} className="mb-7 last:mb-0">
                      <div className="mb-3 flex items-center gap-2">
                        <span className="h-2 w-2 rounded-full" style={{ background: color }} />
                        <h3 className="text-xs font-semibold uppercase tracking-wider text-slate-400">{label}</h3>
                        <span className="text-[10px] text-slate-600">{trackEvents.length}</span>
                      </div>
                      {trackEvents.length ? (
                        <div className="grid gap-2 md:grid-cols-2">
                          {trackEvents.map((event, index) => (
                            <button
                              key={`${event.date}-${index}`}
                              onClick={() => setSelectedEvent(event)}
                              className={`rounded-xl border p-3 text-left transition ${
                                selectedEvent === event
                                  ? "border-cyan-300/40 bg-cyan-300/[0.06]"
                                  : "border-slate-800 bg-slate-950/55 hover:border-slate-700"
                              }`}
                            >
                              <time className="font-mono text-[10px]" style={{ color }}>
                                {event.date}
                              </time>
                              <div className="mt-1.5 line-clamp-2 text-xs leading-5 text-slate-300">
                                {clean(event.title)}
                              </div>
                            </button>
                          ))}
                        </div>
                      ) : (
                        <div className="rounded-lg border border-dashed border-slate-800 px-3 py-4 text-xs text-slate-600">
                          No events in the selected range.
                        </div>
                      )}
                    </section>
                  );
                })}
              </div>
            </div>
          ) : (
            <div className="overflow-hidden rounded-2xl border border-slate-800 bg-slate-900/50">
              <div className="flex items-center justify-between border-b border-slate-800 p-5">
                <div>
                  <h2 className="font-medium text-white">Funding relationship graph</h2>
                  <p className="mt-1 text-xs text-slate-500">Drag nodes, zoom, or toggle funding layers.</p>
                </div>
                <span className="font-mono text-xs text-cyan-300">{visibleFlows.length} flows</span>
              </div>
              <div className="h-[580px]">
                {graph.nodes.length ? (
                  <ReactFlow
                    nodes={graph.nodes}
                    edges={graph.edges}
                    fitView
                    minZoom={0.5}
                    maxZoom={1.8}
                    proOptions={{ hideAttribution: true }}
                  >
                    <Background color="#1e293b" gap={24} />
                    <Controls position="bottom-right" />
                  </ReactFlow>
                ) : (
                  <div className="grid h-full place-items-center text-sm text-slate-500">
                    Enable DARPA or Private to display indexed flows.
                  </div>
                )}
              </div>
            </div>
          )}

          {selectedEvent && activePanel === "timeline" && (
            <div className="mt-5 flex flex-col justify-between gap-4 rounded-2xl border border-cyan-300/20 bg-cyan-300/[0.04] p-5 sm:flex-row sm:items-center">
              <div>
                <div className="font-mono text-xs text-cyan-300">{selectedEvent.date}</div>
                <div className="mt-1 text-sm text-slate-200">{clean(selectedEvent.title)}</div>
                <div className="mt-1 text-xs text-slate-500">{selectedEvent.source_document}</div>
              </div>
              <button
                onClick={() => onOpenSource?.(selectedEvent.source_document)}
                className="inline-flex shrink-0 items-center gap-2 text-xs font-medium text-cyan-300 hover:text-cyan-200"
              >
                Open source <ExternalLink size={13} />
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
