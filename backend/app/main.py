"""FastAPI application entry point."""

from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import CORS_ORIGINS
from app.db import init_db
from app.routes import collect, context, draft, evaluate, history, send, sessions
from app.utils.logging import configure_logging, get_logger

configure_logging()
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:  # noqa: ARG001
    """Initialise the database and upload directory on startup."""
    logger.info("Starting EzLink backend…")
    await init_db()
    yield
    logger.info("EzLink backend shutting down.")


app = FastAPI(
    title="EzLink — Networking Outreach Agent",
    description=(
        "Backend API for an AI-powered networking outreach agent. "
        "Pipeline: collect → evaluate → draft → approve → send."
    ),
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Routers ---
app.include_router(context.router)
app.include_router(sessions.router)
app.include_router(collect.router)
app.include_router(evaluate.router)
app.include_router(draft.router)
app.include_router(send.router)
app.include_router(history.router)


@app.get("/health", tags=["meta"], summary="Health check")
async def health() -> dict:
    """Return service liveness status."""
    return {"status": "ok"}
