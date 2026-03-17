from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


class UserGoal(BaseModel):
    primary_goal: str
    target_roles: list[str] = Field(default_factory=list)
    target_companies: list[str] = Field(default_factory=list)
    preferred_contact_types: list[str] = Field(default_factory=list)
    avoid_contact_types: list[str] = Field(default_factory=list)
    user_background: dict = Field(default_factory=dict)
    outreach_style: dict = Field(default_factory=dict)


class ExperienceDocument(BaseModel):
    id: int | None = None
    filename: str
    markdown_content: str
    uploaded_at: datetime | None = None


class OutreachSession(BaseModel):
    id: int | None = None
    user_goal: UserGoal
    experience_document_id: int
    created_at: datetime | None = None


class CandidateProfile(BaseModel):
    name: str
    platform: str
    title: str
    company: str
    location: str | None = None
    about: str | None = None
    recent_activity: str | None = None
    education: list[str] = Field(default_factory=list)
    experience: list[str] = Field(default_factory=list)
    skills: list[str] = Field(default_factory=list)
    mutual_signals: list[str] = Field(default_factory=list)
    profile_url: str
    extraction_confidence: int


class EvaluationResult(BaseModel):
    should_contact: bool
    priority: Literal['high', 'medium', 'low']
    confidence: int
    reason_to_contact: str
    common_points: list[str] = Field(default_factory=list)
    risk_flags: list[str] = Field(default_factory=list)


class DraftResult(BaseModel):
    message_draft: str
    tone: str
    personalization_used: list[str] = Field(default_factory=list)
    confidence: int


class StartSessionRequest(BaseModel):
    user_goal: UserGoal
    experience_document_id: int


class CollectRequest(BaseModel):
    session_id: int
    profile_url: str


class EvaluateRequest(BaseModel):
    session_id: int
    candidate_id: int


class DraftRequest(BaseModel):
    session_id: int
    candidate_id: int


class ApproveRequest(BaseModel):
    draft_id: int


class SendRequest(BaseModel):
    draft_id: int


class CandidateRecord(BaseModel):
    id: int
    session_id: int
    created_at: datetime
    profile: CandidateProfile


class PipelineCandidateDetail(BaseModel):
    candidate: CandidateRecord
    evaluation: EvaluationResult | None = None
    draft: DraftResult | None = None
    draft_id: int | None = None
    approved: bool = False
    sent: bool = False
