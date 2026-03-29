"""Routes for uploading and retrieving experience documents."""

import os

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import EXPERIENCE_UPLOAD_DIR
from app.dependencies import get_db
from app.models import ExperienceDocument as ExperienceDocumentModel
from app.schemas import ExperienceDocument
from app.utils.logging import get_logger

logger = get_logger(__name__)
router = APIRouter(prefix="/context", tags=["context"])


@router.post(
    "/upload",
    response_model=ExperienceDocument,
    status_code=status.HTTP_201_CREATED,
    summary="Upload a Markdown experience / resume document",
)
async def upload_experience(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
) -> ExperienceDocument:
    """Accept a `.md` file, persist it to disk and store its content in the DB."""
    if not file.filename or not file.filename.endswith(".md"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only Markdown (.md) files are accepted.",
        )

    raw = await file.read()
    try:
        markdown_content = raw.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File must be UTF-8 encoded.",
        ) from exc

    # Persist file to upload directory.
    dest = os.path.join(EXPERIENCE_UPLOAD_DIR, file.filename)
    with open(dest, "w", encoding="utf-8") as fh:
        fh.write(markdown_content)

    doc = ExperienceDocumentModel(
        filename=file.filename,
        markdown_content=markdown_content,
    )
    db.add(doc)
    await db.commit()
    await db.refresh(doc)
    logger.info("Uploaded experience document: %s (id=%d)", doc.filename, doc.id)
    return ExperienceDocument.model_validate(doc)


@router.get(
    "/current",
    response_model=ExperienceDocument,
    summary="Get the most recently uploaded experience document",
)
async def get_current_experience(
    db: AsyncSession = Depends(get_db),
) -> ExperienceDocument:
    """Return the experience document with the highest ID (most recent upload)."""
    result = await db.execute(
        select(ExperienceDocumentModel).order_by(ExperienceDocumentModel.id.desc()).limit(1)
    )
    doc = result.scalar_one_or_none()
    if doc is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No experience document uploaded yet.",
        )
    return ExperienceDocument.model_validate(doc)
