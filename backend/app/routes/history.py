"""Routes: list and retrieve candidate history."""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_db
from app.models import CandidateRecord as CandidateRecordModel
from app.routes._helpers import deserialise_candidate
from app.schemas import CandidateRecord
from app.utils.logging import get_logger

logger = get_logger(__name__)
router = APIRouter(prefix="/history", tags=["history"])


@router.get(
    "",
    response_model=dict,
    summary="List all candidate records with pagination",
)
async def list_history(
    page: int = Query(1, ge=1, description="Page number (1-indexed)"),
    page_size: int = Query(20, ge=1, le=100, description="Records per page"),
    session_id: int | None = Query(None, description="Filter by session ID"),
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Return a paginated list of CandidateRecords, optionally filtered by session."""
    query = select(CandidateRecordModel)
    count_query = select(func.count()).select_from(CandidateRecordModel)

    if session_id is not None:
        query = query.where(CandidateRecordModel.session_id == session_id)
        count_query = count_query.where(CandidateRecordModel.session_id == session_id)

    total_result = await db.execute(count_query)
    total = total_result.scalar_one()

    offset = (page - 1) * page_size
    query = query.order_by(CandidateRecordModel.id.desc()).offset(offset).limit(page_size)
    rows = await db.execute(query)
    records = [deserialise_candidate(r) for r in rows.scalars().all()]

    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "results": [r.model_dump() for r in records],
    }


@router.get(
    "/{candidate_id}",
    response_model=CandidateRecord,
    summary="Get full details for a single candidate record",
)
async def get_candidate(
    candidate_id: int,
    db: AsyncSession = Depends(get_db),
) -> CandidateRecord:
    result = await db.execute(
        select(CandidateRecordModel).where(CandidateRecordModel.id == candidate_id)
    )
    record = result.scalar_one_or_none()
    if record is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"CandidateRecord {candidate_id} not found.",
        )
    return deserialise_candidate(record)
