import React, { lazy, Suspense, useCallback, useEffect, useState } from "react";
import { api, isAuthenticated } from "./api.js";
import Navigation from "./components/Navigation.jsx";
import Dashboard from "./views/Dashboard/index.jsx";

const MERKLE_ROOT = "6a4352d020b6f2a6e2f6d18b0d366f442a18a7cd57987af0b0fce040bce55dd0";
const Modules = lazy(() => import("./views/Modules/index.jsx"));
const SourceVault = lazy(() => import("./views/SourceVault/index.jsx"));
const IngestForm = lazy(() => import("./components/IngestForm.jsx"));
const LoginModal = lazy(() => import("./components/LoginModal.jsx"));

const TOOL_VIEWS = {
  analysis: lazy(() => import("./components/AnalysisView.jsx")),
  entities: lazy(() => import("./components/EntitiesView.jsx")),
  relationships: lazy(() => import("./components/RelationshipsView.jsx")),
  timeline: lazy(() => import("./components/TimelineView.jsx")),
  admin: lazy(() => import("./components/AdminView.jsx")),
};

export default function App() {
  const knownViews = ["dashboard", "modules", "vault", ...Object.keys(TOOL_VIEWS)];
  const initialView = window.location.hash.slice(1);
  const [activeView, setActiveView] = useState(knownViews.includes(initialView) ? initialView : "dashboard");
  const [stats, setStats] = useState(null);
  const [online, setOnline] = useState(true);
  const [showIngest, setShowIngest] = useState(false);
  const [showLogin, setShowLogin] = useState(false);
  const [sourceQuery, setSourceQuery] = useState("");
  const [vaultVersion, setVaultVersion] = useState(0);

  const refreshStatus = useCallback(() => {
    Promise.all([api.health(), api.stats()])
      .then(([, nextStats]) => {
        setStats(nextStats);
        setOnline(true);
      })
      .catch(() => setOnline(false));
  }, []);

  useEffect(() => {
    refreshStatus();
  }, [refreshStatus]);

  useEffect(() => {
    const syncFromHistory = () => {
      const view = window.location.hash.slice(1);
      if (knownViews.includes(view)) setActiveView(view);
    };
    window.addEventListener("popstate", syncFromHistory);
    window.addEventListener("hashchange", syncFromHistory);
    return () => {
      window.removeEventListener("popstate", syncFromHistory);
      window.removeEventListener("hashchange", syncFromHistory);
    };
  }, []);

  useEffect(() => {
    const onKeyDown = (event) => {
      if (event.key === "/" && !["INPUT", "TEXTAREA", "SELECT"].includes(document.activeElement?.tagName)) {
        event.preventDefault();
        setSourceQuery("");
        setActiveView("vault");
      }
    };
    window.addEventListener("keydown", onKeyDown);
    return () => window.removeEventListener("keydown", onKeyDown);
  }, []);

  const navigate = (view) => {
    if (view !== "vault") setSourceQuery("");
    setActiveView(view);
    window.history.pushState(null, "", `#${view}`);
    window.scrollTo({ top: 0, behavior: "smooth" });
  };

  const openSource = (filename) => {
    setSourceQuery(filename || "");
    setActiveView("vault");
    window.history.pushState(null, "", "#vault");
    window.scrollTo({ top: 0, behavior: "smooth" });
  };

  const preserve = () => {
    if (isAuthenticated()) setShowIngest(true);
    else setShowLogin(true);
  };

  const onIngested = (created) => {
    setShowIngest(false);
    setVaultVersion((version) => version + 1);
    setSourceQuery(created?.title || "");
    setActiveView("vault");
    refreshStatus();
  };

  const ToolView = TOOL_VIEWS[activeView];

  return (
    <div className="min-h-screen bg-[#07101d] text-slate-100">
      <Navigation activeView={activeView} onNavigate={navigate} online={online} />

      {activeView === "dashboard" && (
        <Dashboard
          stats={stats}
          online={online}
          merkleRoot={MERKLE_ROOT}
          onNavigate={navigate}
          onOpenSource={openSource}
        />
      )}
      <Suspense fallback={<ViewLoader />}>
        {activeView === "modules" && <Modules onOpenSource={openSource} />}
        {activeView === "vault" && (
          <SourceVault
            key={vaultVersion}
            initialQuery={sourceQuery}
            onPreserve={preserve}
            online={online}
          />
        )}
        {ToolView && (
          <main className="h-[calc(100vh-64px)] overflow-hidden bg-zinc-950">
            <ToolView />
          </main>
        )}

        {showIngest && <IngestForm onClose={() => setShowIngest(false)} onIngested={onIngested} />}
        {showLogin && (
          <LoginModal
            onClose={() => setShowLogin(false)}
            onLogin={() => {
              setShowLogin(false);
              setShowIngest(true);
            }}
          />
        )}
      </Suspense>
    </div>
  );
}

function ViewLoader() {
  return (
    <div className="grid min-h-[calc(100vh-64px)] place-items-center bg-[#07101d]">
      <div className="flex items-center gap-3 text-xs uppercase tracking-[0.16em] text-slate-500">
        <span className="h-2 w-2 animate-pulse rounded-full bg-cyan-300" />
        Loading workspace
      </div>
    </div>
  );
}
