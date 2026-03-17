import { useEffect, useState } from 'react';
import { listSessionCandidates } from '../api/client';
import type { PipelineCandidateDetail } from '../types/api';

export function HistoryPage() {
  const [items, setItems] = useState<PipelineCandidateDetail[]>([]);
  const sessionId = Number(localStorage.getItem('sessionId'));

  useEffect(() => {
    if (!sessionId) return;
    listSessionCandidates(sessionId).then(setItems);
  }, [sessionId]);

  return (
    <div>
      <h2>History</h2>
      {items.map((item) => (
        <div className="panel" key={item.candidate.id}>
          <p>
            {item.candidate.profile.name} - {item.candidate.profile.title} @ {item.candidate.profile.company}
          </p>
          <p>Should contact: {String(item.evaluation?.should_contact)}</p>
          <p>Approved: {String(item.approved)} | Sent: {String(item.sent)}</p>
        </div>
      ))}
    </div>
  );
}
