"""Routes: approve and send outreach messages."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_db
from app.models import CandidateRecord as CandidateRecordModel
from app.routes._helpers import deserialise_candidate
from app.schemas import CandidateRecord
from app.services.sender import send_message
from app.utils.logging import get_logger

logger = get_logger(__name__)
router = APIRouter(prefix="/send", tags=["send"])


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
    "/approve/{candidate_id}",
    response_model=CandidateRecord,
    summary="Approve the draft message for a candidate",
)
async def approve_draft(
    candidate_id: int,
    db: AsyncSession = Depends(get_db),
) -> CandidateRecord:
    """Mark a candidate's draft as approved so it can be sent."""
    record = await _fetch_record(candidate_id, db)

    if record.draft is None:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="No draft to approve. Run POST /draft/{candidate_id} first.",
        )
    if record.sent:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Message has already been sent.",
        )

    record.approved = True
    await db.commit()
    await db.refresh(record)
    logger.info("Candidate %d draft approved.", candidate_id)
    return deserialise_candidate(record)


@router.post(
    "/send/{candidate_id}",
    response_model=CandidateRecord,
    summary="Send the approved message for a candidate",
)
async def send(
    candidate_id: int,
    db: AsyncSession = Depends(get_db),
) -> CandidateRecord:
    """Send the outreach message (requires prior approval)."""
    record = await _fetch_record(candidate_id, db)

    if not record.approved:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Draft must be approved before sending. Call /send/approve first.",
        )
    if record.sent:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Message has already been sent.",
        )

    success = await send_message(candidate_id, db)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to send message.",
        )

    await db.refresh(record)
    logger.info("Message sent for candidate %d.", candidate_id)
    return deserialise_candidate(record)
