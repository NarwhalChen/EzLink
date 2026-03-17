from datetime import datetime

from fastapi import APIRouter, HTTPException

from app.db import db_cursor
from app.models import to_json, utc_now_iso
from app.schemas import OutreachSession, StartSessionRequest

router = APIRouter(prefix='/sessions', tags=['sessions'])


@router.post('', response_model=OutreachSession)
def create_session(payload: StartSessionRequest):
    created_at = utc_now_iso()
    with db_cursor() as cur:
        cur.execute(
            'SELECT id FROM experience_documents WHERE id = ?',
            (payload.experience_document_id,),
        )
        if not cur.fetchone():
            raise HTTPException(status_code=404, detail='Experience document not found')

        cur.execute(
            'INSERT INTO outreach_sessions (user_goal_json, experience_document_id, created_at) VALUES (?, ?, ?)',
            (to_json(payload.user_goal.model_dump()), payload.experience_document_id, created_at),
        )
        session_id = cur.lastrowid

    return OutreachSession(
        id=session_id,
        user_goal=payload.user_goal,
        experience_document_id=payload.experience_document_id,
        created_at=datetime.fromisoformat(created_at),
    )
