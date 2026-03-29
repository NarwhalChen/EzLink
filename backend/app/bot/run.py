"""Standalone entry point for the Telegram bot."""

import sys

from telegram.ext import ApplicationBuilder, CallbackQueryHandler, CommandHandler

from app.config import TELEGRAM_BOT_TOKEN
from app.db import init_db
from app.bot.handlers import (
    build_conversation_handler,
    button_callback,
    history,
    platform_callback,
)
from app.utils.logging import configure_logging, get_logger

configure_logging()
logger = get_logger(__name__)


async def post_init(application) -> None:
    """Initialise DB when the bot starts."""
    await init_db()
    logger.info("Database initialised.")


def main() -> None:
    if not TELEGRAM_BOT_TOKEN:
        print("ERROR: Set TELEGRAM_BOT_TOKEN in your .env file.")
        sys.exit(1)

    app = (
        ApplicationBuilder()
        .token(TELEGRAM_BOT_TOKEN)
        .post_init(post_init)
        .build()
    )

    # Conversation handler covers /start and the full setup flow
    app.add_handler(build_conversation_handler())

    # /history works in any state
    app.add_handler(CommandHandler("history", history))

    # Platform selection callbacks (must come before generic button_callback)
    app.add_handler(CallbackQueryHandler(platform_callback, pattern=r"^platform:"))

    # Inline keyboard callbacks (approve / send / skip)
    app.add_handler(CallbackQueryHandler(button_callback, pattern=r"^(approve|send|skip):"))

    logger.info("Starting EzLink Telegram bot…")
    app.run_polling()


if __name__ == "__main__":
    main()
