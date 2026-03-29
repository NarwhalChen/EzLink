"""Async SQLAlchemy engine, session factory, declarative base, and DB initialisation."""

import os
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from app.config import DATABASE_URL, EXPERIENCE_UPLOAD_DIR
from app.utils.logging import get_logger

logger = get_logger(__name__)

engine = create_async_engine(DATABASE_URL, echo=False, future=True)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


class Base(DeclarativeBase):
    """Shared declarative base for all ORM models."""


async def init_db() -> None:
    """Create all tables and ensure the upload directory exists."""
    os.makedirs(EXPERIENCE_UPLOAD_DIR, exist_ok=True)
    logger.info("Upload directory ready: %s", EXPERIENCE_UPLOAD_DIR)

    async with engine.begin() as conn:
        # Import models so their metadata is registered before create_all.
        import app.models  # noqa: F401

        await conn.run_sync(Base.metadata.create_all)
    logger.info("Database tables initialised.")
