"""SQLAlchemy ORM models.

JSON fields are stored as TEXT in SQLite and serialised / deserialised manually.
"""

from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class ExperienceDocument(Base):
    """Uploaded experience / resume document stored as Markdown."""

    __tablename__ = "experience_documents"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    filename: Mapped[str] = mapped_column(Text, nullable=False)
    markdown_content: Mapped[str] = mapped_column(Text, nullable=False)
    uploaded_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utcnow, nullable=False
    )

    sessions: Mapped[list["OutreachSession"]] = relationship(
        "OutreachSession", back_populates="experience_document"
    )


class OutreachSession(Base):
    """Groups a user goal with an experience document to drive a campaign."""

    __tablename__ = "outreach_sessions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    # Serialised UserGoal JSON
    user_goal: Mapped[str] = mapped_column(Text, nullable=False)
    experience_document_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("experience_documents.id"), nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utcnow, nullable=False
    )

    experience_document: Mapped["ExperienceDocument"] = relationship(
        "ExperienceDocument", back_populates="sessions"
    )
    candidates: Mapped[list["CandidateRecord"]] = relationship(
        "CandidateRecord", back_populates="session"
    )


class CandidateRecord(Base):
    """A single lead/candidate discovered and processed within a session."""

    __tablename__ = "candidate_records"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    session_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("outreach_sessions.id"), nullable=False
    )
    profile_url: Mapped[str] = mapped_column(Text, nullable=False)
    # Serialised JSON blobs — None until each pipeline step runs.
    profile_data: Mapped[str | None] = mapped_column(Text, nullable=True)
    evaluation: Mapped[str | None] = mapped_column(Text, nullable=True)
    draft: Mapped[str | None] = mapped_column(Text, nullable=True)
    approved: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    sent: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utcnow, nullable=False
    )

    session: Mapped["OutreachSession"] = relationship(
        "OutreachSession", back_populates="candidates"
    )
