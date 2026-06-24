import { useState, useEffect, useCallback } from "react";
import { User, Building2, Briefcase, Globe, Plus, Trash2, Search, FileText, Loader2, X } from "lucide-react";
import { api } from "../api.js";

const TYPE_ICONS = {
  PERSON: User,
  BANK: Building2,
  AGENCY: Briefcase,
  COMPANY: Globe,
  OTHER: User,
};

const TYPE_LABELS = {
  PERSON: "Person",
  BANK: "Bank",
  AGENCY: "Agency",
  COMPANY: "Company",
  OTHER: "Other",
};

export default function EntitiesView() {
  const [entities, setEntities] = useState([]);
  const [selected, setSelected] = useState(null);
  const [selectedEvidence, setSelectedEvidence] = useState([]);
  const [query, setQuery] = useState("");
  const [loading, setLoading] = useState(true);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState(null);
  const [showCreate, setShowCreate] = useState(false);
  const [form, setForm] = useState({ name: "", type: "OTHER", description: "" });

  const refresh = useCallback(async (q = "") => {
    setLoading(true);
    try {
      const data = await api.listEntities(q);
      setEntities(data);
      setError(null);
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    refresh();
  }, [refresh]);

  useEffect(() => {
    const t = setTimeout(() => refresh(query), 250);
    return () => clearTimeout(t);
  }, [query, refresh]);

  async function openEntity(entity) {
    setSelected(entity);
    try {
      const ev = await api.entityEvidence(entity.id);
      setSelectedEvidence(ev);
    } catch (e) {
      setSelectedEvidence([]);
    }
  }

  async function create(e) {
    e.preventDefault();
    if (!form.name.trim()) return;
    setBusy(true);
    setError(null);
    try {
      await api.createEntity(form);
      setForm({ name: "", type: "OTHER", description: "" });
      setShowCreate(false);
      refresh(query);
    } catch (err) {
      setError(err.message);
    } finally {
      setBusy(false);
    }
  }

  async function deleteEntity(id) {
    if (!confirm("Delete this entity and all its links?")) return;
    setBusy(true);
    try {
      await api.deleteEntity(id);
      if (selected?.id === id) setSelected(null);
      refresh(query);
    } catch (err) {
      setError(err.message);
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="flex h-full">
      <aside className="flex w-72 shrink-0 flex-col border-r border-zinc-800">
        <div className="flex items-center justify-between border-b border-zinc-800 p-4">
          <h2 className="text-sm font-semibold text-zinc-200">Entities</h2>
          <button
            onClick={() => setShowCreate(true)}
            className="flex items-center gap-1 rounded bg-emerald-600 px-2 py-1 text-xs text-white hover:bg-emerald-500"
          >
            <Plus size={12} /> New
          </button>
        </div>

        <div className="p-3">
          <div className="relative">
            <Search size={13} className="absolute left-2.5 top-2.5 text-zinc-500" />
            <input
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Search entities…"
              className="w-full rounded border border-zinc-700 bg-zinc-900 py-1.5 pl-8 pr-3 text-sm text-zinc-100 outline-none focus:border-emerald-500"
            />
          </div>
        </div>

        <nav className="flex-1 overflow-y-auto px-2 pb-2">
          {loading ? (
            <div className="flex justify-center py-8 text-zinc-600"><Loader2 className="animate-spin" size={20} /></div>
          ) : entities.length === 0 ? (
            <p className="px-3 py-8 text-center text-sm text-zinc-600">No entities yet.</p>
          ) : (
            entities.map((ent) => {
              const Icon = TYPE_ICONS[ent.type] || User;
              return (
                <button
                  key={ent.id}
                  onClick={() => openEntity(ent)}
                  className={`mb-1 flex w-full items-center gap-2 rounded-lg px-3 py-2.5 text-left transition ${
                    selected?.id === ent.id ? "bg-zinc-800" : "hover:bg-zinc-900"
                  }`}
                >
                  <Icon size={14} className="shrink-0 text-zinc-500" />
                  <div className="min-w-0 flex-1">
                    <div className="truncate text-sm font-medium text-zinc-200">{ent.name}</div>
                    <div className="text-xs text-zinc-600">{TYPE_LABELS[ent.type]}</div>
                  </div>
                </button>
              );
            })
          )}
        </nav>
      </aside>

      <main className="flex-1 overflow-y-auto p-6">
        {showCreate && (
          <div className="mb-6 rounded-xl border border-zinc-800 bg-zinc-900 p-5">
            <div className="mb-4 flex items-center justify-between">
              <h3 className="text-sm font-semibold text-zinc-200">Create entity</h3>
              <button onClick={() => setShowCreate(false)} className="text-zinc-500 hover:text-zinc-300"><X size={16} /></button>
            </div>
            <form onSubmit={create} className="space-y-3">
              <input
                value={form.name}
                onChange={(e) => setForm({ ...form, name: e.target.value })}
                placeholder="Name"
                required
                className="w-full rounded-lg border border-zinc-700 bg-zinc-950 px-3 py-2 text-sm text-zinc-100 outline-none focus:border-emerald-500"
              />
              <div className="grid grid-cols-2 gap-3">
                <select
                  value={form.type}
                  onChange={(e) => setForm({ ...form, type: e.target.value })}
                  className="rounded-lg border border-zinc-700 bg-zinc-950 px-3 py-2 text-sm text-zinc-100 outline-none focus:border-emerald-500"
                >
                  {Object.entries(TYPE_LABELS).map(([v, l]) => <option key={v} value={v}>{l}</option>)}
                </select>
                <input
                  value={form.description}
                  onChange={(e) => setForm({ ...form, description: e.target.value })}
                  placeholder="Description (optional)"
                  className="rounded-lg border border-zinc-700 bg-zinc-950 px-3 py-2 text-sm text-zinc-100 outline-none focus:border-emerald-500"
                />
              </div>
              {error && <p className="text-xs text-red-400">{error}</p>}
              <div className="flex justify-end gap-2">
                <button type="button" onClick={() => setShowCreate(false)} className="rounded px-3 py-1.5 text-sm text-zinc-500 hover:text-zinc-300">Cancel</button>
                <button type="submit" disabled={busy} className="flex items-center gap-2 rounded bg-emerald-600 px-3 py-1.5 text-sm text-white hover:bg-emerald-500 disabled:opacity-50">
                  {busy && <Loader2 size={13} className="animate-spin" />} Create
                </button>
              </div>
            </form>
          </div>
        )}

        {selected ? (
          <div>
            <div className="mb-6 flex items-start justify-between">
              <div>
                <div className="flex items-center gap-2">
                  {(() => { const Icon = TYPE_ICONS[selected.type] || User; return <Icon size={18} className="text-zinc-400" />; })()}
                  <h2 className="text-xl font-semibold text-zinc-100">{selected.name}</h2>
                  <span className="rounded bg-zinc-800 px-2 py-0.5 text-xs text-zinc-400">{TYPE_LABELS[selected.type]}</span>
                </div>
                {selected.description && <p className="mt-1 text-sm text-zinc-500">{selected.description}</p>}
              </div>
              <button onClick={() => deleteEntity(selected.id)} className="rounded p-2 text-zinc-600 hover:bg-red-500/10 hover:text-red-400">
                <Trash2 size={16} />
              </button>
            </div>

            <h3 className="mb-3 text-xs font-semibold uppercase tracking-wider text-zinc-500">Linked evidence</h3>
            {selectedEvidence.length === 0 ? (
              <p className="text-sm text-zinc-600">No evidence linked to this entity yet.</p>
            ) : (
              <div className="space-y-2">
                {selectedEvidence.map((ev) => (
                  <div key={ev.id} className="flex items-center gap-3 rounded-lg border border-zinc-800 bg-zinc-900 px-4 py-3">
                    <FileText size={14} className="shrink-0 text-zinc-500" />
                    <div className="flex-1 min-w-0">
                      <div className="truncate text-sm font-medium text-zinc-200">{ev.title}</div>
                      <div className="font-mono text-xs text-zinc-600">{ev.sha256.slice(0, 16)}…</div>
                    </div>
                    {ev.role && <span className="rounded bg-zinc-800 px-2 py-0.5 text-xs text-zinc-400">{ev.role}</span>}
                  </div>
                ))}
              </div>
            )}
          </div>
        ) : (
          <div className="flex h-full items-center justify-center text-zinc-600">
            <p className="text-sm">Select an entity to inspect its linked evidence.</p>
          </div>
        )}
      </main>
    </div>
  );
}
