import { useState, useEffect } from "react";
import {
  Plus,
  Search,
  Trash2,
  Calendar,
  FileText,
  Link as LinkIcon,
  X,
} from "lucide-react";
import { api } from "../api.js";
import { formatDate } from "../lib/format.js";

export default function TimelinePanel({ evidenceId, onLinked }) {
  const [events, setEvents] = useState([]);
  const [searchQuery, setSearchQuery] = useState("");
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [createForm, setCreateForm] = useState({
    title: "",
    description: "",
    occurred_at: "",
    evidence_id: evidenceId || null,
  });
  const [loading, setLoading] = useState(true);
  const [linkingEvidence, setLinkingEvidence] = useState(null);

  useEffect(() => {
    loadEvents();
  }, [evidenceId]);

  async function loadEvents() {
    setLoading(true);
    try {
      const data = await api.listTimeline();
      setEvents(data);
    } catch (err) {
      console.error("Failed to load timeline events:", err);
    } finally {
      setLoading(false);
    }
  }

  async function createEvent(e) {
    e.preventDefault();
    try {
      const payload = {
        ...createForm,
        occurred_at: createForm.occurred_at ? new Date(createForm.occurred_at).toISOString() : null,
        evidence_id: createForm.evidence_id || null,
      };
      await api.createTimelineEvent(payload);
      setCreateForm({
        title: "",
        description: "",
        occurred_at: "",
        evidence_id: evidenceId || null,
      });
      setShowCreateForm(false);
      loadEvents();
    } catch (err) {
      console.error("Failed to create timeline event:", err);
      alert("Failed to create timeline event");
    }
  }

  async function deleteEvent(id) {
    if (!confirm("Delete this timeline event?")) return;
    try {
      await api.deleteTimelineEvent(id);
      loadEvents();
    } catch (err) {
      console.error("Failed to delete timeline event:", err);
      alert("Failed to delete timeline event");
    }
  }

  async function linkEvidenceToEvent(eventId) {
    if (!evidenceId) return;
    setLinkingEvidence(eventId);
    try {
      await api.updateTimelineEvent(eventId, { evidence_id: evidenceId });
      loadEvents();
      if (onLinked) onLinked();
    } catch (err) {
      console.error("Failed to link evidence:", err);
      alert("Failed to link evidence");
    } finally {
      setLinkingEvidence(null);
    }
  }

  async function unlinkEvidenceFromEvent(eventId) {
    try {
      await api.updateTimelineEvent(eventId, { evidence_id: null });
      loadEvents();
      if (onLinked) onLinked();
    } catch (err) {
      console.error("Failed to unlink evidence:", err);
      alert("Failed to unlink evidence");
    }
  }

  const filteredEvents = evidenceId
    ? events.filter((e) => e.evidence_id === evidenceId)
    : events.filter(
        (e) =>
          e.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
          (e.description && e.description.toLowerCase().includes(searchQuery.toLowerCase()))
      );

  const sortedEvents = [...filteredEvents].sort(
    (a, b) => new Date(a.occurred_at) - new Date(b.occurred_at)
  );

  return (
    <div className="flex h-full flex-col">
      <div className="flex items-center justify-between border-b border-zinc-800 p-4">
        <h3 className="text-sm font-semibold text-zinc-200">Timeline</h3>
        <button
          onClick={() => setShowCreateForm(!showCreateForm)}
          className="flex items-center gap-1 rounded-lg border border-zinc-700 px-2 py-1 text-xs text-zinc-300 hover:bg-zinc-800"
        >
          <Plus size={14} />
          New
        </button>
      </div>

      {showCreateForm && (
        <form onSubmit={createEvent} className="border-b border-zinc-800 p-4 space-y-3">
          <div>
            <label className="mb-1 block text-xs text-zinc-500">Title</label>
            <input
              type="text"
              value={createForm.title}
              onChange={(e) => setCreateForm({ ...createForm, title: e.target.value })}
              placeholder="Event title"
              className="w-full rounded-lg border border-zinc-700 bg-zinc-900 px-2 py-1.5 text-sm text-zinc-100 outline-none focus:border-emerald-500"
              required
            />
          </div>
          <div>
            <label className="mb-1 block text-xs text-zinc-500">Description (optional)</label>
            <textarea
              value={createForm.description}
              onChange={(e) => setCreateForm({ ...createForm, description: e.target.value })}
              placeholder="Event description"
              rows={2}
              className="w-full rounded-lg border border-zinc-700 bg-zinc-900 px-2 py-1.5 text-sm text-zinc-100 outline-none focus:border-emerald-500 resize-none"
            />
          </div>
          <div>
            <label className="mb-1 block text-xs text-zinc-500">Occurred At</label>
            <input
              type="date"
              value={createForm.occurred_at}
              onChange={(e) => setCreateForm({ ...createForm, occurred_at: e.target.value })}
              className="w-full rounded-lg border border-zinc-700 bg-zinc-900 px-2 py-1.5 text-sm text-zinc-100 outline-none focus:border-emerald-500"
              required
            />
          </div>
          <div className="flex justify-end gap-2">
            <button
              type="button"
              onClick={() => setShowCreateForm(false)}
              className="rounded-lg border border-zinc-700 px-3 py-1.5 text-xs text-zinc-300 hover:bg-zinc-800"
            >
              Cancel
            </button>
            <button
              type="submit"
              className="rounded-lg bg-emerald-600 px-3 py-1.5 text-xs text-white hover:bg-emerald-700"
            >
              Create
            </button>
          </div>
        </form>
      )}

      {!evidenceId && (
        <div className="border-b border-zinc-800 p-3">
          <div className="relative">
            <Search size={14} className="absolute left-2.5 top-2.5 text-zinc-500" />
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Search events..."
              className="w-full rounded-lg border border-zinc-700 bg-zinc-900 pl-8 pr-3 py-1.5 text-sm text-zinc-100 outline-none focus:border-emerald-500"
            />
          </div>
        </div>
      )}

      <div className="flex-1 overflow-y-auto p-3">
        {loading ? (
          <p className="text-center text-sm text-zinc-500">Loading...</p>
        ) : sortedEvents.length === 0 ? (
          <p className="text-center text-sm text-zinc-500">No timeline events found</p>
        ) : (
          <div className="relative space-y-4 border-l border-zinc-800 pl-5">
            {sortedEvents.map((event) => {
              const isLinked = event.evidence_id === evidenceId;

              return (
                <div key={event.id} className="relative">
                  <span className="absolute -left-[27px] flex h-5 w-5 items-center justify-center rounded-full bg-zinc-950">
                    <Calendar size={15} className="text-emerald-400" />
                  </span>
                  <div className="rounded-lg border border-zinc-800 bg-zinc-900/50 p-3 hover:border-zinc-700">
                    <div className="flex items-start justify-between gap-2">
                      <div className="flex-1">
                        <h4 className="font-medium text-zinc-200">{event.title}</h4>
                        {event.description && (
                          <p className="mt-1 text-sm text-zinc-400">{event.description}</p>
                        )}
                        <p className="mt-2 flex items-center gap-1 text-xs text-zinc-500">
                          <Calendar size={11} />
                          {formatDate(event.occurred_at)}
                        </p>
                      </div>
                      <div className="flex shrink-0 gap-1">
                        {evidenceId && !isLinked && (
                          <button
                            onClick={() => linkEvidenceToEvent(event.id)}
                            disabled={linkingEvidence === event.id}
                            className="rounded p-1.5 bg-zinc-800 text-zinc-400 hover:bg-emerald-500/20 hover:text-emerald-400 disabled:opacity-50"
                            title="Link evidence"
                          >
                            <LinkIcon size={13} />
                          </button>
                        )}
                        {isLinked && (
                          <button
                            onClick={() => unlinkEvidenceFromEvent(event.id)}
                            className="rounded p-1.5 bg-emerald-500/20 text-emerald-400 hover:bg-emerald-500/30"
                            title="Unlink evidence"
                          >
                            <LinkIcon size={13} />
                          </button>
                        )}
                        <button
                          onClick={() => deleteEvent(event.id)}
                          className="rounded p-1.5 bg-zinc-800 text-zinc-400 hover:bg-red-500/20 hover:text-red-400"
                          title="Delete"
                        >
                          <Trash2 size={13} />
                        </button>
                      </div>
                    </div>
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
