import { useState, useEffect, useCallback } from "react";
import CandidateCard from "../components/CandidateCard";
import {
  listCandidates,
  collectProfile,
  evaluateCandidate,
  draftMessage,
  approveCandidate,
  sendMessage,
} from "../api/client";
import type { CandidateRecord, DraftResult } from "../types/api";

export default function ReviewPage() {
  const [candidates, setCandidates] = useState<CandidateRecord[]>([]);
  const [index, setIndex] = useState(0);
  const [loading, setLoading] = useState(true);
  const [actionLoading, setActionLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [newUrl, setNewUrl] = useState("");
  const [collectStatus, setCollectStatus] = useState<string | null>(null);

  const sessionId = Number(localStorage.getItem("ezlink_session_id") ?? "0") || undefined;

  const loadCandidates = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await listCandidates(sessionId);
      setCandidates(data);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Failed to load candidates");
    } finally {
      setLoading(false);
    }
  }, [sessionId]);

  useEffect(() => {
    loadCandidates();
  }, [loadCandidates]);

  const current = candidates[index];

  function updateCurrent(updated: CandidateRecord) {
    setCandidates((prev) => prev.map((c) => (c.id === updated.id ? updated : c)));
  }

  async function handleCollectAndEvaluate() {
    const url = newUrl.trim();
    if (!url) return;
    if (!sessionId) {
      setError("No active session. Go to Setup first.");
      return;
    }
    setActionLoading(true);
    setError(null);
    setCollectStatus("Collecting profile…");
    try {
      const collected = await collectProfile(url, sessionId);
      setCollectStatus("Evaluating…");
      await evaluateCandidate(collected.id!);
      setCollectStatus("Drafting message…");
      const drafted = await draftMessage(collected.id!);
      setCandidates((prev) => [...prev, drafted]);
      setIndex(candidates.length);
      setNewUrl("");
      setCollectStatus(null);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Pipeline failed");
      setCollectStatus(null);
    } finally {
      setActionLoading(false);
    }
  }

  async function handleRegenerateDraft() {
    if (!current?.id) return;
    setActionLoading(true);
    setError(null);
    try {
      const updated = await draftMessage(current.id);
      updateCurrent(updated);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Draft regeneration failed");
    } finally {
      setActionLoading(false);
    }
  }

  async function handleApprove() {
    if (!current?.id) return;
    setActionLoading(true);
    setError(null);
    try {
      const updated = await approveCandidate(current.id);
      updateCurrent(updated);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Approval failed");
    } finally {
      setActionLoading(false);
    }
  }

  async function handleApproveAndSend() {
    if (!current?.id) return;
    setActionLoading(true);
    setError(null);
    try {
      const approved = await approveCandidate(current.id);
      const sent = await sendMessage(approved.id!);
      updateCurrent(sent);
      goNext();
    } catch (e) {
      setError(e instanceof Error ? e.message : "Send failed");
    } finally {
      setActionLoading(false);
    }
  }

  function goNext() {
    setIndex((i) => Math.min(i + 1, candidates.length - 1));
  }

  function handleSkip() {
    goNext();
  }

  function handleDraftUpdated(draft: DraftResult) {
    if (!current) return;
    updateCurrent({ ...current, draft });
  }

  if (loading) {
    return (
      <div className="page">
        <div className="loading-overlay">
          <div className="loading-spinner" />
          <p>Loading candidates…</p>
        </div>
      </div>
    );
  }

  return (
    <div className="page">
      <h1 className="page-title">Review Candidates</h1>
      <p className="page-subtitle">Evaluate, approve, and send personalised outreach messages</p>

      {/* Add new URL */}
      <div className="card" style={{ marginBottom: "1.5rem" }}>
        <div className="card-title" style={{ marginBottom: "0.75rem" }}>Add Profile to Pipeline</div>
        <div style={{ display: "flex", gap: "0.6rem", flexWrap: "wrap" }}>
          <input
            className="form-input"
            style={{ flex: 1, minWidth: 200 }}
            value={newUrl}
            onChange={(e) => setNewUrl(e.target.value)}
            placeholder="https://www.linkedin.com/in/username"
            disabled={actionLoading}
            onKeyDown={(e) => { if (e.key === "Enter") handleCollectAndEvaluate(); }}
          />
          <button
            className="btn btn-primary"
            onClick={handleCollectAndEvaluate}
            disabled={actionLoading || !newUrl.trim()}
          >
            {actionLoading && collectStatus ? (
              <><span className="loading-spinner" style={{ width: 14, height: 14 }} /> {collectStatus}</>
            ) : "Collect & Evaluate"}
          </button>
        </div>
        {!sessionId && (
          <div className="alert alert-info" style={{ marginTop: "0.75rem" }}>
            No active session. Complete Setup first to start a pipeline.
          </div>
        )}
      </div>

      {error && (
        <div className="alert alert-error" style={{ marginBottom: "1rem" }}>⚠ {error}</div>
      )}

      {candidates.length === 0 ? (
        <div className="empty-state">
          <div className="empty-state-icon">📭</div>
          <div className="empty-state-title">No candidates yet</div>
          <div className="empty-state-desc">
            Add profile URLs above or go to Setup to run the pipeline.
          </div>
        </div>
      ) : (
        <>
          {/* Progress */}
          <div className="progress-bar-wrap">
            <span className="progress-text">
              {index + 1} / {candidates.length}
            </span>
            <div className="progress-bar">
              <div
                className="progress-fill"
                style={{ width: `${((index + 1) / candidates.length) * 100}%` }}
              />
            </div>
            <button className="btn btn-ghost btn-sm" onClick={loadCandidates}>
              ↻ Refresh
            </button>
          </div>

          {current && (
            <CandidateCard
              candidate={current}
              onSkip={handleSkip}
              onRegenerateDraft={handleRegenerateDraft}
              onApprove={handleApprove}
              onApproveAndSend={handleApproveAndSend}
              onNext={goNext}
              onDraftUpdated={handleDraftUpdated}
            />
          )}

          {/* Thumbnail nav */}
          <div style={{ display: "flex", gap: "0.4rem", marginTop: "1.25rem", flexWrap: "wrap", justifyContent: "center" }}>
            {candidates.map((c, i) => (
              <button
                key={c.id ?? i}
                onClick={() => setIndex(i)}
                style={{
                  width: 32,
                  height: 32,
                  borderRadius: "50%",
                  border: "2px solid",
                  borderColor: i === index ? "var(--color-primary)" : "var(--color-border)",
                  background: c.sent
                    ? "var(--color-success-light)"
                    : c.approved
                    ? "var(--color-primary-light)"
                    : "var(--color-surface)",
                  cursor: "pointer",
                  fontSize: "0.7rem",
                  fontWeight: 700,
                  color: i === index ? "var(--color-primary)" : "var(--color-text-muted)",
                }}
              >
                {i + 1}
              </button>
            ))}
          </div>
        </>
      )}
    </div>
  );
}
