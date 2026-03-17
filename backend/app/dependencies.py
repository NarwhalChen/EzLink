from fastapi import HTTPException

from app.db import db_cursor
from app.models import from_json
from app.schemas import UserGoal


def get_session_context(session_id: int) -> tuple[UserGoal, str]:
    with db_cursor() as cur:
        cur.execute(
            '''
            SELECT s.user_goal_json, d.markdown_content
            FROM outreach_sessions s
            JOIN experience_documents d ON s.experience_document_id = d.id
            WHERE s.id = ?
            ''',
            (session_id,),
        )
        row = cur.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail='Session not found')
    return UserGoal(**from_json(row['user_goal_json'])), row['markdown_content']
