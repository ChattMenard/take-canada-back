import React from "react";
import { useEffect, useMemo, useState } from "react";
import {
  ArrowLeft,
  BookOpen,
  Check,
  ChevronRight,
  Download,
  FileArchive,
  FileText,
  Filter,
  Link2,
  Plus,
  Quote,
  Search,
  ShieldCheck,
  Tag,
  X,
} from "lucide-react";
import { api } from "../../api.js";
import { sourceDocuments } from "../../data/sourceDocuments.js";
import { formatBytes, formatDate, shortHash } from "../../lib/format.js";

const normalized = (value = "") => value.toLowerCase().replaceAll("_", " ");
const documentClassification = (item) =>
  item.classification || (item.content_type?.includes("pdf") ? "Primary document" : "Preserved evidence");

function saveBundle(items) {
  const bundle = {
    generated_at: new Date().toISOString(),
    citation_style: "Veritas source bundle v1",
    records: items.map((item) => ({
      title: item.title,
      filename: item.filename,
      source_url: item.source_url || null,
      captured_at: item.captured_at || item.created_at || null,
      sha256: item.sha256,
    })),
  };
  const url = URL.createObjectURL(new Blob([JSON.stringify(bundle, null, 2)], { type: "application/json" }));
  const link = Object.assign(document.createElement("a"), { href: url, download: "veritas-citation-bundle.json" });
  link.click();
  URL.revokeObjectURL(url);
}

