import axios from "axios";
import type {
  ExperienceDocument,
  UserGoal,
  OutreachSession,
  CandidateRecord,
} from "../types/api";

const http = axios.create({ baseURL: "/api" });

export async function uploadExperience(file: File): Promise<ExperienceDocument> {
  const form = new FormData();
  form.append("file", file);
  const { data } = await http.post<ExperienceDocument>("/experience/upload", form, {
    headers: { "Content-Type": "multipart/form-data" },
  });
  return data;
}

export async function getCurrentExperience(): Promise<ExperienceDocument | null> {
  try {
    const { data } = await http.get<ExperienceDocument>("/experience/current");
    return data;
  } catch {
    return null;
  }
}

export async function createSession(
  goal: UserGoal,
  experienceDocId: number
): Promise<OutreachSession> {
  const { data } = await http.post<OutreachSession>("/sessions", {
    user_goal: goal,
    experience_document_id: experienceDocId,
  });
  return data;
}

export async function collectProfile(
  profileUrl: string,
  sessionId: number
): Promise<CandidateRecord> {
  const { data } = await http.post<CandidateRecord>("/candidates/collect", {
    profile_url: profileUrl,
    session_id: sessionId,
  });
  return data;
}

export async function evaluateCandidate(candidateId: number): Promise<CandidateRecord> {
  const { data } = await http.post<CandidateRecord>(`/candidates/${candidateId}/evaluate`);
  return data;
}

export async function draftMessage(candidateId: number): Promise<CandidateRecord> {
  const { data } = await http.post<CandidateRecord>(`/candidates/${candidateId}/draft`);
  return data;
}

export async function updateDraft(
  candidateId: number,
  messageDraft: string
): Promise<CandidateRecord> {
  const { data } = await http.patch<CandidateRecord>(`/candidates/${candidateId}/draft`, {
    message_draft: messageDraft,
  });
  return data;
}

export async function approveCandidate(candidateId: number): Promise<CandidateRecord> {
  const { data } = await http.post<CandidateRecord>(`/candidates/${candidateId}/approve`);
  return data;
}

export async function sendMessage(candidateId: number): Promise<CandidateRecord> {
  const { data } = await http.post<CandidateRecord>(`/candidates/${candidateId}/send`);
  return data;
}

export async function listCandidates(sessionId?: number): Promise<CandidateRecord[]> {
  const params = sessionId !== undefined ? { session_id: sessionId } : {};
  const { data } = await http.get<CandidateRecord[]>("/candidates", { params });
  return data;
}

export async function getCandidate(candidateId: number): Promise<CandidateRecord> {
  const { data } = await http.get<CandidateRecord>(`/candidates/${candidateId}`);
  return data;
}


