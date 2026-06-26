import { useRef, useState } from "react";
import { UploadCloud, Loader2, X, Link2, FileUp, List, CheckCircle2, AlertCircle } from "lucide-react";
import { api } from "../api.js";

const empty = {
  title: "",
  source_url: "",
  source_description: "",
  captured_at: "",
  collected_by: "",
  notes: "",
};

export default function IngestForm({ onClose, onIngested }) {
  const [mode, setMode] = useState("file");
  const [file, setFile] = useState(null);
  const [url, setUrl] = useState("");
  const [batchUrls, setBatchUrls] = useState("");
  const [batchResults, setBatchResults] = useState(null);
  const [meta, setMeta] = useState(empty);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState(null);
  const [drag, setDrag] = useState(false);
  const inputRef = useRef(null);

  const set = (k) => (e) => setMeta((m) => ({ ...m, [k]: e.target.value }));

  async function submit(e) {
    e.preventDefault();
    setError(null);
    if (mode === "file" && !file) {
      setError("Select a file to preserve.");
      return;
    }
    if (mode === "url" && !url.trim()) {
      setError("Enter a URL to collect.");
      return;
    }
    if (mode === "batch") {
      const lines = batchUrls.split("\n").map((l) => l.trim()).filter(Boolean);
      if (!lines.length) { setError("Enter at least one URL."); return; }
      setBusy(true);
      setBatchResults(null);
      try {
        const results = await api.batchCollect(
          lines.map((url) => ({
            url,
            collected_by: meta.collected_by || undefined,
            notes: meta.notes || undefined,
          }))
        );
        setBatchResults(results);
        const ok = results.filter((r) => r.success);
        if (ok.length > 0) onIngested(null);
      } catch (err) {
        setError(err.message);
      } finally {
        setBusy(false);
      }
      return;
    }
    setBusy(true);
    try {
      let created;
      if (mode === "url") {
        const payload = { url: url.trim() };
        Object.entries(meta).forEach(([k, v]) => {
          if (v && k !== "source_url") payload[k] = v;
        });
        created = await api.collectUrl(payload);
      } else {
        const fd = new FormData();
        fd.append("file", file);
        Object.entries(meta).forEach(([k, v]) => v && fd.append(k, v));
        created = await api.ingest(fd);
      }
      onIngested(created);
    } catch (err) {
      setError(err.message);
    } finally {
      setBusy(false);
    }
  }

  const tabClass = (m) =>
    `flex items-center gap-2 rounded-lg px-3 py-2 text-sm font-medium transition ${
      mode === m ? "bg-zinc-800 text-zinc-100" : "text-zinc-500 hover:text-zinc-300"
    }`;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 p-4">
      <form
        onSubmit={submit}
        className="w-full max-w-2xl max-h-[90vh] overflow-y-auto rounded-2xl border border-zinc-800 bg-zinc-950 p-6 shadow-2xl"
      >
        <div className="mb-4 flex items-center justify-between">
          <h2 className="text-lg font-semibold text-zinc-100">Preserve new evidence</h2>
          <button type="button" onClick={onClose} className="text-zinc-500 hover:text-zinc-200">
            <X size={20} />
          </button>
        </div>

        <div className="mb-5 flex gap-1 rounded-lg bg-zinc-900 p-1">
          <button type="button" className={tabClass("file")} onClick={() => setMode("file")}>
            <FileUp size={15} /> Upload file
          </button>
          <button type="button" className={tabClass("url")} onClick={() => setMode("url")}>
            <Link2 size={15} /> From URL
          </button>
          <button type="button" className={tabClass("batch")} onClick={() => setMode("batch")}>
            <List size={15} /> Batch URLs
          </button>
        </div>

        {mode === "file" && (
          <div
            onDragOver={(e) => { e.preventDefault(); setDrag(true); }}
            onDragLeave={() => setDrag(false)}
            onDrop={(e) => { e.preventDefault(); setDrag(false); if (e.dataTransfer.files[0]) setFile(e.dataTransfer.files[0]); }}
            onClick={() => inputRef.current?.click()}
            className={`mb-5 flex cursor-pointer flex-col items-center justify-center rounded-xl border-2 border-dashed p-8 text-center transition ${
              drag ? "border-emerald-500 bg-emerald-500/5" : "border-zinc-700 hover:border-zinc-500"
            }`}
          >
            <UploadCloud className="mb-2 text-zinc-400" size={32} />
            {file ? (
              <p className="text-sm text-zinc-200">
                <span className="font-medium">{file.name}</span> ({(file.size / 1024).toFixed(1)} KB)
              </p>
            ) : (
              <p className="text-sm text-zinc-400">
                Drag a document here, or <span className="text-emerald-400">browse</span>. It is hashed with SHA-256 on arrival.
              </p>
            )}
            <input ref={inputRef} type="file" className="hidden" onChange={(e) => setFile(e.target.files[0] || null)} />
          </div>
        )}

        {mode === "url" && (
          <div className="mb-5">
            <label className="mb-1 block text-xs font-medium uppercase tracking-wide text-zinc-500">
              URL to collect
            </label>
            <div className="relative">
              <Link2 size={15} className="absolute left-3 top-1/2 -translate-y-1/2 text-zinc-500" />
              <input
                value={url}
                onChange={(e) => setUrl(e.target.value)}
                placeholder="https://example.gov/report.pdf"
                className="w-full rounded-lg border border-zinc-700 bg-zinc-900 py-2 pl-9 pr-3 text-sm text-zinc-100 outline-none focus:border-emerald-500"
              />
            </div>
            <p className="mt-2 text-xs text-zinc-500">
              Veritas fetches the page server-side, hashes it with SHA-256, and records the source URL, HTTP status, and retrieval time in the chain of custody.
            </p>
          </div>
        )}

        {mode !== "batch" && (
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
            <Field label="Title" value={meta.title} onChange={set("title")} placeholder="Descriptive title" />
            <Field label="Collected by" value={meta.collected_by} onChange={set("collected_by")} placeholder="Your name / handle" />
            {mode === "file" && (
              <Field label="Source URL" value={meta.source_url} onChange={set("source_url")} placeholder="https://…" className="sm:col-span-2" />
            )}
            <Field
              label="Captured at"
              type="datetime-local"
              value={meta.captured_at}
              onChange={set("captured_at")}
            />
            <Field label="Source description" value={meta.source_description} onChange={set("source_description")} placeholder="Where it came from" />
            <div className="sm:col-span-2">
              <label className="mb-1 block text-xs font-medium uppercase tracking-wide text-zinc-500">Notes</label>
              <textarea
                value={meta.notes}
                onChange={set("notes")}
                rows={3}
                placeholder="Context, significance, related records…"
                className="w-full rounded-lg border border-zinc-700 bg-zinc-900 px-3 py-2 text-sm text-zinc-100 outline-none focus:border-emerald-500"
              />
            </div>
          </div>
        )}

        {mode === "batch" && (
          <div className="mb-5">
            <label className="mb-1 block text-xs font-medium uppercase tracking-wide text-zinc-500">
              URLs to collect (one per line)
            </label>
            <textarea
              value={batchUrls}
              onChange={(e) => setBatchUrls(e.target.value)}
              rows={6}
              placeholder="https://example.gov/report1.pdf\nhttps://example.gov/report2.pdf"
              className="w-full resize-y rounded-lg border border-zinc-700 bg-zinc-900 px-3 py-2 font-mono text-xs text-zinc-100 outline-none focus:border-emerald-500"
            />
            <p className="mt-1 text-xs text-zinc-500">
              Each URL is fetched, hashed, and ingested independently. Failed URLs are reported without stopping the batch.
            </p>
            {batchResults && (
              <div className="mt-3 max-h-48 overflow-y-auto space-y-1">
                {batchResults.map((r, i) => (
                  <div key={i} className={`flex items-start gap-2 rounded px-2 py-1.5 text-xs ${
                    r.success ? "bg-emerald-500/10 text-emerald-300" : "bg-red-500/10 text-red-300"
                  }`}>
                    {r.success
                      ? <CheckCircle2 size={13} className="mt-0.5 shrink-0" />
                      : <AlertCircle size={13} className="mt-0.5 shrink-0" />}
                    <span className="truncate">
                      {r.success ? `#${r.evidence_id} ${r.url}` : `${r.url} — ${r.error}`}
                    </span>
                  </div>
                ))}
              </div>
            )}
            <div className="mt-3 grid grid-cols-1 gap-3">
              <div>
                <label className="mb-1 block text-xs font-medium uppercase tracking-wide text-zinc-500">Collected by</label>
                <input
                  value={meta.collected_by}
                  onChange={set("collected_by")}
                  placeholder="Your name / handle"
                  className="w-full rounded-lg border border-zinc-700 bg-zinc-900 px-3 py-2 text-sm text-zinc-100 outline-none focus:border-emerald-500"
                />
              </div>
              <div>
                <label className="mb-1 block text-xs font-medium uppercase tracking-wide text-zinc-500">Notes (applied to all items)</label>
                <textarea
                  value={meta.notes}
                  onChange={set("notes")}
                  rows={2}
                  placeholder="Context, significance, related records…"
                  className="w-full resize-y rounded-lg border border-zinc-700 bg-zinc-900 px-3 py-2 text-sm text-zinc-100 outline-none focus:border-emerald-500"
                />
              </div>
            </div>
          </div>
        )}

        {error && <p className="mt-4 text-sm text-red-400">{error}</p>}

        <div className="mt-6 flex justify-end gap-3">
          <button
            type="button"
            onClick={onClose}
            className="rounded-lg px-4 py-2 text-sm text-zinc-400 hover:text-zinc-200"
          >
            Cancel
          </button>
          <button
            type="submit"
            disabled={busy}
            className="flex items-center gap-2 rounded-lg bg-emerald-600 px-4 py-2 text-sm font-medium text-white hover:bg-emerald-500 disabled:opacity-50"
          >
            {busy && <Loader2 size={16} className="animate-spin" />}
            {mode === "url" ? "Collect & hash" : mode === "batch" ? "Collect all" : "Preserve & hash"}
          </button>
        </div>
      </form>
    </div>
  );
}

function Field({ label, className = "", ...props }) {
  return (
    <div className={className}>
      <label className="mb-1 block text-xs font-medium uppercase tracking-wide text-zinc-500">
        {label}
      </label>
      <input
        {...props}
        className="w-full rounded-lg border border-zinc-700 bg-zinc-900 px-3 py-2 text-sm text-zinc-100 outline-none focus:border-emerald-500"
      />
    </div>
  );
}
