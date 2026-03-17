from fastapi import APIRouter, HTTPException

from app.db import db_cursor
from app.dependencies import get_session_context
from app.models import from_json, to_json, utc_now_iso
from app.schemas import CandidateProfile, DraftRequest, DraftResult, EvaluationResult
from app.services.message_drafter import draft_message

router = APIRouter(prefix='/pipeline', tags=['pipeline'])


@router.post('/draft', response_model=DraftResult)
def draft(payload: DraftRequest):
    user_goal, experience_markdown = get_session_context(payload.session_id)

    with db_cursor() as cur:
        cur.execute('SELECT profile_json FROM candidates WHERE id = ?', (payload.candidate_id,))
        candidate = cur.fetchone()
        if not candidate:
            raise HTTPException(status_code=404, detail='Candidate not found')

        cur.execute(
            'SELECT evaluation_json FROM evaluations WHERE candidate_id = ? ORDER BY id DESC LIMIT 1',
            (payload.candidate_id,),
        )
        evaluation = cur.fetchone()
        if not evaluation:
            raise HTTPException(status_code=400, detail='Candidate must be evaluated first')

    profile = CandidateProfile(**from_json(candidate['profile_json']))
    evaluation_result = EvaluationResult(**from_json(evaluation['evaluation_json']))
    try:
        draft_result = draft_message(profile, evaluation_result, user_goal, experience_markdown)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    now = utc_now_iso()
    with db_cursor() as cur:
        cur.execute(
            '''
            INSERT INTO drafts (candidate_id, draft_json, approved, sent, created_at, updated_at)
            VALUES (?, ?, 0, 0, ?, ?)
            ''',
            (payload.candidate_id, to_json(draft_result.model_dump()), now, now),
        )
    return draft_result
