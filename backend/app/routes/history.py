from datetime import datetime

from fastapi import APIRouter, HTTPException

from app.db import db_cursor
from app.models import from_json
from app.schemas import CandidateProfile, CandidateRecord, DraftResult, EvaluationResult, PipelineCandidateDetail

router = APIRouter(prefix='/history', tags=['history'])


@router.get('/sessions/{session_id}/candidates', response_model=list[PipelineCandidateDetail])
def list_candidates(session_id: int):
    with db_cursor() as cur:
        cur.execute('SELECT * FROM candidates WHERE session_id = ? ORDER BY id ASC', (session_id,))
        candidates = cur.fetchall()

    output: list[PipelineCandidateDetail] = []
    for row in candidates:
        with db_cursor() as cur:
            cur.execute(
                'SELECT evaluation_json FROM evaluations WHERE candidate_id = ? ORDER BY id DESC LIMIT 1',
                (row['id'],),
            )
            eval_row = cur.fetchone()
            cur.execute(
                'SELECT id, draft_json, approved, sent FROM drafts WHERE candidate_id = ? ORDER BY id DESC LIMIT 1',
                (row['id'],),
            )
            draft_row = cur.fetchone()

        output.append(
            PipelineCandidateDetail(
                candidate=CandidateRecord(
                    id=row['id'],
                    session_id=row['session_id'],
                    created_at=datetime.fromisoformat(row['created_at']),
                    profile=CandidateProfile(**from_json(row['profile_json'])),
                ),
                evaluation=EvaluationResult(**from_json(eval_row['evaluation_json'])) if eval_row else None,
                draft=DraftResult(**from_json(draft_row['draft_json'])) if draft_row else None,
                draft_id=draft_row['id'] if draft_row else None,
                approved=bool(draft_row['approved']) if draft_row else False,
                sent=bool(draft_row['sent']) if draft_row else False,
            )
        )
    return output


@router.get('/candidates/{candidate_id}', response_model=PipelineCandidateDetail)
def get_candidate_detail(candidate_id: int):
    with db_cursor() as cur:
        cur.execute('SELECT * FROM candidates WHERE id = ?', (candidate_id,))
        row = cur.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail='Candidate not found')

    details = list_candidates(row['session_id'])
    for item in details:
        if item.candidate.id == candidate_id:
            return item
    raise HTTPException(status_code=404, detail='Candidate detail not found')
