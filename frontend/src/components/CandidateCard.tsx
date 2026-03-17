import type { PipelineCandidateDetail } from '../types/api';
import { DraftPanel } from './DraftPanel';
import { EvaluationPanel } from './EvaluationPanel';

export function CandidateCard({ item }: { item?: PipelineCandidateDetail }) {
  if (!item) return <div className="panel">No candidate loaded.</div>;

  const p = item.candidate.profile;
  return (
    <div className="card">
      <h3>{p.name}</h3>
      <p>
        {p.title} @ {p.company}
      </p>
      <p>{p.profile_url}</p>
      <p>{p.about}</p>
      <EvaluationPanel evaluation={item.evaluation} />
      <DraftPanel draft={item.draft} />
      <p>
        Approved: {String(item.approved)} | Sent: {String(item.sent)}
      </p>
    </div>
  );
}
