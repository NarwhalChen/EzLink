"""Rule-based candidate evaluator.

TODO: Replace rule-based scoring with an LLM evaluator that reasons over
      the full candidate profile and experience markdown.
"""

from app.schemas import CandidateProfile, EvaluationResult, UserGoal
from app.utils.logging import get_logger

logger = get_logger(__name__)

_PRIORITY_THRESHOLDS = {"high": 3, "medium": 1}  # minimum match_score for each tier


def _normalise(text: str) -> str:
    return text.lower().strip()


async def evaluate_candidate(
    candidate: CandidateProfile,
    user_goal: UserGoal,
    experience_markdown: str,  # noqa: ARG001 — reserved for LLM replacement
) -> EvaluationResult:
    """Score a candidate against the user goal using simple rule-based heuristics.

    Scoring rules:
    - +2  if candidate title contains any target role keyword
    - +2  if candidate company matches any target company
    - +1  per overlapping skill (up to +3)
    - confidence = min(match_score * 10, 100)
    - priority: high ≥ 3 pts, medium ≥ 1 pt, otherwise low
    - should_contact: True when priority is high or medium

    TODO: Replace with LLM evaluator for richer contextual reasoning.
    """
    match_score = 0
    common_points: list[str] = []
    risk_flags: list[str] = []

    # --- Role match ---
    candidate_title_lower = _normalise(candidate.title)
    for role in user_goal.target_roles:
        if _normalise(role) in candidate_title_lower:
            match_score += 2
            common_points.append(f"Role match: '{role}'")
            break  # count once

    # --- Company match ---
    candidate_company_lower = _normalise(candidate.company)
    for company in user_goal.target_companies:
        if _normalise(company) in candidate_company_lower:
            match_score += 2
            common_points.append(f"Company match: '{company}'")
            break

    # --- Skill overlap (capped at +3) ---
    goal_skills: set[str] = {
        _normalise(s)
        for s in user_goal.user_background.get("skills", [])
    }
    candidate_skills: set[str] = {_normalise(s) for s in candidate.skills}
    overlap = goal_skills & candidate_skills
    skill_bonus = min(len(overlap), 3)
    match_score += skill_bonus
    for skill in list(overlap)[:3]:
        common_points.append(f"Shared skill: '{skill}'")

    # --- Risk flags ---
    for avoid in user_goal.avoid_contact_types:
        if _normalise(avoid) in candidate_title_lower:
            risk_flags.append(f"Contact type to avoid: '{avoid}'")

    # --- Priority & decision ---
    if match_score >= _PRIORITY_THRESHOLDS["high"]:
        priority = "high"
    elif match_score >= _PRIORITY_THRESHOLDS["medium"]:
        priority = "medium"
    else:
        priority = "low"

    should_contact = priority in ("high", "medium")
    confidence = min(match_score * 10, 100)

    if should_contact:
        reason = (
            f"Candidate matches on {len(common_points)} point(s) "
            f"with a score of {match_score}."
        )
    else:
        reason = (
            f"Insufficient overlap with target criteria (score={match_score}). "
            "Consider broadening target roles or companies."
        )

    logger.debug(
        "Evaluated candidate %s: priority=%s score=%d", candidate.name, priority, match_score
    )

    return EvaluationResult(
        should_contact=should_contact,
        priority=priority,
        confidence=confidence,
        reason_to_contact=reason,
        common_points=common_points,
        risk_flags=risk_flags,
    )
