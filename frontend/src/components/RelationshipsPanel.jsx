import { useState, useEffect } from "react";
import {
  Plus,
  Search,
  Trash2,
  Link as LinkIcon,
  FileText,
  Calendar,
  DollarSign,
  ArrowRightLeft,
  ArrowUpRight,
  User,
  Building,
  X,
} from "lucide-react";
import { api } from "../api.js";
import { formatDate } from "../lib/format.js";

const KIND_ICONS = {
  DONATION: { icon: DollarSign, color: "text-emerald-400" },
  CONTRACT: { icon: FileText, color: "text-blue-400" },
  BOARD_SEAT: { icon: Building, color: "text-purple-400" },
  OWNERSHIP: { icon: ArrowUpRight, color: "text-amber-400" },
  LOBBYING: { icon: ArrowRightLeft, color: "text-pink-400" },
  EMPLOYMENT: { icon: User, color: "text-cyan-400" },
  OTHER: { icon: LinkIcon, color: "text-zinc-400" },
};

const KIND_LABELS = {
  DONATION: "Donation",
  CONTRACT: "Contract",
  BOARD_SEAT: "Board Seat",
  OWNERSHIP: "Ownership",
  LOBBYING: "Lobbying",
  EMPLOYMENT: "Employment",
  OTHER: "Other",
};

