from datetime import datetime, UTC

from fastapi import APIRouter, File, HTTPException, UploadFile

from app.db import db_cursor
from app.models import utc_now_iso
from app.schemas import ExperienceDocument

router = APIRouter(prefix='/context', tags=['context'])


@router.post('/upload', response_model=ExperienceDocument)
async def upload_experience(file: UploadFile = File(...)):
    if not file.filename.endswith('.md'):
        raise HTTPException(status_code=400, detail='Only markdown files are supported.')

    content = (await file.read()).decode('utf-8')
    uploaded_at = utc_now_iso()
    with db_cursor() as cur:
        cur.execute(
            'INSERT INTO experience_documents (filename, markdown_content, uploaded_at) VALUES (?, ?, ?)',
            (file.filename, content, uploaded_at),
        )
        doc_id = cur.lastrowid

    return ExperienceDocument(
        id=doc_id,
        filename=file.filename,
        markdown_content=content,
        uploaded_at=datetime.fromisoformat(uploaded_at),
    )


@router.get('/current', response_model=ExperienceDocument)
def get_current_experience():
    with db_cursor() as cur:
        cur.execute('SELECT * FROM experience_documents ORDER BY id DESC LIMIT 1')
        row = cur.fetchone()
    if not row:
        raise HTTPException(status_code=404, detail='No experience document uploaded.')
    return ExperienceDocument(
        id=row['id'],
        filename=row['filename'],
        markdown_content=row['markdown_content'],
        uploaded_at=datetime.fromisoformat(row['uploaded_at']),
    )
