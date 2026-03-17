"""Message sender service.

TODO: Integrate with an actual messaging platform (e.g. LinkedIn API, email SMTP,
      or browser-use automation) to deliver approved messages.
"""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import CandidateRecord
from app.utils.logging import get_logger

logger = get_logger(__name__)


async def send_message(candidate_record_id: int, db: AsyncSession) -> bool:
    """Mark an approved candidate record as sent.

    For MVP: simulates sending by flipping the ``sent`` flag in the database.

    Returns:
        True  — message marked as sent successfully.
        False — candidate not found, not approved, or already sent.

    TODO: Before flipping ``sent``, call the real platform API / browser-use
          to deliver the message stored in ``candidate_record.draft``.
    """
    result = await db.execute(
        select(CandidateRecord).where(CandidateRecord.id == candidate_record_id)
    )
    record = result.scalar_one_or_none()

    if record is None:
        logger.warning("send_message: CandidateRecord %d not found.", candidate_record_id)
        return False

    if not record.approved:
        logger.warning(
            "send_message: CandidateRecord %d is not approved.", candidate_record_id
        )
        return False

    if record.sent:
        logger.info("send_message: CandidateRecord %d already sent.", candidate_record_id)
        return True

    # TODO: Deliver the message via the real platform here.
    record.sent = True
    await db.commit()
    logger.info("CandidateRecord %d marked as sent (stub).", candidate_record_id)
    return True
