import { useState, useEffect } from "react";
import { Plus, Trash2, Calendar, FileText, Search, X, Loader2 } from "lucide-react";
import { api } from "../api.js";
import { formatDate } from "../lib/format.js";

export default function TimelineView() {
  const [events, setEvents] = useState([]);
  const [query, setQuery] = useState("");
  const [loading, setLoading] = useState(true);
  const [showCreate, setShowCreate] = useState(false);
  const [form, setForm] = useState({ title: "", description: "", occurred_at: "" });

  useEffect(() => {
    load();
  }, []);

  async function load() {
    setLoading(true);
    try {
      const data = await api.listTimeline();
      setEvents(data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  }

  async function create(e) {
    e.preventDefault();
    try {
      await api.createTimelineEvent({
        ...form,
        occurred_at: new Date(form.occurred_at).toISOString(),
        evidence_id: null,
      });
      setForm({ title: "", description: "", occurred_at: "" });
      setShowCreate(false);
      load();
    } catch (err) {
      alert(err.message);
    }
  }

  async function del(id) {
    if (!confirm("Delete this event?")) return;
    await api.deleteTimelineEvent(id);
    load();
  }

  const filtered = events
    .filter((ev) => {
      if (!query) return true;
      const q = query.toLowerCase();
      return ev.title.toLowerCase().includes(q) || (ev.description || "").toLowerCase().includes(q);
    })
    .sort((a, b) => new Date(a.occurred_at) - new Date(b.occurred_at));

  return (
    <div className="flex h-full flex-col overflow-hidden">
      <div className="flex items-center justify-between border-b border-zinc-800 p-4">
        <h2 className="text-sm font-semibold text-zinc-200">Timeline</h2>
        <button
          onClick={() => setShowCreate(true)}
          className="flex items-center gap-1 rounded bg-emerald-600 px-2 py-1 text-xs text-white hover:bg-emerald-500"
        >
          <Plus size={12} /> New event
        </button>
      </div>

      <div className="border-b border-zinc-800 p-3">
        <div className="relative">
          <Search size={13} className="absolute left-2.5 top-2.5 text-zinc-500" />
          <input
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Search events…"
            className="w-full rounded border border-zinc-700 bg-zinc-900 py-1.5 pl-8 pr-3 text-sm text-zinc-100 outline-none focus:border-emerald-500"
          />
        </div>
      </div>

      {showCreate && (
        <div className="border-b border-zinc-800 bg-zinc-900 p-4">
          <div className="mb-3 flex items-center justify-between">
            <span className="text-xs font-semibold text-zinc-300">New timeline event</span>
            <button onClick={() => setShowCreate(false)} className="text-zinc-500 hover:text-zinc-300"><X size={14} /></button>
          </div>
          <form onSubmit={create} className="space-y-3">
            <input
              value={form.title}
              onChange={(e) => setForm({ ...form, title: e.target.value })}
              placeholder="Event title"
              required
              className="w-full rounded border border-zinc-700 bg-zinc-950 px-3 py-2 text-sm text-zinc-100 outline-none focus:border-emerald-500"
            />
            <textarea
              value={form.description}
              onChange={(e) => setForm({ ...form, description: e.target.value })}
              placeholder="Description (optional)"
              rows={2}
              className="w-full resize-none rounded border border-zinc-700 bg-zinc-950 px-3 py-2 text-sm text-zinc-100 outline-none focus:border-emerald-500"
            />
            <input
              type="date"
              value={form.occurred_at}
              onChange={(e) => setForm({ ...form, occurred_at: e.target.value })}
              required
              className="w-full rounded border border-zinc-700 bg-zinc-950 px-3 py-2 text-sm text-zinc-100 outline-none focus:border-emerald-500"
            />
            <div className="flex justify-end gap-2">
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
          <p className="py-12 text-center text-sm text-zinc-600">No timeline events yet.</p>
        ) : (
          <div className="relative space-y-4 border-l border-zinc-800 pl-6">
            {filtered.map((ev) => (
              <div key={ev.id} className="relative">
                <span className="absolute -left-[27px] flex h-5 w-5 items-center justify-center rounded-full bg-zinc-950">
                  <Calendar size={13} className="text-emerald-400" />
                </span>
                <div className="rounded-lg border border-zinc-800 bg-zinc-900/50 p-4 hover:border-zinc-700">
                  <div className="flex items-start justify-between gap-3">
                    <div className="flex-1">
                      <h4 className="font-medium text-zinc-200">{ev.title}</h4>
                      {ev.description && <p className="mt-1 text-sm text-zinc-400">{ev.description}</p>}
                      <div className="mt-2 flex flex-wrap items-center gap-3 text-xs text-zinc-600">
                        <span className="flex items-center gap-1"><Calendar size={11} />{formatDate(ev.occurred_at)}</span>
                        {ev.evidence_id && (
                          <span className="flex items-center gap-1 rounded bg-zinc-800 px-1.5 py-0.5 text-zinc-400">
                            <FileText size={10} /> evidence #{ev.evidence_id}
                          </span>
                        )}
                      </div>
                    </div>
                    <button onClick={() => del(ev.id)} className="rounded p-1.5 text-zinc-600 hover:bg-red-500/10 hover:text-red-400">
                      <Trash2 size={14} />
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
