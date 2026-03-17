export interface UserGoal {
  primary_goal: string;
  target_roles: string[];
  target_companies: string[];
  preferred_contact_types: string[];
  avoid_contact_types: string[];
  user_background: Record<string, unknown>;
  outreach_style: Record<string, unknown>;
}

export interface ExperienceDocument {
  id?: number;
  filename: string;
  markdown_content: string;
  uploaded_at?: string;
}

export interface OutreachSession {
  id?: number;
  user_goal: UserGoal;
  experience_document_id: number;
  created_at?: string;
}

export interface CandidateProfile {
  name: string;
  platform: string;
  title: string;
  company: string;
  location?: string;
  about?: string;
  recent_activity?: string;
  education: string[];
  experience: string[];
  skills: string[];
  mutual_signals: string[];
  profile_url: string;
  extraction_confidence: number;
}

export interface EvaluationResult {
  should_contact: boolean;
  priority: "high" | "medium" | "low";
  confidence: number;
  reason_to_contact: string;
  common_points: string[];
  risk_flags: string[];
}

export interface DraftResult {
  message_draft: string;
  tone: string;
  personalization_used: string[];
  confidence: number;
}

export interface CandidateRecord {
  id?: number;
  session_id: number;
  profile_url: string;
  profile_data?: CandidateProfile;
  evaluation?: EvaluationResult;
  draft?: DraftResult;
  approved: boolean;
  sent: boolean;
  created_at?: string;
}
