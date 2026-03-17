"""Routes: draft and update outreach messages."""

import json

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_db
from app.models import CandidateRecord as CandidateRecordModel
from app.routes._helpers import deserialise_candidate
from app.schemas import (
    CandidateProfile,
    CandidateRecord,
    DraftResult,
    EvaluationResult,
    UpdateDraftRequest,
)
from app.services.context_loader import load_context
from app.services.message_drafter import draft_message
from app.utils.logging import get_logger

logger = get_logger(__name__)
router = APIRouter(prefix="/draft", tags=["draft"])


async def _fetch_record(candidate_id: int, db: AsyncSession) -> CandidateRecordModel:
    result = await db.execute(
        select(CandidateRecordModel).where(CandidateRecordModel.id == candidate_id)
    )
    record = result.scalar_one_or_none()
    if record is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"CandidateRecord {candidate_id} not found.",
        )
    return record


@router.post(
    "/{candidate_id}",
    response_model=CandidateRecord,
    summary="Generate a draft outreach message for a candidate",
)
async def create_draft(
    candidate_id: int,
    db: AsyncSession = Depends(get_db),
) -> CandidateRecord:
    """Draft a personalised message using the profile and evaluation."""
    record = await _fetch_record(candidate_id, db)

    if record.profile_data is None:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Profile data missing. Run /collect first.",
        )
    if record.evaluation is None:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Evaluation missing. Run /evaluate first.",
        )

    ctx = await load_context(record.session_id, db)
    profile = CandidateProfile(**json.loads(record.profile_data))
    evaluation = EvaluationResult(**json.loads(record.evaluation))

    result_draft = await draft_message(
        profile, evaluation, ctx["user_goal"], ctx["experience_markdown"]
    )

    record.draft = result_draft.model_dump_json()
    await db.commit()
    await db.refresh(record)
    logger.info("Draft created for candidate %d.", candidate_id)
    return deserialise_candidate(record)


@router.put(
    "/{candidate_id}",
    response_model=CandidateRecord,
    summary="Update (replace) the draft message for a candidate",
)
async def update_draft(
    candidate_id: int,
    body: UpdateDraftRequest,
    db: AsyncSession = Depends(get_db),
) -> CandidateRecord:
    """Allow the user to manually edit and save the draft message."""
    record = await _fetch_record(candidate_id, db)

    if record.draft is None:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="No existing draft found. Run POST /draft/{candidate_id} first.",
        )

    existing_draft = DraftResult(**json.loads(record.draft))
    existing_draft.message_draft = body.message_draft
    record.draft = existing_draft.model_dump_json()

    await db.commit()
    await db.refresh(record)
    logger.info("Draft updated for candidate %d.", candidate_id)
    return deserialise_candidate(record)
