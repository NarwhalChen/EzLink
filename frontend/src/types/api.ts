export type UserGoal = {
  primary_goal: string;
  target_roles: string[];
  target_companies: string[];
  preferred_contact_types: string[];
  avoid_contact_types: string[];
  user_background: Record<string, string>;
  outreach_style: Record<string, string>;
};

export type ExperienceDocument = {
  id: number;
  filename: string;
  markdown_content: string;
  uploaded_at: string;
};

export type OutreachSession = {
  id: number;
  user_goal: UserGoal;
  experience_document_id: number;
  created_at: string;
};

export type CandidateProfile = {
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
};

export type EvaluationResult = {
  should_contact: boolean;
  priority: 'high' | 'medium' | 'low';
  confidence: number;
  reason_to_contact: string;
  common_points: string[];
  risk_flags: string[];
};

export type DraftResult = {
  message_draft: string;
  tone: string;
  personalization_used: string[];
  confidence: number;
};

export type PipelineCandidateDetail = {
  candidate: {
    id: number;
    session_id: number;
    created_at: string;
    profile: CandidateProfile;
  };
  evaluation?: EvaluationResult;
  draft?: DraftResult;
  draft_id?: number;
  approved: boolean;
  sent: boolean;
};