export default function SourceVault({ initialQuery = "", onPreserve, online }) {
  const [apiItems, setApiItems] = useState([]);
  const [loading, setLoading] = useState(true);
  const [query, setQuery] = useState(initialQuery);
  const [classification, setClassification] = useState("all");
  const [selected, setSelected] = useState(null);
  const [checked, setChecked] = useState([]);
  const [annotation, setAnnotation] = useState("");
  const [annotations, setAnnotations] = useState([]);

  useEffect(() => {
    setQuery(initialQuery || "");
  }, [initialQuery]);

  useEffect(() => {
    api
      .listEvidence()
      .then(setApiItems)
      .catch(() => setApiItems([]))
      .finally(() => setLoading(false));
  }, []);

  const items = useMemo(() => {
    const existing = new Set(apiItems.map(({ filename }) => filename));
    return [...apiItems, ...sourceDocuments.filter(({ filename }) => !existing.has(filename))];
  }, [apiItems]);
  const classes = useMemo(() => [...new Set(items.map(documentClassification))].sort(), [items]);
  const visible = useMemo(
    () =>
      items.filter((item) => {
        const haystack = normalized(
          `${item.title} ${item.filename} ${item.source_description || ""} ${item.notes || ""}`,
        );
        return (
          haystack.includes(normalized(query)) &&
          (classification === "all" || documentClassification(item) === classification)
        );
      }),
    [items, query, classification],
  );

  async function openDocument(item) {
    if (!item.local && typeof item.id === "number") {
      try {
        setSelected(await api.getEvidence(item.id));
        return;
      } catch (_) {}
    }
    setSelected(item);
  }

  const toggleChecked = (id) =>
    setChecked((current) => (current.includes(id) ? current.filter((item) => item !== id) : [...current, id]));
  const checkedItems = items.filter(({ id }) => checked.includes(id));

  if (selected) {
    return (
      <DocumentReader
        document={selected}
        annotations={annotations.filter(({ documentId }) => documentId === selected.id)}
        annotation={annotation}
        setAnnotation={setAnnotation}
        onAddAnnotation={() => {
          if (!annotation.trim()) return;
          setAnnotations((current) => [
            ...current,
            { documentId: selected.id, text: annotation.trim(), at: new Date().toISOString() },
          ]);
          setAnnotation("");
        }}
        onBack={() => setSelected(null)}
      />
    );
  }

  return (
    <div className="min-h-full bg-[#07101d]">
      <div className="border-b border-slate-800 bg-slate-950/25">
        <div className="mx-auto max-w-[1600px] px-4 py-9 sm:px-6 lg:py-12">
          <div className="flex flex-col justify-between gap-6 lg:flex-row lg:items-end">
            <div>
              <div className="text-xs font-semibold uppercase tracking-[0.18em] text-cyan-300">Tier 03 / Sources</div>
              <h1 className="mt-2 text-3xl font-semibold tracking-tight text-white">Source vault</h1>
              <p className="mt-2 max-w-2xl text-sm leading-6 text-slate-400">
                Search preserved evidence and indexed research documents. Hashes, capture dates and citations stay
                attached to every record.
              </p>
            </div>
            <div className="flex flex-wrap gap-2">
              {checkedItems.length > 0 && (
                <button onClick={() => saveBundle(checkedItems)} className="module-action">
                  <Quote size={14} /> Export {checkedItems.length} citation{checkedItems.length === 1 ? "" : "s"}
                </button>
              )}
              <button
                onClick={onPreserve}
                className="inline-flex items-center gap-2 rounded-lg bg-cyan-300 px-3.5 py-2 text-xs font-semibold text-slate-950 hover:bg-cyan-200"
              >
                <Plus size={14} /> Preserve evidence
              </button>
            </div>
          </div>

          <div className="mt-8 grid gap-3 md:grid-cols-[1fr_240px]">
            <label className="relative block">
              <Search
                size={17}
                className="pointer-events-none absolute left-4 top-1/2 -translate-y-1/2 text-slate-500"
              />
              <input
                autoFocus={Boolean(initialQuery)}
                value={query}
                onChange={(event) => setQuery(event.target.value)}
                placeholder="Search titles, filenames, sources and notes"
                className="h-12 w-full rounded-xl border border-slate-700 bg-slate-900/80 pl-11 pr-10 text-sm text-white outline-none transition placeholder:text-slate-600 focus:border-cyan-300/60 focus:ring-2 focus:ring-cyan-300/10"
              />
              {query && (
                <button
                  onClick={() => setQuery("")}
                  aria-label="Clear search"
                  className="absolute right-3 top-1/2 -translate-y-1/2 rounded p-1 text-slate-500 hover:text-white"
                >
                  <X size={15} />
                </button>
              )}
            </label>
            <label className="relative">
              <Filter
                size={15}
                className="pointer-events-none absolute left-4 top-1/2 -translate-y-1/2 text-slate-500"
              />
              <select
                value={classification}
                onChange={(event) => setClassification(event.target.value)}
                className="h-12 w-full appearance-none rounded-xl border border-slate-700 bg-slate-900/80 pl-10 pr-4 text-sm text-slate-300 outline-none focus:border-cyan-300/60"
              >
                <option value="all">All classifications</option>
                {classes.map((item) => (
                  <option key={item}>{item}</option>
                ))}
              </select>
            </label>
          </div>
        </div>
      </div>

      <div className="mx-auto max-w-[1600px] px-4 py-8 sm:px-6">
        <div className="mb-5 flex items-center justify-between text-xs">
          <span className="text-slate-500">
            {loading ? "Checking archive…" : `${visible.length} source${visible.length === 1 ? "" : "s"}`}
          </span>
          <span className="flex items-center gap-2 text-slate-500">
            <span className={`h-1.5 w-1.5 rounded-full ${online ? "bg-emerald-400" : "bg-amber-400"}`} />
            {apiItems.length ? `${apiItems.length} preserved objects` : "Signed local index"}
          </span>
        </div>

        {visible.length ? (
          <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-3 2xl:grid-cols-4">
            {visible.map((item) => (
              <DocumentCard
                key={item.id}
                item={item}
                checked={checked.includes(item.id)}
                onCheck={() => toggleChecked(item.id)}
                onOpen={() => openDocument(item)}
              />
            ))}
          </div>
        ) : (
          <div className="rounded-2xl border border-dashed border-slate-700 py-20 text-center">
            <FileArchive className="mx-auto text-slate-700" size={36} />
            <h2 className="mt-4 text-sm font-medium text-slate-300">No sources match this view</h2>
            <button
              onClick={() => {
                setQuery("");
                setClassification("all");
              }}
              className="mt-3 text-xs text-cyan-300 hover:text-cyan-200"
            >
              Clear filters
            </button>
          </div>
        )}
      </div>
    </div>
  );
}

