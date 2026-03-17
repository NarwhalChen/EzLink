"""Telegram bot conversation handlers for EzLink.

Conversation flow:
  /start → upload resume → set goal (multi-step) → pick platform → auto-discover → review
"""

import json
import tempfile
from pathlib import Path

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    CallbackQueryHandler,
    CommandHandler,
    ConversationHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

from app.db import AsyncSessionLocal
from app.models import (
    CandidateRecord as CandidateRecordModel,
    ExperienceDocument as ExperienceDocumentModel,
    OutreachSession as OutreachSessionModel,
)
from app.routes._helpers import deserialise_candidate
from app.schemas import UserGoal
from app.services.browser_collector import discover_profiles
from app.services.context_loader import load_context
from app.services.lead_evaluator import evaluate_candidate
from app.services.message_drafter import draft_message
from app.services.sender import send_message

from sqlalchemy import select

# Conversation states
(
    WAITING_RESUME,
    WAITING_GOAL,
    WAITING_ROLES,
    WAITING_COMPANIES,
    WAITING_STYLE,
    READY,
) = range(6)

SUPPORTED_PLATFORMS = ["linkedin", "github", "twitter"]


def _candidate_card(rec) -> str:
    """Build a plain-text summary card for a candidate record."""
    lines = []
    p = rec.profile_data
    e = rec.evaluation
    d = rec.draft

    # Header
    if p:
        lines.append(f"👤 {p.name} — {p.title} @ {p.company}")
        if p.location:
            lines.append(f"📍 {p.location}")
        if p.profile_url:
            lines.append(f"🔗 {p.profile_url}")
    else:
        lines.append(f"🔗 {rec.profile_url}")

    # Evaluation
    if e:
        contact = "✅ Yes" if e.should_contact else "❌ No"
        lines.append(f"\n📊 Contact: {contact} | Priority: {e.priority.upper()} | Confidence: {e.confidence}%")
        if e.reason_to_contact:
            lines.append(f"💡 {e.reason_to_contact}")
        if e.common_points:
            lines.append(f"🤝 {', '.join(e.common_points)}")

    # Draft
    if d and d.message_draft:
        lines.append(f"\n📝 Draft ({d.tone}):\n───────────\n{d.message_draft}\n───────────")

    # Status
    status_parts = []
    if rec.approved:
        status_parts.append("✅ Approved")
    if rec.sent:
        status_parts.append("📤 Sent")
    if status_parts:
        lines.append(" | ".join(status_parts))

    return "\n".join(lines)


def _review_keyboard(candidate_id: int, approved: bool, sent: bool) -> InlineKeyboardMarkup:
    """Build inline keyboard for candidate review actions."""
    buttons = []
    if not approved:
        buttons.append(InlineKeyboardButton("✅ Approve", callback_data=f"approve:{candidate_id}"))
    if approved and not sent:
        buttons.append(InlineKeyboardButton("📤 Send", callback_data=f"send:{candidate_id}"))
    buttons.append(InlineKeyboardButton("⏭ Skip", callback_data=f"skip:{candidate_id}"))
    return InlineKeyboardMarkup([buttons])


def _platform_keyboard() -> InlineKeyboardMarkup:
    """Build inline keyboard for platform selection."""
    buttons = [
        [InlineKeyboardButton("LinkedIn", callback_data="platform:linkedin")],
        [InlineKeyboardButton("GitHub", callback_data="platform:github")],
        [InlineKeyboardButton("Twitter/X", callback_data="platform:twitter")],
    ]
    return InlineKeyboardMarkup(buttons)


