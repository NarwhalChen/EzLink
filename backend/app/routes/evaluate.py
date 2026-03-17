"""Route: evaluate a collected candidate."""

import json

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_db
from app.models import CandidateRecord as CandidateRecordModel
from app.routes._helpers import deserialise_candidate
from app.schemas import CandidateProfile, CandidateRecord
from app.services.context_loader import load_context
from app.services.lead_evaluator import evaluate_candidate
from app.utils.logging import get_logger

logger = get_logger(__name__)
router = APIRouter(prefix="/evaluate", tags=["evaluate"])


@router.post(
    "/{candidate_id}",
    response_model=CandidateRecord,
    summary="Evaluate a candidate against the session goal",
)
async def evaluate(
    candidate_id: int,
    db: AsyncSession = Depends(get_db),
) -> CandidateRecord:
    """Run the evaluator for the given candidate and persist the result."""
    result = await db.execute(
        select(CandidateRecordModel).where(CandidateRecordModel.id == candidate_id)
    )
    record = result.scalar_one_or_none()
    if record is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"CandidateRecord {candidate_id} not found.",
        )
    if record.profile_data is None:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Profile data not collected yet. Run /collect first.",
        )

    ctx = await load_context(record.session_id, db)
    profile = CandidateProfile(**json.loads(record.profile_data))
    evaluation = await evaluate_candidate(
        profile, ctx["user_goal"], ctx["experience_markdown"]
    )

    record.evaluation = evaluation.model_dump_json()
    await db.commit()
    await db.refresh(record)
    logger.info("Evaluated candidate %d: priority=%s.", candidate_id, evaluation.priority)
    return deserialise_candidate(record)
