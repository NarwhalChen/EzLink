"""Browser-based autonomous profile discovery using browser-use.

The agent navigates to the chosen platform, searches for people matching the
user goal, visits profiles one at a time, and extracts structured data.

Rules:
- Reuses logged-in browser session (Chrome instance).
- Visits profiles one at a time.
- Waits for page stability before extracting.
- Avoids rapid actions (typing, clicking).
- Returns partial data if a field cannot be extracted.
- Never fabricates data.
"""

import json
import re
from urllib.parse import urlparse

from browser_use import Agent, Browser, BrowserConfig
from langchain_openai import ChatOpenAI

from app.config import CHROME_PATH, LLM_API_KEY, LLM_MODEL
from app.schemas import CandidateProfile, UserGoal
from app.utils.logging import get_logger

logger = get_logger(__name__)

PLATFORM_URLS = {
    "linkedin": "https://www.linkedin.com",
    "github": "https://github.com",
    "twitter": "https://twitter.com",
    "x": "https://x.com",
}


def _build_task(platform: str, user_goal: UserGoal, experience_markdown: str, max_candidates: int) -> str:
    """Construct the natural-language task prompt for the browser-use Agent."""
    platform_url = PLATFORM_URLS.get(platform.lower(), platform)

    roles_text = ", ".join(user_goal.target_roles) if user_goal.target_roles else "any relevant role"
    companies_text = ", ".join(user_goal.target_companies) if user_goal.target_companies else "any company"

    # Truncate experience to keep the prompt manageable.
    exp_summary = experience_markdown[:500] if experience_markdown else "(no background provided)"

    return f"""Go to {platform_url}.

My goal: {user_goal.primary_goal}
Target roles: {roles_text}
Target companies: {companies_text}
My background (summary): {exp_summary}

Search for people who match these criteria. Visit up to {max_candidates} individual profiles.

For EACH profile you visit, extract the following fields from what is actually visible on the page. Do NOT make up any data — if a field is not visible, set it to null or an empty list.

Fields to extract per profile:
- name (string)
- title (string, current job title)
- company (string, current company)
- location (string or null)
- about (string or null, their bio/summary)
- recent_activity (string or null, any recent post or activity)
- education (list of strings)
- experience (list of strings, formatted as "Role at Company")
- skills (list of strings)
- profile_url (string, the URL of the profile page you are on)

Important rules:
- Visit one profile at a time.
- Wait for each page to fully load before extracting.
- Do not click or type rapidly.
- Only extract data that is visible on the page.
- If you cannot extract some fields, include what you can (partial data is OK).
- Never fabricate or hallucinate data.

Return your results as a JSON array of objects. Example:
[
  {{
    "name": "Jane Doe",
    "title": "Software Engineer",
    "company": "Google",
    "location": "San Francisco, CA",
    "about": "Building distributed systems...",
    "recent_activity": null,
    "education": ["BS Computer Science, MIT"],
    "experience": ["Software Engineer at Google", "Intern at Meta"],
    "skills": ["Python", "Go", "Kubernetes"],
    "profile_url": "https://www.linkedin.com/in/janedoe"
  }}
]

Return ONLY the JSON array, nothing else."""


def _detect_platform(profile_url: str) -> str:
    """Detect platform name from a profile URL."""
    host = urlparse(profile_url).netloc.lower()
    if "linkedin" in host:
        return "LinkedIn"
    if "github" in host:
        return "GitHub"
    if "twitter" in host or "x.com" in host:
        return "Twitter/X"
    return "Unknown"


def _parse_profiles(raw_result: str, platform: str) -> list[CandidateProfile]:
    """Parse the Agent's JSON output into CandidateProfile objects."""
    # Try to extract JSON array from the output.
    json_match = re.search(r"\[.*\]", raw_result, re.DOTALL)
    if not json_match:
        logger.warning("Could not find JSON array in agent output.")
        return []

    try:
        items = json.loads(json_match.group())
    except json.JSONDecodeError:
        logger.warning("Failed to parse JSON from agent output.")
        return []

    profiles: list[CandidateProfile] = []
    for item in items:
        if not isinstance(item, dict):
            continue
        try:
            profile = CandidateProfile(
                name=item.get("name", "Unknown"),
                platform=_detect_platform(item.get("profile_url", "")) or platform.capitalize(),
                title=item.get("title", ""),
                company=item.get("company", ""),
                location=item.get("location"),
                about=item.get("about"),
                recent_activity=item.get("recent_activity"),
                education=item.get("education", []) or [],
                experience=item.get("experience", []) or [],
                skills=item.get("skills", []) or [],
                mutual_signals=[],
                profile_url=item.get("profile_url", ""),
                extraction_confidence=_compute_confidence(item),
            )
            profiles.append(profile)
        except Exception as exc:
            logger.warning("Failed to parse one profile entry: %s", exc)
            continue

    return profiles


def _compute_confidence(item: dict) -> int:
    """Estimate extraction confidence based on how many fields were populated."""
    fields = ["name", "title", "company", "location", "about", "skills", "education", "experience"]
    populated = sum(1 for f in fields if item.get(f))
    return min(round(populated / len(fields) * 100), 100)


async def discover_profiles(
    platform: str,
    user_goal: UserGoal,
    experience_markdown: str,
    max_candidates: int = 5,
) -> list[CandidateProfile]:
    """Use browser-use Agent to autonomously find and extract candidate profiles.

    Args:
        platform: Platform name (e.g. "linkedin", "github") or a base URL.
        user_goal: The user's outreach goal and targeting criteria.
        experience_markdown: The user's experience/resume as markdown.
        max_candidates: Maximum number of profiles to visit.

    Returns:
        A list of CandidateProfile objects extracted from the platform.
        May be partial if some profiles could not be fully extracted.
    """
    if not LLM_API_KEY:
        raise RuntimeError(
            "LLM_API_KEY is required for browser-use Agent. "
            "Set it in your .env file."
        )

    task = _build_task(platform, user_goal, experience_markdown, max_candidates)
    logger.info("Starting browser-use discovery on %s (max %d candidates).", platform, max_candidates)

    browser = Browser(config=BrowserConfig(
        headless=False,
        chrome_instance_path=CHROME_PATH,
    ))

    llm = ChatOpenAI(model=LLM_MODEL, api_key=LLM_API_KEY)

    agent = Agent(
        task=task,
        llm=llm,
        browser=browser,
    )

    result = await agent.run()

    # Extract the final text result from the agent.
    raw_text = result.final_result() if hasattr(result, "final_result") else str(result)
    logger.debug("Agent raw output length: %d chars.", len(raw_text))

    profiles = _parse_profiles(raw_text, platform)
    logger.info("Discovered %d profiles on %s.", len(profiles), platform)

    return profiles