# ─── /start ────────────────────────────────────────────────────────────

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Greet the user and ask for a resume."""
    context.user_data.clear()
    await update.message.reply_text(
        "👋 Welcome to EzLink!\n\n"
        "I'll help you find and reach out to people automatically.\n"
        "Let's start — please send me your resume/experience file (.md or .txt)."
    )
    return WAITING_RESUME


# ─── Resume upload ─────────────────────────────────────────────────────

async def receive_resume(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle uploaded document — save to DB."""
    doc = update.message.document
    if not doc:
        await update.message.reply_text("Please send a file (.md or .txt).")
        return WAITING_RESUME

    filename = doc.file_name or "resume.md"
    if not filename.endswith((".md", ".txt")):
        await update.message.reply_text("Only .md or .txt files are supported. Try again.")
        return WAITING_RESUME

    tg_file = await doc.get_file()
    with tempfile.NamedTemporaryFile(suffix=Path(filename).suffix, delete=False) as tmp:
        await tg_file.download_to_drive(tmp.name)
        content = Path(tmp.name).read_text(encoding="utf-8")

    async with AsyncSessionLocal() as db:
        record = ExperienceDocumentModel(filename=filename, markdown_content=content)
        db.add(record)
        await db.commit()
        await db.refresh(record)
        context.user_data["experience_doc_id"] = record.id

    preview = content[:200] + ("…" if len(content) > 200 else "")
    await update.message.reply_text(
        f"✅ Resume saved ({len(content)} chars).\n\n"
        f"Preview:\n{preview}\n\n"
        "Now tell me: what's your primary outreach goal?\n"
        "(e.g. \"looking for SWE roles at FAANG companies\")"
    )
    return WAITING_GOAL


async def receive_resume_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Prompt again if user sends text instead of file."""
    await update.message.reply_text(
        "I need a file, not text. Please send your resume as a .md or .txt file.\n"
        "You can also type /skip to use an empty resume."
    )
    return WAITING_RESUME


async def skip_resume(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Allow skipping resume upload."""
    async with AsyncSessionLocal() as db:
        record = ExperienceDocumentModel(filename="empty.md", markdown_content="(No resume provided)")
        db.add(record)
        await db.commit()
        await db.refresh(record)
        context.user_data["experience_doc_id"] = record.id

    await update.message.reply_text(
        "⏭ Skipped resume.\n\nWhat's your primary outreach goal?"
    )
    return WAITING_GOAL


# ─── Goal collection (multi-step) ──────────────────────────────────────

