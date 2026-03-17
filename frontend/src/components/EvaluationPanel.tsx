import type { EvaluationResult } from '../types/api';

export function EvaluationPanel({ evaluation }: { evaluation?: EvaluationResult }) {
  if (!evaluation) return <div className="panel">No evaluation yet.</div>;
  return (
    <div className="panel">
      <h4>Evaluation</h4>
      <p>
        <strong>Contact:</strong> {evaluation.should_contact ? 'Yes' : 'No'} ({evaluation.priority})
      </p>
      <p>{evaluation.reason_to_contact}</p>
      <p>Confidence: {evaluation.confidence}</p>
      <p>Common points: {evaluation.common_points.join(', ') || 'None'}</p>
      <p>Risk flags: {evaluation.risk_flags.join(', ') || 'None'}</p>
    </div>
  );
}
