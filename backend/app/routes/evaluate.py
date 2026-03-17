from datetime import datetime

from fastapi import APIRouter, HTTPException

from app.db import db_cursor
from app.dependencies import get_session_context
from app.models import from_json, to_json, utc_now_iso
from app.schemas import CandidateProfile, EvaluateRequest, EvaluationResult
from app.services.lead_evaluator import evaluate_candidate

router = APIRouter(prefix='/pipeline', tags=['pipeline'])


@router.post('/evaluate', response_model=EvaluationResult)
def evaluate(payload: EvaluateRequest):
    user_goal, experience_markdown = get_session_context(payload.session_id)
    with db_cursor() as cur:
        cur.execute('SELECT profile_json FROM candidates WHERE id = ?', (payload.candidate_id,))
        row = cur.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail='Candidate not found')

    profile = CandidateProfile(**from_json(row['profile_json']))
    result = evaluate_candidate(profile, user_goal, experience_markdown)
    with db_cursor() as cur:
        cur.execute(
            'INSERT INTO evaluations (candidate_id, evaluation_json, created_at) VALUES (?, ?, ?)',
            (payload.candidate_id, to_json(result.model_dump()), utc_now_iso()),
        )
    return result
