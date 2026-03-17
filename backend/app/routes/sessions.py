"""Routes for creating and retrieving outreach sessions."""

import json

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_db
from app.models import ExperienceDocument, OutreachSession as OutreachSessionModel
from app.schemas import CreateSessionRequest, OutreachSession
from app.utils.logging import get_logger

logger = get_logger(__name__)
router = APIRouter(prefix="/sessions", tags=["sessions"])


def _deserialise_session(record: OutreachSessionModel) -> OutreachSession:
    """Build an OutreachSession schema from the ORM model."""
    from app.schemas import UserGoal

    return OutreachSession(
        id=record.id,
        user_goal=UserGoal(**json.loads(record.user_goal)),
        experience_document_id=record.experience_document_id,
        created_at=record.created_at,
    )


@router.post(
    "",
    response_model=OutreachSession,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new outreach session",
)
async def create_session(
    body: CreateSessionRequest,
    db: AsyncSession = Depends(get_db),
) -> OutreachSession:
    """Create an OutreachSession linking a UserGoal to an ExperienceDocument."""
    # Verify the document exists.
    doc_result = await db.execute(
        select(ExperienceDocument).where(
            ExperienceDocument.id == body.experience_document_id
        )
    )
    if doc_result.scalar_one_or_none() is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"ExperienceDocument {body.experience_document_id} not found.",
        )

    record = OutreachSessionModel(
        user_goal=body.user_goal.model_dump_json(),
        experience_document_id=body.experience_document_id,
    )
    db.add(record)
    await db.commit()
    await db.refresh(record)
    logger.info("Created OutreachSession id=%d.", record.id)
    return _deserialise_session(record)


@router.get(
    "/{session_id}",
    response_model=OutreachSession,
    summary="Get outreach session details",
)
async def get_session(
    session_id: int,
    db: AsyncSession = Depends(get_db),
) -> OutreachSession:
    result = await db.execute(
        select(OutreachSessionModel).where(OutreachSessionModel.id == session_id)
    )
    record = result.scalar_one_or_none()
    if record is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"OutreachSession {session_id} not found.",
        )
    return _deserialise_session(record)
