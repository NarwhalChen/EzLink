import { useEffect, useState } from 'react';
import {
  approveDraft,
  collectProfile,
  draftMessage,
  evaluateCandidate,
  listSessionCandidates,
  sendDraft,
} from '../api/client';
import { CandidateCard } from '../components/CandidateCard';
import type { PipelineCandidateDetail } from '../types/api';

export function ReviewPage() {
  const sessionId = Number(localStorage.getItem('sessionId'));
  const [items, setItems] = useState<PipelineCandidateDetail[]>([]);
  const [index, setIndex] = useState(0);
  const [profileUrl, setProfileUrl] = useState('https://example.com/profile');
  const current = items[index];

  async function refresh() {
    if (!sessionId) return;
    const data = await listSessionCandidates(sessionId);
    setItems(data);
  }

  useEffect(() => {
    refresh();
  }, []);

  async function runCollect() {
    const candidate = await collectProfile(sessionId, profileUrl);
    await evaluateCandidate(sessionId, candidate.id);
    try {
      await draftMessage(sessionId, candidate.id);
    } catch {
      // expected when not contactable
    }
    await refresh();
  }

  async function regenerateDraft() {
    if (!current) return;
    await draftMessage(sessionId, current.candidate.id);
    await refresh();
  }

  async function approve() {
    if (!current) return;
    if (!current.draft_id) return;
    await approveDraft(current.draft_id);
    await refresh();
  }

  async function approveAndSend() {
    if (!current) return;
    if (!current.draft_id) return;
    await approveDraft(current.draft_id);
    await sendDraft(current.draft_id);
    await refresh();
  }

  return (
    <div>
      <h2>Review</h2>
      <div className="panel actions">
        <input value={profileUrl} onChange={(e) => setProfileUrl(e.target.value)} placeholder="Profile URL" />
        <button onClick={runCollect}>Collect Pipeline</button>
        <button onClick={() => setIndex((i) => Math.max(0, i - 1))}>Skip</button>
        <button onClick={regenerateDraft}>Regenerate Draft</button>
        <button onClick={approve}>Approve</button>
        <button onClick={approveAndSend}>Approve & Send</button>
        <button onClick={() => setIndex((i) => Math.min(items.length - 1, i + 1))}>Next</button>
      </div>
      <CandidateCard item={current} />
    </div>
  );
}
