"""Pydantic v2 request / response schemas."""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict


class UserGoal(BaseModel):
    primary_goal: str
    target_roles: list[str] = []
    target_companies: list[str] = []
    preferred_contact_types: list[str] = []
    avoid_contact_types: list[str] = []
    user_background: dict[str, Any] = {}
    outreach_style: dict[str, Any] = {}


class ExperienceDocument(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int | None = None
    filename: str
    markdown_content: str
    uploaded_at: datetime | None = None


class OutreachSession(BaseModel):
    model_config = ConfigDict(from_attributes=True)

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
    education: list[str] = []
    experience: list[str] = []
    skills: list[str] = []
    mutual_signals: list[str] = []
    profile_url: str
    extraction_confidence: int


class EvaluationResult(BaseModel):
    should_contact: bool
    priority: str  # "high" | "medium" | "low"
    confidence: int
    reason_to_contact: str
    common_points: list[str]
    risk_flags: list[str]


class DraftResult(BaseModel):
    message_draft: str
    tone: str
    personalization_used: list[str]
    confidence: int


class CandidateRecord(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int | None = None
    session_id: int
    profile_url: str
    profile_data: CandidateProfile | None = None
    evaluation: EvaluationResult | None = None
    draft: DraftResult | None = None
    approved: bool = False
    sent: bool = False
    created_at: datetime | None = None


# ---------- Request bodies ----------

class CreateSessionRequest(BaseModel):
    user_goal: UserGoal
    experience_document_id: int


class CollectRequest(BaseModel):
    platform: str  # e.g. "linkedin", "github", "twitter"
    session_id: int
    max_candidates: int = 5


class UpdateDraftRequest(BaseModel):
    message_draft: str
