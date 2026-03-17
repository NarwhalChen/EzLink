"""Browser-based profile collector.

TODO: Replace stub implementation with real browser-use automation.
      See https://github.com/browser-use/browser-use for the async API.
"""

import re
from urllib.parse import urlparse

from app.schemas import CandidateProfile, UserGoal
from app.utils.logging import get_logger

logger = get_logger(__name__)


def _slug_to_name(slug: str) -> str:
    """Convert a URL path slug like 'john-doe' into 'John Doe'."""
    return " ".join(part.capitalize() for part in re.split(r"[-_]+", slug) if part)


def _extract_platform(url: str) -> str:
    host = urlparse(url).netloc.lower().split(":")[0]  # strip port if present
    # Use exact domain matching to avoid false positives on substrings like "notx.com".
    domain_parts = host.split(".")
    apex = ".".join(domain_parts[-2:]) if len(domain_parts) >= 2 else host
    if apex == "linkedin.com":
        return "LinkedIn"
    if apex in ("twitter.com", "x.com"):
        return "Twitter/X"
    if apex == "github.com":
        return "GitHub"
    return "Unknown"


async def collect_profile(
    profile_url: str,
    user_goal: UserGoal,
    experience_markdown: str,  # noqa: ARG001 — reserved for future LLM context
) -> CandidateProfile:
    """Collect and return a candidate profile from the given URL.

    Current implementation is a **stub** that derives placeholder data from the
    URL so the rest of the pipeline can be exercised end-to-end.

    TODO: Replace this function body with browser-use automation:
        1. Instantiate a `browser_use.Browser` (async context manager).
        2. Navigate to `profile_url`.
        3. Extract structured data with a browser-use Agent or direct DOM queries.
        4. Map extracted data to CandidateProfile fields.
        5. Populate `mutual_signals` by comparing extracted skills/experience
           against `user_goal` and `experience_markdown`.
        6. Set `extraction_confidence` based on fields successfully populated.
    """
    logger.info("Collecting profile (stub): %s", profile_url)

    platform = _extract_platform(profile_url)
    path_parts = [p for p in urlparse(profile_url).path.strip("/").split("/") if p]
    slug = path_parts[-1] if path_parts else "unknown"
    name = _slug_to_name(slug)

    # Derive a plausible target role from the user goal to make stubs useful.
    target_role = user_goal.target_roles[0] if user_goal.target_roles else "Professional"
    target_company = (
        user_goal.target_companies[0] if user_goal.target_companies else "Acme Corp"
    )

    return CandidateProfile(
        name=name,
        platform=platform,
        title=f"{target_role}",  # stub — real extraction would differ
        company=target_company,
        location="San Francisco, CA",
        about=(
            f"Stub profile for {name}. "
            "TODO: Replace with real data extracted via browser-use."
        ),
        recent_activity="No recent activity extracted (stub).",
        education=["TODO: Extract from profile"],
        experience=[f"TODO: Extract from {platform} profile"],
        skills=["TODO: Extract skills via browser-use"],
        mutual_signals=[],
        profile_url=profile_url,
        extraction_confidence=10,  # low confidence — stub data only
    )
