from fastapi import APIRouter, HTTPException

from app.db import db_cursor
from app.models import from_json, utc_now_iso
from app.schemas import ApproveRequest, DraftResult, SendRequest
from app.services.sender import send_message

router = APIRouter(prefix='/pipeline', tags=['pipeline'])


@router.post('/approve')
def approve_draft(payload: ApproveRequest):
    with db_cursor() as cur:
        cur.execute('SELECT id FROM drafts WHERE id = ?', (payload.draft_id,))
        if not cur.fetchone():
            raise HTTPException(status_code=404, detail='Draft not found')
        cur.execute(
            'UPDATE drafts SET approved = 1, updated_at = ? WHERE id = ?',
            (utc_now_iso(), payload.draft_id),
        )
    return {'status': 'approved'}


@router.post('/send')
async def send_draft(payload: SendRequest):
    with db_cursor() as cur:
        cur.execute('SELECT draft_json, approved, sent FROM drafts WHERE id = ?', (payload.draft_id,))
        row = cur.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail='Draft not found')
        if row['approved'] != 1:
            raise HTTPException(status_code=400, detail='Draft must be approved before sending')
        if row['sent'] == 1:
            return {'status': 'already_sent'}

    result = await send_message(DraftResult(**from_json(row['draft_json'])))
    with db_cursor() as cur:
        cur.execute(
            'UPDATE drafts SET sent = 1, updated_at = ? WHERE id = ?',
            (utc_now_iso(), payload.draft_id),
        )
    return result


@router.post('/approve-and-send')
async def approve_and_send(payload: SendRequest):
    await approve_draft(ApproveRequest(draft_id=payload.draft_id))
    return await send_draft(payload)
