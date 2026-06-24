import { useState, useEffect } from "react";
import {
  Plus, Trash2, DollarSign, ArrowRightLeft, ArrowUpRight,
  User, Building, Link as LinkIcon, FileText, Calendar, X, Search, Loader2,
} from "lucide-react";
import { api } from "../api.js";
import { formatDate } from "../lib/format.js";

const KIND_ICONS = {
  DONATION:   { icon: DollarSign,    color: "text-emerald-400" },
  CONTRACT:   { icon: FileText,      color: "text-blue-400" },
  BOARD_SEAT: { icon: Building,      color: "text-purple-400" },
  OWNERSHIP:  { icon: ArrowUpRight,  color: "text-amber-400" },
  LOBBYING:   { icon: ArrowRightLeft,color: "text-pink-400" },
  EMPLOYMENT: { icon: User,          color: "text-cyan-400" },
  OTHER:      { icon: LinkIcon,      color: "text-zinc-400" },
};

const KIND_LABELS = {
  DONATION:   "Donation",
  CONTRACT:   "Contract",
  BOARD_SEAT: "Board Seat",
  OWNERSHIP:  "Ownership",
  LOBBYING:   "Lobbying",
  EMPLOYMENT: "Employment",
  OTHER:      "Other",
};

export default function RelationshipsView() {
  const [relationships, setRelationships] = useState([]);
  const [entities, setEntities] = useState([]);
  const [query, setQuery] = useState("");
  const [loading, setLoading] = useState(true);
  const [showCreate, setShowCreate] = useState(false);
  const [form, setForm] = useState({
    source_entity_id: "", target_entity_id: "", kind: "OTHER",
    description: "", amount: "", occurred_at: "",
  });

  useEffect(() => {
    load();
  }, []);

  async function load() {
    setLoading(true);
    try {
      const [rels, ents] = await Promise.all([api.listRelationships(), api.listEntities()]);
      setRelationships(rels);
      setEntities(ents);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  }

  async function create(e) {
    e.preventDefault();
    try {
      const payload = {
        source_entity_id: Number(form.source_entity_id),
        target_entity_id: Number(form.target_entity_id),
        kind: form.kind,
        description: form.description || null,
        amount: form.amount ? Number(form.amount) : null,
        occurred_at: form.occurred_at ? new Date(form.occurred_at).toISOString() : null,
      };
      await api.createRelationship(payload);
      setForm({ source_entity_id: "", target_entity_id: "", kind: "OTHER", description: "", amount: "", occurred_at: "" });
      setShowCreate(false);
      load();
    } catch (err) {
      alert(err.message);
    }
  }

  async function del(id) {
    if (!confirm("Delete this relationship?")) return;
    await api.deleteRelationship(id);
    load();
  }

  const entityName = (id) => entities.find((e) => e.id === id)?.name ?? "Unknown";

  const filtered = relationships.filter((r) => {
    if (!query) return true;
    const q = query.toLowerCase();
    return (
      entityName(r.source_entity_id).toLowerCase().includes(q) ||
      entityName(r.target_entity_id).toLowerCase().includes(q) ||
      (r.description || "").toLowerCase().includes(q)
    );
  });

  return (
    <div className="flex h-full flex-col overflow-hidden">
      <div className="flex items-center justify-between border-b border-zinc-800 p-4">
        <h2 className="text-sm font-semibold text-zinc-200">Relationships</h2>
        <button
          onClick={() => setShowCreate(true)}
          className="flex items-center gap-1 rounded bg-emerald-600 px-2 py-1 text-xs text-white hover:bg-emerald-500"
        >
          <Plus size={12} /> New
        </button>
      </div>

      <div className="border-b border-zinc-800 p-3">
        <div className="relative">
          <Search size={13} className="absolute left-2.5 top-2.5 text-zinc-500" />
          <input
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Filter by entity or description…"
            className="w-full rounded border border-zinc-700 bg-zinc-900 py-1.5 pl-8 pr-3 text-sm text-zinc-100 outline-none focus:border-emerald-500"
          />
        </div>
      </div>

      {showCreate && (
        <div className="border-b border-zinc-800 bg-zinc-900 p-4">
          <div className="mb-3 flex items-center justify-between">
            <span className="text-xs font-semibold text-zinc-300">New relationship</span>
            <button onClick={() => setShowCreate(false)} className="text-zinc-500 hover:text-zinc-300"><X size={14} /></button>
          </div>
          <form onSubmit={create} className="grid grid-cols-2 gap-3">
            <div>
              <label className="mb-1 block text-xs text-zinc-500">Source entity</label>
              <select value={form.source_entity_id} required onChange={(e) => setForm({ ...form, source_entity_id: e.target.value })}
                className="w-full rounded border border-zinc-700 bg-zinc-950 px-2 py-1.5 text-sm text-zinc-100 outline-none focus:border-emerald-500">
                <option value="">Select…</option>
                {entities.map((e) => <option key={e.id} value={e.id}>{e.name}</option>)}
              </select>
            </div>
            <div>
              <label className="mb-1 block text-xs text-zinc-500">Target entity</label>
              <select value={form.target_entity_id} required onChange={(e) => setForm({ ...form, target_entity_id: e.target.value })}
                className="w-full rounded border border-zinc-700 bg-zinc-950 px-2 py-1.5 text-sm text-zinc-100 outline-none focus:border-emerald-500">
                <option value="">Select…</option>
                {entities.map((e) => <option key={e.id} value={e.id}>{e.name}</option>)}
              </select>
            </div>
            <div>
              <label className="mb-1 block text-xs text-zinc-500">Kind</label>
              <select value={form.kind} onChange={(e) => setForm({ ...form, kind: e.target.value })}
                className="w-full rounded border border-zinc-700 bg-zinc-950 px-2 py-1.5 text-sm text-zinc-100 outline-none focus:border-emerald-500">
                {Object.entries(KIND_LABELS).map(([v, l]) => <option key={v} value={v}>{l}</option>)}
              </select>
            </div>
            <div>
              <label className="mb-1 block text-xs text-zinc-500">Amount (optional)</label>
              <input type="number" value={form.amount} onChange={(e) => setForm({ ...form, amount: e.target.value })}
                placeholder="e.g. 500000"
                className="w-full rounded border border-zinc-700 bg-zinc-950 px-2 py-1.5 text-sm text-zinc-100 outline-none focus:border-emerald-500" />
            </div>
            <div>
              <label className="mb-1 block text-xs text-zinc-500">Occurred at (optional)</label>
              <input type="date" value={form.occurred_at} onChange={(e) => setForm({ ...form, occurred_at: e.target.value })}
                className="w-full rounded border border-zinc-700 bg-zinc-950 px-2 py-1.5 text-sm text-zinc-100 outline-none focus:border-emerald-500" />
            </div>
            <div>
              <label className="mb-1 block text-xs text-zinc-500">Description (optional)</label>
              <input value={form.description} onChange={(e) => setForm({ ...form, description: e.target.value })}
                placeholder="Brief note"
                className="w-full rounded border border-zinc-700 bg-zinc-950 px-2 py-1.5 text-sm text-zinc-100 outline-none focus:border-emerald-500" />
            </div>
            <div className="col-span-2 flex justify-end gap-2">
              <button type="button" onClick={() => setShowCreate(false)} className="rounded px-3 py-1.5 text-sm text-zinc-500 hover:text-zinc-300">Cancel</button>
              <button type="submit" className="rounded bg-emerald-600 px-3 py-1.5 text-sm text-white hover:bg-emerald-500">Create</button>
            </div>
          </form>
        </div>
      )}

      <div className="flex-1 overflow-y-auto p-4">
        {loading ? (
          <div className="flex justify-center py-12 text-zinc-600"><Loader2 className="animate-spin" size={22} /></div>
        ) : filtered.length === 0 ? (
          <p className="py-12 text-center text-sm text-zinc-600">No relationships yet.</p>
        ) : (
          <div className="space-y-2">
            {filtered.map((rel) => {
              const meta = KIND_ICONS[rel.kind] ?? KIND_ICONS.OTHER;
              const Icon = meta.icon;
              return (
                <div key={rel.id} className="rounded-lg border border-zinc-800 bg-zinc-900/50 p-4 hover:border-zinc-700">
                  <div className="flex items-start justify-between gap-3">
                    <div className="flex-1">
                      <div className="flex flex-wrap items-center gap-2 text-sm">
                        <span className="font-medium text-zinc-200">{entityName(rel.source_entity_id)}</span>
                        <Icon size={13} className={meta.color} />
                        <span className={`text-xs font-medium ${meta.color}`}>{KIND_LABELS[rel.kind]}</span>
                        <Icon size={13} className={meta.color} />
                        <span className="font-medium text-zinc-200">{entityName(rel.target_entity_id)}</span>
                      </div>
                      {rel.description && <p className="mt-1 text-xs text-zinc-500">{rel.description}</p>}
                      <div className="mt-1.5 flex flex-wrap gap-3 text-xs text-zinc-600">
                        {rel.amount != null && (
                          <span className="flex items-center gap-1"><DollarSign size={11} />{rel.amount.toLocaleString()}</span>
                        )}
                        {rel.occurred_at && (
                          <span className="flex items-center gap-1"><Calendar size={11} />{formatDate(rel.occurred_at)}</span>
                        )}
                      </div>
                      {rel.linked_evidence?.length > 0 && (
                        <div className="mt-2 flex flex-wrap gap-1">
                          {rel.linked_evidence.map((le) => (
                            <span key={le.id} className="inline-flex items-center gap-1 rounded bg-zinc-800 px-1.5 py-0.5 text-xs text-zinc-400">
                              <FileText size={10} />{le.title.length > 24 ? le.title.slice(0, 24) + "…" : le.title}
                            </span>
                          ))}
                        </div>
                      )}
                    </div>
                    <button onClick={() => del(rel.id)} className="rounded p-1.5 text-zinc-600 hover:bg-red-500/10 hover:text-red-400">
                      <Trash2 size={14} />
                    </button>
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
}