function DocumentCard({ item, checked, onCheck, onOpen }) {
  return (
    <article className="group overflow-hidden rounded-2xl border border-slate-800 bg-slate-900/55 transition hover:-translate-y-0.5 hover:border-slate-700 hover:shadow-xl">
      <div className="relative grid h-32 place-items-center border-b border-slate-800 bg-slate-950/60">
        <div className="document-lines absolute inset-5 opacity-50" />
        <FileText size={30} className="relative text-slate-600 transition group-hover:text-cyan-300" />
        <button
          onClick={onCheck}
          aria-label={`${checked ? "Remove" : "Add"} ${item.title} ${checked ? "from" : "to"} citation bundle`}
          className={`absolute right-3 top-3 grid h-7 w-7 place-items-center rounded-lg border transition ${
            checked
              ? "border-cyan-300/50 bg-cyan-300 text-slate-950"
              : "border-slate-700 bg-slate-900 text-transparent hover:text-slate-500"
          }`}
        >
          <Check size={14} />
        </button>
        <span className="absolute bottom-3 left-3 rounded-md border border-slate-700 bg-slate-900/90 px-2 py-1 text-[9px] font-semibold uppercase tracking-wider text-slate-400">
          {item.content_type?.split("/").pop() || "document"}
        </span>
      </div>
      <button onClick={onOpen} className="block w-full p-4 text-left">
        <div className="flex items-center gap-1.5 text-[10px] font-medium uppercase tracking-wider text-cyan-300">
          <ShieldCheck size={12} /> {documentClassification(item)}
        </div>
        <h2 className="mt-3 line-clamp-2 min-h-10 text-sm font-medium leading-5 text-slate-100">{item.title}</h2>
        <p className="mt-2 line-clamp-2 min-h-10 text-xs leading-5 text-slate-500">
          {item.source_description || item.notes || item.filename}
        </p>
        <div className="mt-5 flex items-center justify-between border-t border-slate-800 pt-3 text-[10px] text-slate-600">
          <span>{formatDate(item.captured_at || item.created_at)}</span>
          <span className="flex items-center gap-1">
            <Link2 size={11} /> {item.crossReferences ?? 0} links
          </span>
          <ChevronRight size={13} className="transition group-hover:translate-x-0.5 group-hover:text-cyan-300" />
        </div>
      </button>
    </article>
  );
}