export default function RelationshipsPanel({ evidenceId, onLinked }) {
  const [relationships, setRelationships] = useState([]);
  const [entities, setEntities] = useState([]);
  const [searchQuery, setSearchQuery] = useState("");
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [createForm, setCreateForm] = useState({
    source_entity_id: "",
    target_entity_id: "",
    kind: "OTHER",
    amount: "",
    occurred_at: "",
  });
  const [loading, setLoading] = useState(true);
  const [linkingEvidence, setLinkingEvidence] = useState(null);

  useEffect(() => {
    loadEntities();
  }, []);

  useEffect(() => {
    if (evidenceId) {
      loadRelationships();
    }
  }, [evidenceId]);

  async function loadEntities() {
    try {
      const data = await api.listEntities();
      setEntities(data);
    } catch (err) {
      console.error("Failed to load entities:", err);
    }
  }

  async function loadRelationships() {
    setLoading(true);
    try {
      const data = await api.listRelationships();
      setRelationships(data);
    } catch (err) {
      console.error("Failed to load relationships:", err);
    } finally {
      setLoading(false);
    }
  }

  async function createRelationship(e) {
    e.preventDefault();
    try {
      await api.createRelationship(createForm);
      setCreateForm({
        source_entity_id: "",
        target_entity_id: "",
        kind: "OTHER",
        amount: "",
        occurred_at: "",
      });
      setShowCreateForm(false);
      loadRelationships();
    } catch (err) {
      console.error("Failed to create relationship:", err);
      alert("Failed to create relationship");
    }
  }

  async function deleteRelationship(id) {
    if (!confirm("Delete this relationship?")) return;
    try {
      await api.deleteRelationship(id);
      loadRelationships();
    } catch (err) {
      console.error("Failed to delete relationship:", err);
      alert("Failed to delete relationship");
    }
  }

  async function linkEvidenceToRelationship(relationshipId) {
    if (!evidenceId) return;
    setLinkingEvidence(relationshipId);
    try {
      await api.linkRelationshipEvidence(relationshipId, evidenceId);
      loadRelationships();
      if (onLinked) onLinked();
    } catch (err) {
      console.error("Failed to link evidence:", err);
      alert("Failed to link evidence");
    } finally {
      setLinkingEvidence(null);
    }
  }

  async function unlinkEvidenceFromRelationship(relationshipId) {
    if (!evidenceId) return;
    try {
      await api.unlinkRelationshipEvidence(relationshipId, evidenceId);
      loadRelationships();
      if (onLinked) onLinked();
    } catch (err) {
      console.error("Failed to unlink evidence:", err);
      alert("Failed to unlink evidence");
    }
  }

  const filteredEntities = entities.filter((e) =>
    e.name.toLowerCase().includes(searchQuery.toLowerCase())
  );

  const filteredRelationships = evidenceId
    ? relationships.filter((r) => r.linked_evidence?.some((le) => le.id === evidenceId))
    : relationships;

  return (
    <div className="flex h-full flex-col">
      <div className="flex items-center justify-between border-b border-zinc-800 p-4">
        <h3 className="text-sm font-semibold text-zinc-200">Relationships</h3>
        <button
          onClick={() => setShowCreateForm(!showCreateForm)}
          className="flex items-center gap-1 rounded-lg border border-zinc-700 px-2 py-1 text-xs text-zinc-300 hover:bg-zinc-800"
        >
          <Plus size={14} />
          New
        </button>
      </div>

      {showCreateForm && (
        <form onSubmit={createRelationship} className="border-b border-zinc-800 p-4 space-y-3">
          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="mb-1 block text-xs text-zinc-500">Source Entity</label>
              <select
                value={createForm.source_entity_id}
                onChange={(e) => setCreateForm({ ...createForm, source_entity_id: e.target.value })}
                className="w-full rounded-lg border border-zinc-700 bg-zinc-900 px-2 py-1.5 text-sm text-zinc-100 outline-none focus:border-emerald-500"
                required
              >
                <option value="">Select...</option>
                {entities.map((e) => (
                  <option key={e.id} value={e.id}>
                    {e.name} ({e.type})
                  </option>
                ))}
              </select>
            </div>
            <div>
              <label className="mb-1 block text-xs text-zinc-500">Target Entity</label>
              <select
                value={createForm.target_entity_id}
                onChange={(e) => setCreateForm({ ...createForm, target_entity_id: e.target.value })}
                className="w-full rounded-lg border border-zinc-700 bg-zinc-900 px-2 py-1.5 text-sm text-zinc-100 outline-none focus:border-emerald-500"
                required
              >
                <option value="">Select...</option>
                {entities.map((e) => (
                  <option key={e.id} value={e.id}>
                    {e.name} ({e.type})
                  </option>
                ))}
              </select>
            </div>
          </div>
          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="mb-1 block text-xs text-zinc-500">Relationship Type</label>
              <select
                value={createForm.kind}
                onChange={(e) => setCreateForm({ ...createForm, kind: e.target.value })}
                className="w-full rounded-lg border border-zinc-700 bg-zinc-900 px-2 py-1.5 text-sm text-zinc-100 outline-none focus:border-emerald-500"
              >
                {Object.entries(KIND_LABELS).map(([value, label]) => (
                  <option key={value} value={value}>
                    {label}
                  </option>
                ))}
              </select>
            </div>
            <div>
              <label className="mb-1 block text-xs text-zinc-500">Amount (optional)</label>
              <input
                type="text"
                value={createForm.amount}
                onChange={(e) => setCreateForm({ ...createForm, amount: e.target.value })}
                placeholder="e.g. $1M, 50%"
                className="w-full rounded-lg border border-zinc-700 bg-zinc-900 px-2 py-1.5 text-sm text-zinc-100 outline-none focus:border-emerald-500"
              />
            </div>
          </div>
          <div>
            <label className="mb-1 block text-xs text-zinc-500">Occurred At (optional)</label>
            <input
              type="date"
              value={createForm.occurred_at}
              onChange={(e) => setCreateForm({ ...createForm, occurred_at: e.target.value })}
              className="w-full rounded-lg border border-zinc-700 bg-zinc-900 px-2 py-1.5 text-sm text-zinc-100 outline-none focus:border-emerald-500"
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

      <div className="border-b border-zinc-800 p-3">
        <div className="relative">
          <Search size={14} className="absolute left-2.5 top-2.5 text-zinc-500" />
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Search entities..."
            className="w-full rounded-lg border border-zinc-700 bg-zinc-900 pl-8 pr-3 py-1.5 text-sm text-zinc-100 outline-none focus:border-emerald-500"
          />
        </div>
      </div>

      <div className="flex-1 overflow-y-auto p-3">
        {loading ? (
          <p className="text-center text-sm text-zinc-500">Loading...</p>
        ) : filteredRelationships.length === 0 ? (
          <p className="text-center text-sm text-zinc-500">No relationships found</p>
        ) : (
          <div className="space-y-2">
            {filteredRelationships.map((rel) => {
              const meta = KIND_ICONS[rel.kind] || KIND_ICONS.RELATED_TO;
              const Icon = meta.icon;
              const sourceEntity = entities.find((e) => e.id === rel.source_entity_id);
              const targetEntity = entities.find((e) => e.id === rel.target_entity_id);
              const isLinked = rel.linked_evidence?.some((le) => le.id === evidenceId);

              return (
                <div
                  key={rel.id}
                  className="rounded-lg border border-zinc-800 bg-zinc-900/50 p-3 hover:border-zinc-700"
                >
                  <div className="flex items-start justify-between gap-2">
                    <div className="flex-1">
                      <div className="flex items-center gap-2">
                        <span className="font-medium text-zinc-200">{sourceEntity?.name || "Unknown"}</span>
                        <Icon size={14} className={meta.color} />
                        <span className="text-xs text-zinc-500">{KIND_LABELS[rel.kind]}</span>
                        <Icon size={14} className={meta.color} />
                        <span className="font-medium text-zinc-200">{targetEntity?.name || "Unknown"}</span>
                      </div>
                      {rel.amount && (
                        <p className="mt-1 text-xs text-zinc-400">
                          <DollarSign size={11} className="inline mr-1" />
                          {rel.amount}
                        </p>
                      )}
                      {rel.occurred_at && (
                        <p className="mt-1 text-xs text-zinc-400">
                          <Calendar size={11} className="inline mr-1" />
                          {formatDate(rel.occurred_at)}
                        </p>
                      )}
                      {rel.linked_evidence && rel.linked_evidence.length > 0 && (
                        <div className="mt-2 flex flex-wrap gap-1">
                          {rel.linked_evidence.map((le) => (
                            <span
                              key={le.id}
                              className="inline-flex items-center gap-1 rounded bg-zinc-800 px-1.5 py-0.5 text-xs text-zinc-400"
                              title={le.title}
                            >
                              <FileText size={10} />
                              {le.title.length > 20 ? le.title.slice(0, 20) + "..." : le.title}
                            </span>
                          ))}
                        </div>
                      )}
                    </div>
                    <div className="flex shrink-0 gap-1">
                      {evidenceId && (
                        <button
                          onClick={() =>
                            isLinked
                              ? unlinkEvidenceFromRelationship(rel.id)
                              : linkEvidenceToRelationship(rel.id)
                          }
                          disabled={linkingEvidence === rel.id}
                          className={`rounded p-1.5 ${
                            isLinked
                              ? "bg-emerald-500/20 text-emerald-400 hover:bg-emerald-500/30"
                              : "bg-zinc-800 text-zinc-400 hover:bg-zinc-700"
                          } disabled:opacity-50`}
                          title={isLinked ? "Unlink evidence" : "Link evidence"}
                        >
                          <LinkIcon size={13} />
                        </button>
                      )}
                      <button
                        onClick={() => deleteRelationship(rel.id)}
                        className="rounded p-1.5 bg-zinc-800 text-zinc-400 hover:bg-red-500/20 hover:text-red-400"
                        title="Delete"
                      >
                        <Trash2 size={13} />
                      </button>
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
