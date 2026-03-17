from app.schemas import CandidateProfile, DraftResult, EvaluationResult, UserGoal


def draft_message(
    candidate_profile: CandidateProfile,
    evaluation_result: EvaluationResult,
    user_goal: UserGoal,
    experience_markdown: str,
) -> DraftResult:
    if not evaluation_result.should_contact:
        raise ValueError('Drafting is only allowed when should_contact is true.')

    personalization = [
        f'{candidate_profile.title} at {candidate_profile.company}',
        f'Goal: {user_goal.primary_goal}',
    ]

    draft = (
        f"Hi {candidate_profile.name}, I noticed your work as {candidate_profile.title} at "
        f"{candidate_profile.company}. I'm currently focused on {user_goal.primary_goal} "
        "and would value a quick exchange to learn from your perspective. "
        "If you're open, I can share a concise note on why this is relevant to your work."
    )

    if experience_markdown:
        personalization.append('Experience markdown context included')

    return DraftResult(
        message_draft=draft,
        tone='professional',
        personalization_used=personalization,
        confidence=max(50, evaluation_result.confidence - 5),
    )
