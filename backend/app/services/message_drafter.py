"""Template-based message drafter.

TODO: Replace template logic with an LLM drafter that uses the full context
      (experience markdown, evaluation reasoning, user goal) to craft highly
      personalised outreach messages.
"""

from app.schemas import CandidateProfile, DraftResult, EvaluationResult, UserGoal
from app.utils.logging import get_logger

logger = get_logger(__name__)

_DEFAULT_TONE = "professional-friendly"


def _build_message(
    candidate: CandidateProfile,
    evaluation: EvaluationResult,
    user_goal: UserGoal,
) -> tuple[str, list[str]]:
    """Return (message_draft, personalization_used) from a simple template."""
    personalization_used: list[str] = []

    # Greeting
    first_name = candidate.name.split()[0] if candidate.name else "there"
    intro = f"Hi {first_name},"
    personalization_used.append("first_name")

    # Common-point hook
    if evaluation.common_points:
        hook_point = evaluation.common_points[0]
        hook = f"I came across your profile and noticed {hook_point.lower()}."
        personalization_used.append("common_point")
    else:
        hook = f"I came across your profile and was impressed by your work as {candidate.title} at {candidate.company}."
        personalization_used.append("title_and_company")

    # Purpose
    goal_snippet = user_goal.primary_goal
    purpose = (
        f"I'm currently {goal_snippet} and would love to connect with "
        f"professionals in your space."
    )
    personalization_used.append("primary_goal")

    # CTA
    cta = (
        "Would you be open to a brief 15-minute chat or exchanging a few messages? "
        "I'd really value your perspective."
    )

    message = "\n\n".join([intro, hook, purpose, cta])
    return message, personalization_used


async def draft_message(
    candidate: CandidateProfile,
    evaluation: EvaluationResult,
    user_goal: UserGoal,
    experience_markdown: str,  # noqa: ARG001 — reserved for LLM replacement
) -> DraftResult:
    """Draft a concise, personalised outreach message.

    Only produces a draft when ``evaluation.should_contact`` is True; otherwise
    returns an empty placeholder so callers can detect no-op cases.

    TODO: Replace template with an LLM call:
        - Pass experience_markdown as sender context.
        - Pass evaluation.common_points as personalisation seeds.
        - Ask the LLM to match user_goal.outreach_style tone/length preferences.
    """
    if not evaluation.should_contact:
        logger.debug("Skipping draft for %s — should_contact=False.", candidate.name)
        return DraftResult(
            message_draft="",
            tone="n/a",
            personalization_used=[],
            confidence=0,
        )

    message, personalization_used = _build_message(candidate, evaluation, user_goal)

    # Confidence scales with evaluation confidence but is capped lower because
    # template drafts are less reliable than LLM-generated ones.
    confidence = max(10, evaluation.confidence // 2)

    logger.debug("Drafted message for %s.", candidate.name)

    return DraftResult(
        message_draft=message,
        tone=_DEFAULT_TONE,
        personalization_used=personalization_used,
        confidence=confidence,
    )
