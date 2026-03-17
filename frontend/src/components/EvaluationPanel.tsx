import type { EvaluationResult } from "../types/api";

interface Props {
  evaluation: EvaluationResult;
}

function confidenceClass(n: number) {
  if (n >= 0.7) return "high";
  if (n >= 0.4) return "medium";
  return "low";
}

export default function EvaluationPanel({ evaluation }: Props) {
  const pct = Math.round(evaluation.confidence * 100);
  const cls = confidenceClass(evaluation.confidence);

  return (
    <div className="eval-panel">
      <div className="eval-row">
        <span style={{ fontSize: "0.82rem", color: "var(--color-text-muted)", fontWeight: 600 }}>
          Contact?
        </span>
        <span className={`badge badge-${evaluation.should_contact ? "yes" : "no"}`}>
          {evaluation.should_contact ? "✓ Yes" : "✗ No"}
        </span>

        <span style={{ fontSize: "0.82rem", color: "var(--color-text-muted)", fontWeight: 600, marginLeft: "0.5rem" }}>
          Priority
        </span>
        <span className={`badge badge-${evaluation.priority}`}>
          {evaluation.priority.toUpperCase()}
        </span>
      </div>

      <div className="confidence-wrap">
        <div className="confidence-label">
          <span>Confidence</span>
          <span>{pct}%</span>
        </div>
        <div className="confidence-bar">
          <div className={`confidence-fill ${cls}`} style={{ width: `${pct}%` }} />
        </div>
      </div>

      <p className="eval-reason">{evaluation.reason_to_contact}</p>

      {evaluation.common_points.length > 0 && (
        <div>
          <div className="section-label">Common Ground</div>
          <div className="tag-list">
            {evaluation.common_points.map((p, i) => (
              <span key={i} className="tag tag-signal">
                ✦ {p}
              </span>
            ))}
          </div>
        </div>
      )}

      {evaluation.risk_flags.length > 0 && (
        <div style={{ marginTop: "0.75rem" }}>
          <div className="section-label">Risk Flags</div>
          <div className="tag-list">
            {evaluation.risk_flags.map((f, i) => (
              <span key={i} className="tag tag-warning">
                ⚠ {f}
              </span>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
