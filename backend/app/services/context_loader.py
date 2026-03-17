"""Loads experience markdown and session goal as a combined context dict."""

import json

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import ExperienceDocument, OutreachSession
from app.schemas import UserGoal
from app.utils.logging import get_logger

logger = get_logger(__name__)


async def load_context(session_id: int, db: AsyncSession) -> dict:
    """Return experience markdown and user goal for the given session.

    Returns:
        {
            "experience_markdown": str,
            "user_goal": UserGoal,
        }

    Raises:
        ValueError: if the session or its linked document cannot be found.
    """
    result = await db.execute(
        select(OutreachSession).where(OutreachSession.id == session_id)
    )
    session = result.scalar_one_or_none()
    if session is None:
        raise ValueError(f"OutreachSession {session_id} not found.")

    doc_result = await db.execute(
        select(ExperienceDocument).where(
            ExperienceDocument.id == session.experience_document_id
        )
    )
    doc = doc_result.scalar_one_or_none()
    if doc is None:
        raise ValueError(
            f"ExperienceDocument {session.experience_document_id} not found."
        )

    user_goal = UserGoal(**json.loads(session.user_goal))
    logger.debug("Context loaded for session %d.", session_id)

    return {
        "experience_markdown": doc.markdown_content,
        "user_goal": user_goal,
    }