async def receive_goal(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data["primary_goal"] = update.message.text.strip()
    await update.message.reply_text(
        "🎯 Got it.\n\n"
        "What target roles are you interested in?\n"
        "(comma-separated, e.g. \"Software Engineer, Data Scientist\")\n\n"
        "Type /skip to skip."
    )
    return WAITING_ROLES


async def receive_roles(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    text = update.message.text.strip()
    context.user_data["target_roles"] = [r.strip() for r in text.split(",") if r.strip()]
    await update.message.reply_text(
        "🏢 What target companies?\n"
        "(comma-separated, e.g. \"Google, Meta, Apple\")\n\n"
        "Type /skip to skip."
    )
    return WAITING_COMPANIES


async def skip_roles(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data["target_roles"] = []
    await update.message.reply_text("🏢 What target companies?\n(comma-separated)\n\nType /skip to skip.")
    return WAITING_COMPANIES


async def receive_companies(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    text = update.message.text.strip()
    context.user_data["target_companies"] = [c.strip() for c in text.split(",") if c.strip()]
    await update.message.reply_text("✍️ Outreach style: casual or formal?\n\nType /skip to default to casual.")
    return WAITING_STYLE


async def skip_companies(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data["target_companies"] = []
    await update.message.reply_text("✍️ Outreach style: casual or formal?\n\nType /skip to default to casual.")
    return WAITING_STYLE


async def receive_style(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    text = update.message.text.strip().lower()
    style = "formal" if "formal" in text else "casual"
    return await _create_session(update, context, style)


async def skip_style(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    return await _create_session(update, context, "casual")


async def _create_session(update: Update, context: ContextTypes.DEFAULT_TYPE, style: str) -> int:
    """Persist the session and transition to READY state."""
    user_goal = UserGoal(
        primary_goal=context.user_data["primary_goal"],
        target_roles=context.user_data.get("target_roles", []),
        target_companies=context.user_data.get("target_companies", []),
        outreach_style={"tone": style},
    )

    async with AsyncSessionLocal() as db:
        session = OutreachSessionModel(
            user_goal=user_goal.model_dump_json(),
            experience_document_id=context.user_data["experience_doc_id"],
        )
        db.add(session)
        await db.commit()
        await db.refresh(session)
        context.user_data["session_id"] = session.id

    await update.message.reply_text(
        f"✅ Session created! (style: {style})\n\n"
        "Now pick a platform and I'll automatically find relevant people for you.",
        reply_markup=_platform_keyboard(),
    )
    return READY


# ─── Platform selection & discovery (READY state) ──────────────────────

async def platform_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle platform selection from inline keyboard."""
    query = update.callback_query
    await query.answer()

    if not query.data.startswith("platform:"):
        return

    platform = query.data.split(":", 1)[1]
    session_id = context.user_data.get("session_id")
    if not session_id:
        await query.edit_message_text("No active session. Use /start to begin.")
        return

    await query.edit_message_text(f"🔍 Searching {platform.capitalize()} for relevant profiles...\nThis may take a few minutes.")

    try:
        async with AsyncSessionLocal() as db:
            ctx = await load_context(session_id, db)
            user_goal = ctx["user_goal"]
            experience_md = ctx["experience_markdown"]

            profiles = await discover_profiles(
                platform=platform,
                user_goal=user_goal,
                experience_markdown=experience_md,
                max_candidates=5,
            )

            if not profiles:
                await query.edit_message_text(
                    "No profiles found. Try a different platform or adjust your goal.\n\n"
                    "Pick another platform:",
                    reply_markup=_platform_keyboard(),
                )
                return

            await query.edit_message_text(f"✅ Found {len(profiles)} profiles! Evaluating and drafting...")

            # Process each profile: save → evaluate → draft → send card
            for profile in profiles:
                record = CandidateRecordModel(
                    session_id=session_id,
                    profile_url=profile.profile_url or f"discovered-on-{platform}",
                    profile_data=profile.model_dump_json(),
                )
                db.add(record)
                await db.flush()
                await db.refresh(record)

                # Evaluate
                evaluation = await evaluate_candidate(profile, user_goal, experience_md)
                record.evaluation = evaluation.model_dump_json()

                # Draft
                draft = await draft_message(profile, evaluation, user_goal, experience_md)
                if draft.message_draft:
                    record.draft = draft.model_dump_json()

                await db.flush()
                await db.refresh(record)

                # Send card to user
                candidate = deserialise_candidate(record)
                card = _candidate_card(candidate)
                await context.bot.send_message(
                    chat_id=query.message.chat_id,
                    text=card,
                    reply_markup=_review_keyboard(candidate.id, candidate.approved, candidate.sent),
                )

            await db.commit()

        # Offer to search another platform
        await context.bot.send_message(
            chat_id=query.message.chat_id,
            text=f"Done! Processed {len(profiles)} candidates.\n\nSearch another platform or /history to review all.",
            reply_markup=_platform_keyboard(),
        )

    except RuntimeError as exc:
        await query.edit_message_text(f"Error: {exc}")
    except Exception as exc:
        await query.edit_message_text(f"Unexpected error during discovery: {exc}")


async def handle_text_in_ready(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """In READY state, guide user to pick a platform."""
    await update.message.reply_text(
        "Pick a platform to search for people:",
        reply_markup=_platform_keyboard(),
    )
    return READY


# ─── Inline keyboard callbacks (approve / send / skip) ──────────────────

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle approve / send / skip button presses."""
    query = update.callback_query
    await query.answer()

    # Ignore platform callbacks here — handled by platform_callback.
    if query.data.startswith("platform:"):
        return

    action, candidate_id_str = query.data.split(":", 1)
    candidate_id = int(candidate_id_str)

    async with AsyncSessionLocal() as db:
        result = await db.execute(
            select(CandidateRecordModel).where(CandidateRecordModel.id == candidate_id)
        )
        record = result.scalar_one_or_none()
        if not record:
            await query.edit_message_text("Candidate not found.")
            return

        if action == "approve":
            record.approved = True
            await db.commit()
            await db.refresh(record)
            candidate = deserialise_candidate(record)
            card = _candidate_card(candidate)
            await query.edit_message_text(
                f"✅ Approved!\n\n{card}",
                reply_markup=_review_keyboard(candidate.id, candidate.approved, candidate.sent),
            )

        elif action == "send":
            success = await send_message(candidate_id, db)
            if success:
                await db.refresh(record)
                candidate = deserialise_candidate(record)
                card = _candidate_card(candidate)
                await query.edit_message_text(f"📤 Sent!\n\n{card}")
            else:
                await query.edit_message_text("Failed to send. Make sure the candidate is approved first.")

        elif action == "skip":
            await query.edit_message_text("⏭ Skipped.")


# ─── /history command ───────────────────────────────────────────────────

async def history(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show recent candidates."""
    session_id = context.user_data.get("session_id")

    async with AsyncSessionLocal() as db:
        query = select(CandidateRecordModel).order_by(CandidateRecordModel.created_at.desc())
        if session_id:
            query = query.where(CandidateRecordModel.session_id == session_id)
        query = query.limit(20)

        result = await db.execute(query)
        records = result.scalars().all()

    if not records:
        await update.message.reply_text("No candidates yet. Pick a platform to start searching.")
        return

    lines = [f"📋 Recent candidates ({len(records)}):\n"]
    for rec in records:
        candidate = deserialise_candidate(rec)
        p = candidate.profile_data
        e = candidate.evaluation

        name = p.name if p else "Unknown"
        title = f"{p.title} @ {p.company}" if p else ""
        priority = e.priority.upper() if e else "—"
        status = ""
        if candidate.sent:
            status = "📤"
        elif candidate.approved:
            status = "✅"
        elif candidate.draft and candidate.draft.message_draft:
            status = "📝"
        elif candidate.evaluation:
            status = "📊"

        lines.append(f"  {status} {name} — {title} [{priority}]")

    lines.append("\nPick a platform to search more, or /start to begin a new session.")
    await update.message.reply_text("\n".join(lines))


# ─── /cancel ────────────────────────────────────────────────────────────

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Cancel the current conversation."""
    context.user_data.clear()
    await update.message.reply_text("Cancelled. Use /start to begin again.")
    return ConversationHandler.END


# ─── Build the conversation handler ─────────────────────────────────────

def build_conversation_handler() -> ConversationHandler:
    return ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            WAITING_RESUME: [
                CommandHandler("skip", skip_resume),
                MessageHandler(filters.Document.ALL, receive_resume),
                MessageHandler(filters.TEXT & ~filters.COMMAND, receive_resume_text),
            ],
            WAITING_GOAL: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, receive_goal),
            ],
            WAITING_ROLES: [
                CommandHandler("skip", skip_roles),
                MessageHandler(filters.TEXT & ~filters.COMMAND, receive_roles),
            ],
            WAITING_COMPANIES: [
                CommandHandler("skip", skip_companies),
                MessageHandler(filters.TEXT & ~filters.COMMAND, receive_companies),
            ],
            WAITING_STYLE: [
                CommandHandler("skip", skip_style),
                MessageHandler(filters.TEXT & ~filters.COMMAND, receive_style),
            ],
            READY: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text_in_ready),
            ],
        },
        fallbacks=[
            CommandHandler("cancel", cancel),
            CommandHandler("start", start),
        ],
    )
