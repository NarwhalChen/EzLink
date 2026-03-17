"""Route: discover candidate profiles on a platform via browser-use."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_db
from app.models import CandidateRecord as CandidateRecordModel, OutreachSession
from app.routes._helpers import deserialise_candidate
from app.schemas import CandidateRecord, CollectRequest
from app.services.browser_collector import discover_profiles
from app.services.context_loader import load_context
from app.utils.logging import get_logger

logger = get_logger(__name__)
router = APIRouter(prefix="/collect", tags=["collect"])


@router.post(
    "",
    response_model=list[CandidateRecord],
    status_code=status.HTTP_201_CREATED,
    summary="Discover candidate profiles on a platform",
)
async def collect(
    body: CollectRequest,
    db: AsyncSession = Depends(get_db),
) -> list[CandidateRecord]:
    """Use browser-use to autonomously find profiles on the given platform."""
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

    profiles = await discover_profiles(
        platform=body.platform,
        user_goal=ctx["user_goal"],
        experience_markdown=ctx["experience_markdown"],
        max_candidates=body.max_candidates,
    )

    if not profiles:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No profiles discovered. Try adjusting your goal or platform.",
        )

    records: list[CandidateRecord] = []
    for profile in profiles:
        record = CandidateRecordModel(
            session_id=body.session_id,
            profile_url=profile.profile_url or f"discovered-on-{body.platform}",
            profile_data=profile.model_dump_json(),
        )
        db.add(record)
        await db.flush()
        await db.refresh(record)
        records.append(deserialise_candidate(record))

    await db.commit()
    logger.info(
        "Discovered %d profiles on %s (session=%d).",
        len(records), body.platform, body.session_id,
    )
    return records
