import type {
  DraftResult,
  ExperienceDocument,
  EvaluationResult,
  OutreachSession,
  PipelineCandidateDetail,
  UserGoal,
} from '../types/api';

const API_BASE = 'http://localhost:8000';

async function jsonFetch<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    ...init,
    headers: {
      'Content-Type': 'application/json',
      ...(init?.headers ?? {}),
    },
  });
  if (!res.ok) {
    const body = await res.text();
    throw new Error(body || 'Request failed');
  }
  return res.json() as Promise<T>;
}

export async function uploadExperience(file: File): Promise<ExperienceDocument> {
  const form = new FormData();
  form.append('file', file);
  const res = await fetch(`${API_BASE}/context/upload`, { method: 'POST', body: form });
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}

export function startSession(experience_document_id: number, user_goal: UserGoal): Promise<OutreachSession> {
  return jsonFetch('/sessions', {
    method: 'POST',
    body: JSON.stringify({ experience_document_id, user_goal }),
  });
}

export function collectProfile(session_id: number, profile_url: string): Promise<PipelineCandidateDetail['candidate']> {
  return jsonFetch('/pipeline/collect', {
    method: 'POST',
    body: JSON.stringify({ session_id, profile_url }),
  });
}

export function evaluateCandidate(session_id: number, candidate_id: number): Promise<EvaluationResult> {
  return jsonFetch('/pipeline/evaluate', {
    method: 'POST',
    body: JSON.stringify({ session_id, candidate_id }),
  });
}

export function draftMessage(session_id: number, candidate_id: number): Promise<DraftResult> {
  return jsonFetch('/pipeline/draft', {
    method: 'POST',
    body: JSON.stringify({ session_id, candidate_id }),
  });
}

export function approveDraft(draft_id: number): Promise<{ status: string }> {
  return jsonFetch('/pipeline/approve', {
    method: 'POST',
    body: JSON.stringify({ draft_id }),
  });
}

export function sendDraft(draft_id: number): Promise<{ status: string }> {
  return jsonFetch('/pipeline/send', {
    method: 'POST',
    body: JSON.stringify({ draft_id }),
  });
}

export function listSessionCandidates(session_id: number): Promise<PipelineCandidateDetail[]> {
  return jsonFetch(`/history/sessions/${session_id}/candidates`);
}
