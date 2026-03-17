import { useState } from "react";
import EvaluationPanel from "./EvaluationPanel";
import DraftPanel from "./DraftPanel";
import type { CandidateRecord, DraftResult } from "../types/api";

interface Props {
  candidate: CandidateRecord;
  onSkip: () => void;
  onRegenerateDraft: () => void;
  onApprove: () => void;
  onApproveAndSend: () => void;
  onNext: () => void;
  onDraftUpdated?: (draft: DraftResult) => void;
}

export default function CandidateCard({
  candidate,
  onSkip,
  onRegenerateDraft,
  onApprove,
  onApproveAndSend,
  onNext,
  onDraftUpdated,
}: Props) {
  const [showDetails, setShowDetails] = useState(false);
  const profile = candidate.profile_data;

  const extractionPct = profile ? Math.round(profile.extraction_confidence * 100) : 0;

  function confidenceClass(n: number) {
    if (n >= 0.7) return "high";
    if (n >= 0.4) return "medium";
    return "low";
  }

  return (
    <div className="swipe-card">
      {/* Header */}
      <div className="swipe-card-header">
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start" }}>
          <div>
            <div className="swipe-card-name">
              {profile?.name ?? "Unknown Candidate"}
            </div>
            <div className="swipe-card-title">
              {profile?.title ?? "—"}
              {profile?.company ? ` @ ${profile.company}` : ""}
            </div>
            <div className="swipe-card-meta">
              {profile?.location && <span>📍 {profile.location}</span>}
              <span>🌐 {profile?.platform ?? "Unknown"}</span>
              {candidate.approved && <span>✓ Approved</span>}
              {candidate.sent && <span>✉ Sent</span>}
            </div>
          </div>
          {candidate.evaluation && (
            <span className={`badge badge-${candidate.evaluation.priority}`} style={{ fontSize: "0.75rem" }}>
              {candidate.evaluation.priority.toUpperCase()}
            </span>
          )}
        </div>

        {/* Extraction confidence */}
        {profile && (
          <div className="confidence-wrap" style={{ marginTop: "0.75rem" }}>
            <div className="confidence-label" style={{ color: "rgba(255,255,255,0.7)" }}>
              <span>Extraction confidence</span>
              <span>{extractionPct}%</span>
            </div>
            <div className="confidence-bar" style={{ background: "rgba(255,255,255,0.25)" }}>
              <div
                className={`confidence-fill ${confidenceClass(profile.extraction_confidence)}`}
                style={{ width: `${extractionPct}%`, background: "rgba(255,255,255,0.9)" }}
              />
            </div>
          </div>
        )}
      </div>

      {/* Body */}
      <div className="swipe-card-body">
        <a
          href={candidate.profile_url}
          target="_blank"
          rel="noreferrer"
          style={{ fontSize: "0.78rem", color: "var(--color-primary)", wordBreak: "break-all" }}
        >
          {candidate.profile_url}
        </a>

        {profile?.about && (
          <div style={{ marginTop: "0.85rem" }}>
            <div className="section-label">About</div>
            <p style={{ fontSize: "0.875rem", lineHeight: 1.6, color: "var(--color-text)" }}>
              {profile.about}
            </p>
          </div>
        )}

        {profile?.skills && profile.skills.length > 0 && (
          <div style={{ marginTop: "0.85rem" }}>
            <div className="section-label">Skills</div>
            <div className="tag-list">
              {profile.skills.map((s, i) => <span key={i} className="tag">{s}</span>)}
            </div>
          </div>
        )}

        {profile?.mutual_signals && profile.mutual_signals.length > 0 && (
          <div style={{ marginTop: "0.85rem" }}>
            <div className="section-label">Mutual Signals</div>
            <div className="tag-list">
              {profile.mutual_signals.map((s, i) => (
                <span key={i} className="tag tag-signal">✦ {s}</span>
              ))}
            </div>
          </div>
        )}

        {/* Collapsible details */}
        <button
          className="btn btn-ghost btn-sm"
          style={{ marginTop: "0.75rem", padding: "0.25rem 0" }}
          onClick={() => setShowDetails((v) => !v)}
        >
          {showDetails ? "▲ Hide details" : "▼ Show education & experience"}
        </button>

        {showDetails && profile && (
          <div style={{ marginTop: "0.75rem" }}>
            {profile.education.length > 0 && (
              <div>
                <div className="section-label">Education</div>
                <ul style={{ paddingLeft: "1.2rem", fontSize: "0.875rem", color: "var(--color-text)", lineHeight: 1.8 }}>
                  {profile.education.map((e, i) => <li key={i}>{e}</li>)}
                </ul>
              </div>
            )}
            {profile.experience.length > 0 && (
              <div style={{ marginTop: "0.75rem" }}>
                <div className="section-label">Experience</div>
                <ul style={{ paddingLeft: "1.2rem", fontSize: "0.875rem", color: "var(--color-text)", lineHeight: 1.8 }}>
                  {profile.experience.map((e, i) => <li key={i}>{e}</li>)}
                </ul>
              </div>
            )}
            {profile.recent_activity && (
              <div style={{ marginTop: "0.75rem" }}>
                <div className="section-label">Recent Activity</div>
                <p style={{ fontSize: "0.875rem", lineHeight: 1.6, color: "var(--color-text)" }}>
                  {profile.recent_activity}
                </p>
              </div>
            )}
          </div>
        )}

        {/* Evaluation */}
        {candidate.evaluation && (
          <div style={{ marginTop: "1rem" }}>
            <hr className="divider" style={{ margin: "1rem 0" }} />
            <div className="section-label" style={{ marginBottom: 0 }}>Evaluation</div>
            <EvaluationPanel evaluation={candidate.evaluation} />
          </div>
        )}

        {/* Draft */}
        {candidate.draft && candidate.id !== undefined && (
          <div style={{ marginTop: "1rem" }}>
            <hr className="divider" style={{ margin: "1rem 0" }} />
            <div className="section-label" style={{ marginBottom: 0 }}>Draft Message</div>
            <DraftPanel
              draft={candidate.draft}
              candidateId={candidate.id}
              onUpdated={(d) => onDraftUpdated?.(d)}
            />
          </div>
        )}
      </div>

      {/* Actions */}
      <div className="swipe-card-actions">
        <button className="btn btn-ghost" onClick={onSkip} title="Skip this candidate">
          ✕ Skip
        </button>
        <button className="btn btn-outline" onClick={onRegenerateDraft} title="Regenerate draft">
          ↺ Regenerate Draft
        </button>
        <button
          className="btn btn-success-outline"
          onClick={onApprove}
          disabled={candidate.approved}
        >
          ✓ Approve
        </button>
        <button
          className="btn btn-success"
          onClick={onApproveAndSend}
          disabled={candidate.sent}
        >
          ✉ Approve &amp; Send
        </button>
        <button className="btn btn-secondary" onClick={onNext} style={{ marginLeft: "auto" }}>
          Next →
        </button>
      </div>
    </div>
  );
}
