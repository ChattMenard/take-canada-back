import { useEffect, useState } from "react";
import {
  ShieldCheck,
  ShieldAlert,
  Download,
  Loader2,
  Link as LinkIcon,
  Clock,
  FileText,
  CheckCircle2,
  AlertTriangle,
  Eye,
  Pencil,
  FileDown,
  Stamp,
  RefreshCw,
  ExternalLink,
} from "lucide-react";
import { api } from "../api.js";
import { formatBytes, formatDate, shortHash } from "../lib/format.js";
import EntitiesPanel from "./EntitiesPanel.jsx";
import RelationshipsPanel from "./RelationshipsPanel.jsx";
import TimelinePanel from "./TimelinePanel.jsx";

const ACTION_META = {
  CREATED: { icon: FileText, color: "text-emerald-400" },
  ACCESSED: { icon: Eye, color: "text-zinc-400" },
  VERIFIED: { icon: CheckCircle2, color: "text-emerald-400" },
  VERIFY_FAILED: { icon: AlertTriangle, color: "text-red-400" },
  EXPORTED: { icon: FileDown, color: "text-blue-400" },
  ANNOTATED: { icon: Pencil, color: "text-amber-400" },
  LINKED: { icon: LinkIcon, color: "text-purple-400" },
};

export default function EvidenceDetail({ evidence, onUpdated }) {
  const [verifying, setVerifying] = useState(false);
  const [verifyResult, setVerifyResult] = useState(null);
  const [note, setNote] = useState("");
  const [actor, setActor] = useState("");
  const [activeTab, setActiveTab] = useState("entities");

  const [tsStatus, setTsStatus] = useState(null);
  const [tsWorking, setTsWorking] = useState(false);
  const [tsVerifyResult, setTsVerifyResult] = useState(null);

  useEffect(() => {
    let cancelled = false;
    api.timestampStatus(evidence.id)
      .then((s) => { if (!cancelled) setTsStatus(s); })
      .catch(() => { if (!cancelled) setTsStatus(null); });
    return () => { cancelled = true; };
  }, [evidence.id]);

  async function verify() {
    setVerifying(true);
    setVerifyResult(null);
    try {
      const res = await api.verify(evidence.id);
      setVerifyResult(res);
      const fresh = await api.getEvidence(evidence.id);
      onUpdated(fresh);
    } finally {
      setVerifying(false);
    }
  }

  async function createTimestamp() {
    setTsWorking(true);
    setTsVerifyResult(null);
    try {
      await api.createTimestamp(evidence.id);
      const s = await api.timestampStatus(evidence.id);
      setTsStatus(s);
      const fresh = await api.getEvidence(evidence.id);
      onUpdated(fresh);
    } catch (e) {
      alert(e.message);
    } finally {
      setTsWorking(false);
    }
  }

  async function upgradeTimestamp() {
    setTsWorking(true);
    setTsVerifyResult(null);
    try {
      await api.upgradeTimestamp(evidence.id);
      const s = await api.timestampStatus(evidence.id);
      setTsStatus(s);
      const fresh = await api.getEvidence(evidence.id);
      onUpdated(fresh);
    } catch (e) {
      alert(e.message);
    } finally {
      setTsWorking(false);
    }
  }

  async function verifyTimestamp() {
    setTsWorking(true);
    setTsVerifyResult(null);
    try {
      const res = await api.verifyTimestamp(evidence.id);
      setTsVerifyResult(res);
      const fresh = await api.getEvidence(evidence.id);
      onUpdated(fresh);
    } catch (e) {
      alert(e.message);
    } finally {
      setTsWorking(false);
    }
  }

  async function submitNote(e) {
    e.preventDefault();
    if (!note.trim()) return;
    await api.addNote(evidence.id, { actor: actor || null, detail: note });
    setNote("");
    const fresh = await api.getEvidence(evidence.id);
    onUpdated(fresh);
  }

  return (
    <div className="flex h-full flex-col">
      <div className="border-b border-zinc-800 p-6">
        <div className="flex items-start justify-between gap-4">
          <div className="min-w-0">
            <h2 className="truncate text-xl font-semibold text-zinc-100">{evidence.title}</h2>
            <p className="mt-1 truncate text-sm text-zinc-500">{evidence.filename}</p>
          </div>
          <div className="flex shrink-0 gap-2">
            <button
              onClick={verify}
              disabled={verifying}
              className="flex items-center gap-2 rounded-lg border border-zinc-700 px-3 py-2 text-sm text-zinc-200 hover:bg-zinc-800 disabled:opacity-50"
            >
              {verifying ? <Loader2 size={16} className="animate-spin" /> : <ShieldCheck size={16} />}
              Verify integrity
            </button>
            <a
              href={api.downloadUrl(evidence.id)}
              className="flex items-center gap-2 rounded-lg bg-zinc-800 px-3 py-2 text-sm text-zinc-100 hover:bg-zinc-700"
            >
              <Download size={16} />
              Download
            </a>
          </div>

          <div className="flex shrink-0 gap-2">
            {tsStatus?.timestamped ? (
              <>
                <a
                  href={api.timestampFileUrl(evidence.id)}
                  className="flex items-center gap-2 rounded-lg border border-zinc-700 px-3 py-2 text-sm text-zinc-200 hover:bg-zinc-800"
                >
                  <ExternalLink size={16} />
                  .ots
                </a>
                <button
                  onClick={upgradeTimestamp}
                  disabled={tsWorking}
                  className="flex items-center gap-2 rounded-lg border border-zinc-700 px-3 py-2 text-sm text-zinc-200 hover:bg-zinc-800 disabled:opacity-50"
                >
                  {tsWorking ? <Loader2 size={16} className="animate-spin" /> : <RefreshCw size={16} />}
                  Upgrade
                </button>
                <button
                  onClick={verifyTimestamp}
                  disabled={tsWorking}
                  className="flex items-center gap-2 rounded-lg border border-zinc-700 px-3 py-2 text-sm text-zinc-200 hover:bg-zinc-800 disabled:opacity-50"
                >
                  {tsWorking ? <Loader2 size={16} className="animate-spin" /> : <Stamp size={16} />}
                  Verify timestamp
                </button>
              </>
            ) : (
              <button
                onClick={createTimestamp}
                disabled={tsWorking}
                className="flex items-center gap-2 rounded-lg border border-zinc-700 px-3 py-2 text-sm text-zinc-200 hover:bg-zinc-800 disabled:opacity-50"
              >
                {tsWorking ? <Loader2 size={16} className="animate-spin" /> : <Stamp size={16} />}
                Create timestamp
              </button>
            )}
          </div>
        </div>

        {verifyResult && (
          <div
            className={`mt-4 flex items-center gap-2 rounded-lg border px-3 py-2 text-sm ${
              verifyResult.intact
                ? "border-emerald-700 bg-emerald-500/10 text-emerald-300"
                : "border-red-700 bg-red-500/10 text-red-300"
            }`}
          >
            {verifyResult.intact ? <ShieldCheck size={16} /> : <ShieldAlert size={16} />}
            {verifyResult.message}
          </div>
        )}

        {tsVerifyResult && (
          <div
            className={`mt-4 flex items-center gap-2 rounded-lg border px-3 py-2 text-sm ${
              tsVerifyResult.verified
                ? "border-emerald-700 bg-emerald-500/10 text-emerald-300"
                : tsVerifyResult.pending
                ? "border-amber-700 bg-amber-500/10 text-amber-300"
                : "border-red-700 bg-red-500/10 text-red-300"
            }`}
          >
            {tsVerifyResult.verified ? (
              <CheckCircle2 size={16} />
            ) : tsVerifyResult.pending ? (
              <Loader2 size={16} className="animate-spin" />
            ) : (
              <AlertTriangle size={16} />
            )}
            {tsVerifyResult.verified
              ? `OpenTimestamps verified at block ${tsVerifyResult.block_height}.`
              : tsVerifyResult.pending
              ? `OpenTimestamps pending${tsVerifyResult.error ? `: ${tsVerifyResult.error}` : ""}.`
              : `OpenTimestamps verification failed${tsVerifyResult.error ? `: ${tsVerifyResult.error}` : ""}.`}
          </div>
        )}
      </div>

      <div className="grid flex-1 grid-cols-1 gap-6 overflow-y-auto p-6 lg:grid-cols-3">
        <section>
          <h3 className="mb-3 text-xs font-semibold uppercase tracking-wider text-zinc-500">
            Provenance
          </h3>
          <dl className="space-y-3 text-sm">
            <Row label="SHA-256">
              <code className="break-all font-mono text-xs text-emerald-300">{evidence.sha256}</code>
            </Row>
            <Row label="Size">{formatBytes(evidence.size_bytes)}</Row>
            <Row label="Type">{evidence.content_type}</Row>
            <Row label="Source">
              {evidence.source_url ? (
                <a
                  href={evidence.source_url}
                  target="_blank"
                  rel="noreferrer"
                  className="inline-flex items-center gap-1 text-blue-400 hover:underline"
                >
                  <LinkIcon size={13} /> {evidence.source_url}
                </a>
              ) : (
                "—"
              )}
            </Row>
            <Row label="Description">{evidence.source_description || "—"}</Row>
            <Row label="Captured">{formatDate(evidence.captured_at)}</Row>
            <Row label="Collected by">{evidence.collected_by || "—"}</Row>
            <Row label="Ingested">{formatDate(evidence.created_at)}</Row>
            <Row label="Timestamp">
              {tsStatus ? (
                tsStatus.timestamped ? (
                  <span className="inline-flex items-center gap-1 text-emerald-400">
                    <CheckCircle2 size={13} /> OpenTimestamps signature present
                  </span>
                ) : (
                  <span className="text-zinc-500">Not timestamped</span>
                )
              ) : (
                <span className="text-zinc-500">—</span>
              )}
            </Row>
            <Row label="Notes">{evidence.notes || "—"}</Row>
          </dl>
        </section>

        <section className="flex flex-col">
          <h3 className="mb-3 text-xs font-semibold uppercase tracking-wider text-zinc-500">
            Chain of custody
          </h3>
          <ol className="relative space-y-4 border-l border-zinc-800 pl-5">
            {(evidence.custody_events || []).map((ev) => {
              const meta = ACTION_META[ev.action] || ACTION_META.ACCESSED;
              const Icon = meta.icon;
              return (
                <li key={ev.id} className="relative">
                  <span className="absolute -left-[27px] flex h-5 w-5 items-center justify-center rounded-full bg-zinc-950">
                    <Icon size={15} className={meta.color} />
                  </span>
                  <div className="flex items-center gap-2">
                    <span className={`text-sm font-medium ${meta.color}`}>{ev.action}</span>
                    {ev.actor && <span className="text-xs text-zinc-500">· {ev.actor}</span>}
                  </div>
                  {ev.detail && <p className="text-sm text-zinc-300">{ev.detail}</p>}
                  <p className="flex items-center gap-1 text-xs text-zinc-600">
                    <Clock size={11} /> {formatDate(ev.timestamp)}
                    {ev.hash_at_event && <span className="font-mono">· {shortHash(ev.hash_at_event)}</span>}
                  </p>
                </li>
              );
            })}
          </ol>

          <form onSubmit={submitNote} className="mt-5 space-y-2">
            <input
              value={actor}
              onChange={(e) => setActor(e.target.value)}
              placeholder="Actor (optional)"
              className="w-full rounded-lg border border-zinc-700 bg-zinc-900 px-3 py-2 text-sm text-zinc-100 outline-none focus:border-emerald-500"
            />
            <div className="flex gap-2">
              <input
                value={note}
                onChange={(e) => setNote(e.target.value)}
                placeholder="Add a custody note…"
                className="flex-1 rounded-lg border border-zinc-700 bg-zinc-900 px-3 py-2 text-sm text-zinc-100 outline-none focus:border-emerald-500"
              />
              <button
                type="submit"
                className="rounded-lg bg-zinc-800 px-4 text-sm text-zinc-100 hover:bg-zinc-700"
              >
                Log
              </button>
            </div>
          </form>
        </section>

        <section>
          <div className="mb-3 flex gap-2 border-b border-zinc-800">
            <button
              onClick={() => setActiveTab("entities")}
              className={`px-3 py-1.5 text-sm font-medium transition-colors ${
                activeTab === "entities"
                  ? "border-b-2 border-emerald-500 text-emerald-400"
                  : "text-zinc-500 hover:text-zinc-300"
              }`}
            >
              Entities
            </button>
            <button
              onClick={() => setActiveTab("relationships")}
              className={`px-3 py-1.5 text-sm font-medium transition-colors ${
                activeTab === "relationships"
                  ? "border-b-2 border-emerald-500 text-emerald-400"
                  : "text-zinc-500 hover:text-zinc-300"
              }`}
            >
              Relationships
            </button>
            <button
              onClick={() => setActiveTab("timeline")}
              className={`px-3 py-1.5 text-sm font-medium transition-colors ${
                activeTab === "timeline"
                  ? "border-b-2 border-emerald-500 text-emerald-400"
                  : "text-zinc-500 hover:text-zinc-300"
              }`}
            >
              Timeline
            </button>
          </div>
          {activeTab === "entities" && (
            <EntitiesPanel evidenceId={evidence.id} onLinked={() => onUpdated(evidence)} />
          )}
          {activeTab === "relationships" && (
            <RelationshipsPanel evidenceId={evidence.id} onLinked={() => onUpdated(evidence)} />
          )}
          {activeTab === "timeline" && (
            <TimelinePanel evidenceId={evidence.id} onLinked={() => onUpdated(evidence)} />
          )}
        </section>
      </div>
    </div>
  );
}

function Row({ label, children }) {
  return (
    <div className="grid grid-cols-[110px_1fr] gap-2">
      <dt className="text-zinc-500">{label}</dt>
      <dd className="text-zinc-200">{children}</dd>
    </div>
  );
}
