import { useRef, useState } from "react";
import { UploadCloud, Loader2, X, Link2, FileUp } from "lucide-react";
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
        </div>

        {mode === "file" ? (
          <div
            onDragOver={(e) => {
              e.preventDefault();
              setDrag(true);
            }}
            onDragLeave={() => setDrag(false)}
            onDrop={(e) => {
              e.preventDefault();
              setDrag(false);
              if (e.dataTransfer.files[0]) setFile(e.dataTransfer.files[0]);
            }}
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
                Drag a document here, or <span className="text-emerald-400">browse</span>. It is
                hashed with SHA-256 on arrival.
              </p>
            )}
            <input
              ref={inputRef}
              type="file"
              className="hidden"
              onChange={(e) => setFile(e.target.files[0] || null)}
            />
          </div>
        ) : (
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
              Veritas fetches the page server-side, hashes it with SHA-256, and records the source
              URL, HTTP status, and retrieval time in the chain of custody.
            </p>
          </div>
        )}

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
            {mode === "url" ? "Collect & hash" : "Preserve & hash"}
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
