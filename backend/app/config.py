"""Application configuration loaded from environment variables."""

import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./ezlink.db")

EXPERIENCE_UPLOAD_DIR: str = os.getenv("EXPERIENCE_UPLOAD_DIR", "./uploads")

# Optional LLM API key — required when replacing stub services with real LLM calls.
LLM_API_KEY: str | None = os.getenv("LLM_API_KEY")

CORS_ORIGINS: list[str] = [
    origin.strip()
    for origin in os.getenv("CORS_ORIGINS", "http://localhost:5173").split(",")
    if origin.strip()
]