function DocumentReader({
  document,
  annotation,
  setAnnotation,
  annotations,
  onAddAnnotation,
  onBack,
}) {
  const description = document.source_description || document.notes || "No extracted preview is available for this record.";

  return (
    <div className="flex min-h-[calc(100vh-64px)] flex-col bg-[#07101d]">
      <header className="flex flex-col gap-4 border-b border-slate-800 bg-slate-950/35 px-4 py-4 sm:flex-row sm:items-center sm:px-6">
        <button onClick={onBack} className="module-action self-start">
          <ArrowLeft size={14} /> Back to vault
        </button>
        <div className="min-w-0 sm:ml-2">
          <h1 className="truncate text-sm font-medium text-white">{document.title}</h1>
          <p className="mt-0.5 truncate text-xs text-slate-500">{document.filename}</p>
        </div>
        <div className="flex gap-2 sm:ml-auto">
          {!document.local && typeof document.id === "number" && (
            <a href={api.downloadUrl(document.id)} className="module-action">
              <Download size={14} /> Download
            </a>
          )}
          <span className="inline-flex items-center gap-2 rounded-lg border border-emerald-400/20 bg-emerald-400/[0.06] px-3 py-2 text-xs text-emerald-300">
            <ShieldCheck size={14} /> Manifest indexed
          </span>
        </div>
      </header>

      <div className="grid flex-1 lg:grid-cols-[minmax(0,1fr)_360px]">
        <main className="border-b border-slate-800 p-4 sm:p-8 lg:border-b-0 lg:border-r">
          <div className="mx-auto max-w-3xl rounded-sm bg-[#f3f0e8] px-7 py-10 text-slate-900 shadow-2xl sm:px-12 sm:py-14">
            <div className="border-b border-slate-300 pb-7">
              <div className="text-[10px] font-semibold uppercase tracking-[0.2em] text-slate-500">
                Indexed evidence document
              </div>
              <h2 className="mt-4 text-2xl font-semibold leading-tight">{document.title}</h2>
              <div className="mt-4 flex flex-wrap gap-x-5 gap-y-2 text-xs text-slate-500">
                <span>{document.filename}</span>
                <span>{formatDate(document.captured_at || document.created_at)}</span>
              </div>
            </div>
            <div className="py-8">
              <div className="mb-4 text-xs font-semibold uppercase tracking-wider text-slate-500">Archive summary</div>
              <p className="text-base leading-8">{description}</p>
              {document.local && (
                <div className="mt-8 border-l-2 border-amber-500 bg-amber-50 px-4 py-3 text-sm leading-6 text-amber-950">
                  This is an index preview. Open the repository source file for full context before citing a passage.
                </div>
              )}
              <div className="mt-10 grid gap-3 border-t border-slate-300 pt-7 sm:grid-cols-2">
                <div>
                  <div className="text-[10px] uppercase tracking-wider text-slate-500">Classification</div>
                  <div className="mt-1 text-sm font-medium">{documentClassification(document)}</div>
                </div>
                <div>
                  <div className="text-[10px] uppercase tracking-wider text-slate-500">Content type</div>
                  <div className="mt-1 text-sm font-medium">{document.content_type}</div>
                </div>
              </div>
            </div>
          </div>
        </main>

        <aside className="bg-slate-950/30 p-5 sm:p-6">
          <section>
            <div className="flex items-center gap-2 text-xs font-semibold uppercase tracking-[0.14em] text-slate-400">
              <BookOpen size={14} /> Evidence context
            </div>
            <dl className="mt-4 space-y-4 rounded-xl border border-slate-800 bg-slate-900/55 p-4">
              <Metadata label="SHA-256" value={shortHash(document.sha256, 18)} mono />
              <Metadata label="Captured" value={formatDate(document.captured_at || document.created_at)} />
              <Metadata label="Size" value={document.size_bytes ? formatBytes(document.size_bytes) : "Manifest index"} />
              <Metadata label="Cross-references" value={`${document.crossReferences ?? 0} linked records`} />
            </dl>
          </section>

          <section className="mt-8">
            <div className="flex items-center gap-2 text-xs font-semibold uppercase tracking-[0.14em] text-slate-400">
              <Tag size={14} /> Annotations
            </div>
            <textarea
              value={annotation}
              onChange={(event) => setAnnotation(event.target.value)}
              placeholder="Add a private review note…"
              className="mt-4 min-h-24 w-full resize-y rounded-xl border border-slate-700 bg-slate-900 p-3 text-xs leading-5 text-slate-200 outline-none placeholder:text-slate-600 focus:border-cyan-300/50"
            />
            <button
              onClick={onAddAnnotation}
              disabled={!annotation.trim()}
              className="mt-2 w-full rounded-lg bg-slate-800 px-3 py-2 text-xs font-medium text-slate-200 hover:bg-slate-700 disabled:cursor-not-allowed disabled:opacity-40"
            >
              Save annotation
            </button>
            <div className="mt-4 space-y-2">
              {annotations.map((item, index) => (
                <div key={`${item.at}-${index}`} className="rounded-lg border border-slate-800 bg-slate-900/55 p-3">
                  <p className="text-xs leading-5 text-slate-300">{item.text}</p>
                  <time className="mt-2 block text-[9px] text-slate-600">{formatDate(item.at)}</time>
                </div>
              ))}
            </div>
          </section>
        </aside>
      </div>
    </div>
  );
}

function Metadata({ label, value, mono }) {
  return (
    <div>
      <dt className="text-[9px] font-semibold uppercase tracking-wider text-slate-600">{label}</dt>
      <dd className={`mt-1 break-all text-xs text-slate-300 ${mono ? "font-mono" : ""}`}>{value}</dd>
    </div>
  );
}
