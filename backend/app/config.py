"""Application configuration loaded from environment variables."""

import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./ezlink.db")

EXPERIENCE_UPLOAD_DIR: str = os.getenv("EXPERIENCE_UPLOAD_DIR", "./uploads")

# LLM API key — required for browser-use Agent.
LLM_API_KEY: str | None = os.getenv("LLM_API_KEY")
LLM_MODEL: str = os.getenv("LLM_MODEL", "gpt-4o")

# Chrome executable path — used to reuse logged-in browser sessions.
CHROME_PATH: str = os.getenv(
    "CHROME_PATH",
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
)

TELEGRAM_BOT_TOKEN: str = os.getenv("TELEGRAM_BOT_TOKEN", "")
