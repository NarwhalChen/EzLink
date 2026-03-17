from datetime import datetime

from fastapi import APIRouter

from app.db import db_cursor
from app.models import to_json, utc_now_iso
from app.services.browser_collector import collect_profile
from app.services.context_loader import load_core_context
from app.schemas import CandidateRecord, CollectRequest, CandidateProfile

router = APIRouter(prefix='/pipeline', tags=['pipeline'])


@router.post('/collect', response_model=CandidateRecord)
async def collect_candidate(payload: CollectRequest):
    context = load_core_context(payload.session_id)
    profile = await collect_profile(
        profile_url=payload.profile_url,
        user_goal=context['user_goal'],
        experience_markdown=context['experience_markdown'],
    )
    created_at = utc_now_iso()
    with db_cursor() as cur:
        cur.execute(
            'INSERT INTO candidates (session_id, profile_json, created_at) VALUES (?, ?, ?)',
            (payload.session_id, to_json(profile.model_dump()), created_at),
        )
        candidate_id = cur.lastrowid

    return CandidateRecord(
        id=candidate_id,
        session_id=payload.session_id,
        created_at=datetime.fromisoformat(created_at),
        profile=CandidateProfile(**profile.model_dump()),
    )
