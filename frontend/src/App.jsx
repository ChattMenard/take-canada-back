import { useEffect, useState, useCallback } from "react";
import {
  ShieldCheck,
  Plus,
  Search,
  Database,
  FileText,
  HardDrive,
  Users,
  GitBranch,
  Calendar,
  BarChart3,
  Loader2,
  Settings,
  LogOut,
  Lock,
} from "lucide-react";
import { api, isAuthenticated, setToken } from "./api.js";
import { formatBytes, formatDate, shortHash } from "./lib/format.js";
import IngestForm from "./components/IngestForm.jsx";
import EvidenceDetail from "./components/EvidenceDetail.jsx";
import EntitiesView from "./components/EntitiesView.jsx";
import RelationshipsView from "./components/RelationshipsView.jsx";
import TimelineView from "./components/TimelineView.jsx";
import AnalysisView from "./components/AnalysisView.jsx";
import AdminView from "./components/AdminView.jsx";
import LoginModal from "./components/LoginModal.jsx";

export default function App() {
  const [items, setItems] = useState([]);
  const [selected, setSelected] = useState(null);
  const [query, setQuery] = useState("");
  const [showIngest, setShowIngest] = useState(false);
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [online, setOnline] = useState(true);
  const [activeView, setActiveView] = useState("vault");
  const [showLogin, setShowLogin] = useState(false);

  const refresh = useCallback(async (q = "") => {
    try {
      const [list, s] = await Promise.all([api.listEvidence(q), api.stats()]);
      setItems(list);
      setStats(s);
      setOnline(true);
    } catch (e) {
      setOnline(false);
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

  async function openItem(id) {
    const detail = await api.getEvidence(id);
    setSelected(detail);
  }

  function onIngested(created) {
    setShowIngest(false);
    refresh(query);
    setSelected(created);
  }

  function handleLoginRequired() {
    setShowLogin(true);
  }

  function handleLogout() {
    setToken(null);
    setShowLogin(false);
  }

  function onUpdated(fresh) {
    setSelected(fresh);
    setItems((prev) => prev.map((it) => (it.id === fresh.id ? { ...it, ...fresh } : it)));
    api.stats().then(setStats).catch(() => {});
  }

  const navTab = (id, label, Icon) => (
    <button
      key={id}
      onClick={() => setActiveView(id)}
      className={`flex items-center gap-1.5 rounded-lg px-3 py-1.5 text-sm font-medium transition ${
        activeView === id
          ? "bg-zinc-800 text-zinc-100"
          : "text-zinc-500 hover:text-zinc-300"
      }`}
    >
      <Icon size={14} />
      {label}
    </button>
  );

  return (
    <div className="flex h-screen flex-col bg-zinc-950 text-zinc-100">
      {/* Top navigation bar */}
      <header className="flex shrink-0 items-center gap-4 border-b border-zinc-800 px-4 py-2">
        <div className="flex items-center gap-2">
          <ShieldCheck className="text-emerald-400" size={20} />
          <span className="text-sm font-semibold">Veritas</span>
          <span
            className={`h-2 w-2 rounded-full ${online ? "bg-emerald-500" : "bg-red-500"}`}
            title={online ? "Backend online" : "Backend offline"}
          />
        </div>
        <nav className="flex items-center gap-1">
          {navTab("vault", "Vault", Database)}
          {navTab("analysis", "Analysis", BarChart3)}
          {navTab("entities", "Entities", Users)}
          {navTab("relationships", "Relationships", GitBranch)}
          {navTab("timeline", "Timeline", Calendar)}
          {navTab("admin", "Admin", Settings)}
        </nav>
        <div className="ml-auto flex items-center gap-3">
          {isAuthenticated() ? (
            <button
              onClick={handleLogout}
              className="flex items-center gap-1.5 rounded-lg px-3 py-1.5 text-xs font-medium text-zinc-400 hover:text-zinc-200 hover:bg-zinc-800 transition"
              title="Logout"
            >
              <LogOut size={14} />
              Logout
            </button>
          ) : (
            <button
              onClick={() => setShowLogin(true)}
              className="flex items-center gap-1.5 rounded-lg px-3 py-1.5 text-xs font-medium text-zinc-400 hover:text-zinc-200 hover:bg-zinc-800 transition"
            >
              <Lock size={14} />
              Login
            </button>
          )}
          {stats && (
            <div className="flex items-center gap-4 text-xs text-zinc-500">
              <span>{stats.evidence_count} evidence</span>
              <span>{stats.entity_count} entities</span>
              <span>{formatBytes(stats.storage_bytes)}</span>
            </div>
          )}
        </div>
      </header>

      {/* View area */}
      <div className="flex min-h-0 flex-1">
        {activeView === "vault" && (
          <>
            {/* Sidebar */}
            <aside className="flex w-80 shrink-0 flex-col border-r border-zinc-800">
              <div className="p-3">
                <button
                  onClick={() => setShowIngest(true)}
                  className="flex w-full items-center justify-center gap-2 rounded-lg bg-emerald-600 px-3 py-2 text-sm font-medium text-white hover:bg-emerald-500"
                >
                  <Plus size={16} /> Preserve evidence
                </button>
                <div className="relative mt-3">
                  <Search size={15} className="absolute left-3 top-1/2 -translate-y-1/2 text-zinc-500" />
                  <input
                    value={query}
                    onChange={(e) => setQuery(e.target.value)}
                    placeholder="Search evidence…"
                    className="w-full rounded-lg border border-zinc-700 bg-zinc-900 py-2 pl-9 pr-3 text-sm outline-none focus:border-emerald-500"
                  />
                </div>
              </div>

              <nav className="flex-1 overflow-y-auto px-2 pb-2">
                {loading ? (
                  <div className="flex justify-center py-10 text-zinc-600">
                    <Loader2 className="animate-spin" />
                  </div>
                ) : items.length === 0 ? (
                  <p className="px-3 py-10 text-center text-sm text-zinc-600">
                    No evidence yet. Preserve your first document.
                  </p>
                ) : (
                  items.map((it) => (
                    <button
                      key={it.id}
                      onClick={() => openItem(it.id)}
                      className={`mb-1 w-full rounded-lg px-3 py-2.5 text-left transition ${
                        selected?.id === it.id ? "bg-zinc-800" : "hover:bg-zinc-900"
                      }`}
                    >
                      <div className="flex items-center gap-2">
                        <FileText size={15} className="shrink-0 text-zinc-500" />
                        <span className="truncate text-sm font-medium">{it.title}</span>
                      </div>
                      <div className="mt-1 flex items-center justify-between text-xs text-zinc-600">
                        <span className="font-mono">{shortHash(it.sha256)}</span>
                        <span>{formatDate(it.created_at)}</span>
                      </div>
                    </button>
                  ))
                )}
              </nav>

              {stats && (
                <footer className="grid grid-cols-2 gap-px border-t border-zinc-800 bg-zinc-800 text-xs">
                  <Stat icon={Database} label="Evidence" value={stats.evidence_count} />
                  <Stat icon={HardDrive} label="Stored" value={formatBytes(stats.storage_bytes)} />
                  <Stat icon={Users} label="Entities" value={stats.entity_count} />
                  <Stat icon={GitBranch} label="Links" value={stats.relationship_count} />
                </footer>
              )}
            </aside>

            {/* Main */}
            <main className="flex-1 overflow-hidden">
              {selected ? (
                <EvidenceDetail evidence={selected} onUpdated={onUpdated} />
              ) : (
                <EmptyState online={online} onAdd={() => setShowIngest(true)} />
              )}
            </main>
          </>
        )}

        {activeView === "entities" && (
          <div className="flex-1 overflow-hidden">
            <EntitiesView />
          </div>
        )}

        {activeView === "analysis" && (
          <div className="flex-1 overflow-hidden">
            <AnalysisView />
          </div>
        )}

        {activeView === "relationships" && (
          <div className="flex-1 overflow-hidden">
            <RelationshipsView />
          </div>
        )}

        {activeView === "timeline" && (
          <div className="flex-1 overflow-hidden">
            <TimelineView />
          </div>
        )}

        {activeView === "admin" && (
          <div className="flex-1 overflow-hidden">
            <AdminView />
          </div>
        )}
      </div>

      {showIngest && (
        <IngestForm onClose={() => setShowIngest(false)} onIngested={onIngested} />
      )}
      {showLogin && (
        <LoginModal onClose={() => setShowLogin(false)} onLogin={() => setShowLogin(false)} />
      )}
    </div>
  );
}

function Stat({ icon: Icon, label, value }) {
  return (
    <div className="flex items-center gap-2 bg-zinc-950 px-3 py-2.5">
      <Icon size={14} className="text-zinc-500" />
      <div>
        <div className="font-semibold text-zinc-200">{value}</div>
        <div className="text-zinc-600">{label}</div>
      </div>
    </div>
  );
}

function EmptyState({ online, onAdd }) {
  return (
    <div className="flex h-full flex-col items-center justify-center p-8 text-center">
      <ShieldCheck size={48} className="mb-4 text-zinc-700" />
      <h2 className="text-lg font-medium text-zinc-300">
        {online ? "Select evidence to inspect it" : "Backend offline"}
      </h2>
      <p className="mt-2 max-w-md text-sm text-zinc-500">
        {online
          ? "Every document is hashed with SHA-256 on arrival and tracked with a full chain of custody. Tamper-evidence you can re-verify anytime."
          : "Start the API server (uvicorn app.main:app) on port 8000, then reload."}
      </p>
      {online && (
        <button
          onClick={onAdd}
          className="mt-5 flex items-center gap-2 rounded-lg bg-emerald-600 px-4 py-2 text-sm font-medium text-white hover:bg-emerald-500"
        >
          <Plus size={16} /> Preserve evidence
        </button>
      )}
    </div>
  );
}
