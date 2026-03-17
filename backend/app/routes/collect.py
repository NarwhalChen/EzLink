"""Route: collect a candidate profile from a URL."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_db
from app.models import CandidateRecord as CandidateRecordModel, OutreachSession
from app.routes._helpers import deserialise_candidate
from app.schemas import CandidateRecord, CollectRequest
from app.services.browser_collector import collect_profile
from app.services.context_loader import load_context
from app.utils.logging import get_logger

logger = get_logger(__name__)
router = APIRouter(prefix="/collect", tags=["collect"])


@router.post(
    "",
    response_model=CandidateRecord,
    status_code=status.HTTP_201_CREATED,
    summary="Collect a candidate profile from a URL",
)
async def collect(
    body: CollectRequest,
    db: AsyncSession = Depends(get_db),
) -> CandidateRecord:
    """Collect profile data for a URL and persist a CandidateRecord."""
    # Verify session exists.
    session_result = await db.execute(
        select(OutreachSession).where(OutreachSession.id == body.session_id)
    )
    if session_result.scalar_one_or_none() is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"OutreachSession {body.session_id} not found.",
        )

    ctx = await load_context(body.session_id, db)
    profile = await collect_profile(
        body.profile_url, ctx["user_goal"], ctx["experience_markdown"]
    )

    record = CandidateRecordModel(
        session_id=body.session_id,
        profile_url=body.profile_url,
        profile_data=profile.model_dump_json(),
    )
    db.add(record)
    await db.commit()
    await db.refresh(record)
    logger.info(
        "Collected profile for %s (candidate_id=%d).", body.profile_url, record.id
    )
    return deserialise_candidate(record)
