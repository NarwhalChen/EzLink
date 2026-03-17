import type { DraftResult } from '../types/api';

export function DraftPanel({ draft }: { draft?: DraftResult }) {
  if (!draft) return <div className="panel">No draft yet.</div>;
  return (
    <div className="panel">
      <h4>Draft</h4>
      <p>{draft.message_draft}</p>
      <p>Tone: {draft.tone}</p>
      <p>Confidence: {draft.confidence}</p>
    </div>
  );
}
