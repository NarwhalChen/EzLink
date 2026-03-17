from app.schemas import CandidateProfile, EvaluationResult, UserGoal


def evaluate_candidate(
    candidate_profile: CandidateProfile,
    user_goal: UserGoal,
    experience_markdown: str,
) -> EvaluationResult:
    target_title_hit = any(
        role.lower() in candidate_profile.title.lower() for role in user_goal.target_roles
    )
    target_company_hit = any(
        company.lower() in candidate_profile.company.lower()
        for company in user_goal.target_companies
    )

    common_points = []
    if candidate_profile.company != 'Unknown':
        common_points.append(f'Works at {candidate_profile.company}')
    if candidate_profile.title != 'Unknown':
        common_points.append(f'Role alignment: {candidate_profile.title}')
    if experience_markdown:
        common_points.append('Experience context loaded')

    score = 30
    if target_title_hit:
        score += 30
    if target_company_hit:
        score += 25
    score += min(candidate_profile.extraction_confidence // 5, 15)

    risk_flags = []
    if candidate_profile.extraction_confidence < 40:
        risk_flags.append('Low extraction confidence; review manually.')
    if not target_title_hit and not target_company_hit:
        risk_flags.append('Weak role/company match.')

    should_contact = score >= 60
    priority = 'high' if score >= 80 else 'medium' if score >= 60 else 'low'

    return EvaluationResult(
        should_contact=should_contact,
        priority=priority,
        confidence=min(score, 99),
        reason_to_contact=(
            'Matches stated outreach targets based on role/company overlap.'
            if should_contact
            else 'Insufficient alignment with current goal targets.'
        ),
        common_points=common_points[:4],
        risk_flags=risk_flags,
    )
