import { useState } from "react";
import {
  AlertTriangle,
  Download,
  FileText,
  Lock,
  ShieldCheck,
  Loader2,
  CheckCircle2,
} from "lucide-react";
import { api } from "../api.js";
import { formatDate, formatBytes } from "../lib/format.js";

export default function AdminView() {
  const [sealStatus, setSealStatus] = useState(null);
  const [loading, setLoading] = useState(true);
  const [verifying, setVerifying] = useState(false);
  const [exporting, setExporting] = useState(false);
  const [verifyResult, setVerifyResult] = useState(null);
  const [exportResult, setExportResult] = useState(null);

  useState(() => {
    loadSealStatus();
  });

  async function loadSealStatus() {
    try {
      const status = await api.sealStatus();
      setSealStatus(status);
    } catch (e) {
      console.error("Failed to load seal status", e);
    } finally {
      setLoading(false);
    }
  }

  async function handleSeal() {
    if (!confirm("This will permanently seal the vault. All write operations will be blocked. Continue?")) {
      return;
    }
    try {
      const result = await api.sealVault();
      setSealStatus({ ...sealStatus, sealed: true, sealed_at: result.sealed_at });
      alert("Vault sealed successfully.");
    } catch (e) {
      alert("Failed to seal vault: " + e.message);
    }
  }

  async function handleVerifyAll() {
    setVerifying(true);
    try {
      const result = await api.verifyAll();
      setVerifyResult(result);
    } catch (e) {
      alert("Verification failed: " + e.message);
    } finally {
      setVerifying(false);
    }
  }

  async function handleExport() {
    const vaultId = prompt("Enter vault ID (e.g., release-2024-06-25):", "manual-export");
    if (!vaultId) return;
    const includeStore = confirm("Include object store in package? (Large file)");
    setExporting(true);
    try {
      const result = await api.exportPackage(vaultId, includeStore);
      setExportResult(result);
      alert(`Export complete.\nManifest: ${result.manifest_path}\nPackage: ${result.package_path || "Not included"}`);
    } catch (e) {
      alert("Export failed: " + e.message);
    } finally {
      setExporting(false);
    }
  }

  if (loading) {
    return (
      <div className="flex h-full items-center justify-center text-zinc-600">
        <Loader2 className="animate-spin" size={26} />
      </div>
    );
  }

  return (
    <div className="flex h-full flex-col overflow-hidden">
      <header className="shrink-0 border-b border-zinc-800 px-5 py-4">
        <div className="flex items-center gap-2 text-sm font-semibold text-zinc-100">
          <ShieldCheck size={18} className="text-cyan-300" />
          Vault Administration
        </div>
      </header>

      <main className="min-h-0 flex-1 overflow-y-auto p-5">
        <div className="max-w-2xl space-y-6">
          {/* Seal Status */}
          <section className="rounded-lg border border-zinc-800 bg-zinc-950 p-5">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                {sealStatus?.sealed ? (
                  <Lock size={20} className="text-amber-300" />
                ) : (
                  <ShieldCheck size={20} className="text-emerald-300" />
                )}
                <h2 className="text-sm font-semibold text-zinc-100">
                  Vault Status: {sealStatus?.sealed ? "Sealed" : "Unsealed"}
                </h2>
              </div>
              {!sealStatus?.sealed && (
                <button
                  onClick={handleSeal}
                  className="rounded-lg bg-amber-600 px-3 py-1.5 text-xs font-medium text-white hover:bg-amber-500"
                >
                  Seal Vault
                </button>
              )}
            </div>
            {sealStatus?.sealed && (
              <div className="mt-3 text-xs text-zinc-500">
                Sealed at: {formatDate(sealStatus.sealed_at)}
              </div>
            )}
            <div className="mt-3 grid grid-cols-3 gap-2 text-xs">
              <div className="rounded bg-zinc-900 px-2 py-2">
                <div className="font-semibold text-zinc-200">{sealStatus?.evidence_objects || 0}</div>
                <div className="text-zinc-600">Evidence objects</div>
              </div>
              <div className="rounded bg-zinc-900 px-2 py-2">
                <div className="font-semibold text-zinc-200">{sealStatus?.timestamp_files || 0}</div>
                <div className="text-zinc-600">Timestamp files</div>
              </div>
              <div className="rounded bg-zinc-900 px-2 py-2">
                <div className="font-semibold text-zinc-200">{sealStatus?.db_path?.split("/")?.pop()}</div>
                <div className="text-zinc-600">Database</div>
              </div>
            </div>
          </section>

          {/* Verify All */}
          <section className="rounded-lg border border-zinc-800 bg-zinc-950 p-5">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <CheckCircle2 size={20} className="text-cyan-300" />
                <h2 className="text-sm font-semibold text-zinc-100">Verify All Evidence</h2>
              </div>
              <button
                onClick={handleVerifyAll}
                disabled={verifying}
                className="rounded-lg bg-cyan-600 px-3 py-1.5 text-xs font-medium text-white hover:bg-cyan-500 disabled:opacity-50"
              >
                {verifying ? <Loader2 size={14} className="animate-spin" /> : "Verify"}
              </button>
            </div>
            {verifyResult && (
              <div className="mt-3 text-xs">
                <div className="flex items-center gap-2">
                  <span className="text-zinc-500">Total: {verifyResult.total}</span>
                  <span className="text-emerald-300">Verified: {verifyResult.verified}</span>
                  {verifyResult.failed > 0 && (
                    <span className="text-red-300">Failed: {verifyResult.failed}</span>
                  )}
                </div>
              </div>
            )}
          </section>

          {/* Export */}
          <section className="rounded-lg border border-zinc-800 bg-zinc-950 p-5">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <Download size={20} className="text-cyan-300" />
                <h2 className="text-sm font-semibold text-zinc-100">Export Vault</h2>
              </div>
              <button
                onClick={handleExport}
                disabled={exporting}
                className="rounded-lg bg-cyan-600 px-3 py-1.5 text-xs font-medium text-white hover:bg-cyan-500 disabled:opacity-50"
              >
                {exporting ? <Loader2 size={14} className="animate-spin" /> : "Export"}
              </button>
            </div>
            {exportResult && (
              <div className="mt-3 space-y-2 text-xs">
                <div className="flex items-center gap-2">
                  <FileText size={14} className="text-zinc-500" />
                  <span className="text-zinc-300">Manifest: {exportResult.manifest_path}</span>
                </div>
                {exportResult.package_path && (
                  <div className="flex items-center gap-2">
                    <Download size={14} className="text-zinc-500" />
                    <span className="text-zinc-300">Package: {exportResult.package_path}</span>
                  </div>
                )}
                <div className="text-zinc-500">
                  {exportResult.evidence_count} items, {formatBytes(exportResult.storage_bytes)}
                </div>
              </div>
            )}
          </section>

          {/* Warning */}
          {sealStatus?.sealed && (
            <section className="rounded-lg border border-amber-900/50 bg-amber-950/20 p-4">
              <div className="flex items-start gap-2">
                <AlertTriangle size={16} className="mt-0.5 text-amber-300 shrink-0" />
                <div className="text-xs text-amber-200">
                  <strong>Vault is sealed.</strong> No new evidence can be added. To unseal,
                  you must manually restore filesystem permissions and remove the seal file.
                </div>
              </div>
            </section>
          )}
        </div>
      </main>
    </div>
  );
}
