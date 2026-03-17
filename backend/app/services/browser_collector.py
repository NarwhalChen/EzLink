from app.schemas import CandidateProfile, UserGoal


async def collect_profile(
    profile_url: str,
    user_goal: UserGoal,
    experience_markdown: str,
) -> CandidateProfile:
    """Collect visible profile data with browser-use.

    TODO: integrate browser-use agent flow with real selectors/session persistence.
    Rules: one profile at a time, wait for stability, allow partial fields, no fabrication.
    """
    _ = user_goal
    _ = experience_markdown
    return CandidateProfile(
        name='Unknown (TODO collector)',
        platform='LinkedIn',
        title='Unknown',
        company='Unknown',
        location=None,
        about='Collector placeholder: configure browser-use extraction.',
        recent_activity=None,
        education=[],
        experience=[],
        skills=[],
        mutual_signals=[],
        profile_url=profile_url,
        extraction_confidence=20,
    )
