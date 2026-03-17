import { useState, useEffect, useCallback } from "react";
import { listCandidates } from "../api/client";
import EvaluationPanel from "../components/EvaluationPanel";
import DraftPanel from "../components/DraftPanel";
import type { CandidateRecord, DraftResult } from "../types/api";

type StatusFilter = "all" | "evaluated" | "drafted" | "approved" | "sent";

function statusLabel(c: CandidateRecord): string {
  if (c.sent) return "sent";
  if (c.approved) return "approved";
  if (c.draft) return "drafted";
  if (c.evaluation) return "evaluated";
  return "collected";
}

function statusBadge(c: CandidateRecord) {
  const s = statusLabel(c);
  const cls: Record<string, string> = {
    sent: "badge-yes",
    approved: "badge-primary",
    drafted: "badge-neutral",
    evaluated: "badge-neutral",
    collected: "badge-neutral",
  };
  return <span className={`badge ${cls[s] ?? "badge-neutral"}`}>{s}</span>;
}

export default function HistoryPage() {
  const [candidates, setCandidates] = useState<CandidateRecord[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [filter, setFilter] = useState<StatusFilter>("all");
  const [expandedId, setExpandedId] = useState<number | null>(null);

  const load = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await listCandidates();
      setCandidates(data);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Failed to load");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    load();
  }, [load]);

  function updateCandidate(updated: CandidateRecord) {
    setCandidates((prev) => prev.map((c) => (c.id === updated.id ? updated : c)));
  }

  const filtered = candidates.filter((c) => {
    if (filter === "all") return true;
    return statusLabel(c) === filter;
  });

  const filterOptions: { value: StatusFilter; label: string }[] = [
    { value: "all", label: `All (${candidates.length})` },
    { value: "sent", label: `Sent (${candidates.filter((c) => c.sent).length})` },
    { value: "approved", label: `Approved (${candidates.filter((c) => c.approved && !c.sent).length})` },
    { value: "drafted", label: `Drafted (${candidates.filter((c) => !!c.draft && !c.approved).length})` },
    { value: "evaluated", label: `Evaluated (${candidates.filter((c) => !!c.evaluation && !c.draft).length})` },
  ];

  return (
    <div className="page-wide">
      <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: "0.4rem", flexWrap: "wrap", gap: "0.5rem" }}>
        <div>
          <h1 className="page-title">History</h1>
          <p className="page-subtitle">All collected candidates across sessions</p>
        </div>
        <button className="btn btn-secondary" onClick={load} disabled={loading}>
          {loading ? <><span className="loading-spinner" style={{ width: 14, height: 14 }} /> Loading…</> : "↻ Refresh"}
        </button>
      </div>

      {error && <div className="alert alert-error" style={{ marginBottom: "1rem" }}>⚠ {error}</div>}

      <div className="filter-bar">
        <span className="filter-label">Filter:</span>
        {filterOptions.map((opt) => (
          <button
            key={opt.value}
            className={`btn btn-sm ${filter === opt.value ? "btn-primary" : "btn-secondary"}`}
            onClick={() => setFilter(opt.value)}
          >
            {opt.label}
          </button>
        ))}
      </div>

      {loading ? (
        <div className="loading-overlay">
          <div className="loading-spinner" />
          <p>Loading history…</p>
        </div>
      ) : filtered.length === 0 ? (
        <div className="empty-state">
          <div className="empty-state-icon">📋</div>
          <div className="empty-state-title">No candidates</div>
          <div className="empty-state-desc">
            {filter !== "all" ? "No candidates match this filter." : "Run the pipeline from Setup to collect candidates."}
          </div>
        </div>
      ) : (
        <div className="table-wrap">
          <table>
            <thead>
              <tr>
                <th>#</th>
                <th>Name</th>
                <th>Title / Company</th>
                <th>Priority</th>
                <th>Status</th>
                <th>Contact?</th>
                <th>Date</th>
              </tr>
            </thead>
            <tbody>
              {filtered.map((c, i) => {
                const expanded = expandedId === (c.id ?? i);
                return (
                  <>
                    <tr
                      key={c.id ?? i}
                      onClick={() => setExpandedId(expanded ? null : (c.id ?? i))}
                    >
                      <td style={{ color: "var(--color-text-muted)", fontSize: "0.78rem" }}>{i + 1}</td>
                      <td>
                        <strong>{c.profile_data?.name ?? "—"}</strong>
                        <br />
                        <a
                          href={c.profile_url}
                          target="_blank"
                          rel="noreferrer"
                          style={{ fontSize: "0.75rem", color: "var(--color-primary)" }}
                          onClick={(e) => e.stopPropagation()}
                        >
                          {c.profile_data?.platform ?? "Link"}
                        </a>
                      </td>
                      <td>
                        <div style={{ fontSize: "0.85rem" }}>{c.profile_data?.title ?? "—"}</div>
                        <div style={{ fontSize: "0.78rem", color: "var(--color-text-muted)" }}>
                          {c.profile_data?.company ?? "—"}
                        </div>
                      </td>
                      <td>
                        {c.evaluation ? (
                          <span className={`badge badge-${c.evaluation.priority}`}>
                            {c.evaluation.priority.toUpperCase()}
                          </span>
                        ) : (
                          <span className="badge badge-neutral">—</span>
                        )}
                      </td>
                      <td>{statusBadge(c)}</td>
                      <td>
                        {c.evaluation ? (
                          <span className={`badge badge-${c.evaluation.should_contact ? "yes" : "no"}`}>
                            {c.evaluation.should_contact ? "Yes" : "No"}
                          </span>
                        ) : (
                          <span className="badge badge-neutral">—</span>
                        )}
                      </td>
                      <td style={{ fontSize: "0.78rem", color: "var(--color-text-muted)", whiteSpace: "nowrap" }}>
                        {c.created_at
                          ? new Date(c.created_at).toLocaleDateString()
                          : "—"}
                      </td>
                    </tr>
                    {expanded && (
                      <tr key={`${c.id ?? i}-details`}>
                        <td colSpan={7} style={{ padding: 0 }}>
                          <div className="expanded-details">
                            {c.profile_data?.about && (
                              <p style={{ fontSize: "0.875rem", marginBottom: "0.75rem", lineHeight: 1.6 }}>
                                {c.profile_data.about}
                              </p>
                            )}
                            {c.profile_data?.skills && c.profile_data.skills.length > 0 && (
                              <div style={{ marginBottom: "0.75rem" }}>
                                <div className="section-label">Skills</div>
                                <div className="tag-list">
                                  {c.profile_data.skills.map((s, si) => (
                                    <span key={si} className="tag">{s}</span>
                                  ))}
                                </div>
                              </div>
                            )}
                            {c.evaluation && (
                              <div style={{ marginBottom: "0.75rem" }}>
                                <div className="section-label">Evaluation</div>
                                <EvaluationPanel evaluation={c.evaluation} />
                              </div>
                            )}
                            {c.draft && c.id !== undefined && (
                              <div>
                                <div className="section-label">Draft</div>
                                <DraftPanel
                                  draft={c.draft}
                                  candidateId={c.id}
                                  onUpdated={(draft: DraftResult) =>
                                    updateCandidate({ ...c, draft })
                                  }
                                />
                              </div>
                            )}
                          </div>
                        </td>
                      </tr>
                    )}
                  </>
                );
              })}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
