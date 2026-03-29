# EzLink — Networking Outreach Agent

EzLink is an AI-powered networking outreach tool that automates the "discover → evaluate → draft → approve → send" pipeline. Upload your resume, pick a platform (LinkedIn, GitHub, Twitter), and the agent autonomously finds relevant people, evaluates each candidate, drafts personalised messages, and lets you approve before sending — all through a Telegram bot.

---

## Tech Stack

| Layer     | Technology                                                |
|-----------|-----------------------------------------------------------|
| Backend   | Python 3.11+, FastAPI, SQLAlchemy (async), SQLite, Uvicorn |
| Interface | Telegram Bot (python-telegram-bot)                        |
| Agent     | browser-use (autonomous browser automation) + LLM (OpenAI) |

---

## Prerequisites

- **Python 3.11+** — `python3 --version`
- **Google Chrome** — for browser-use to reuse your logged-in sessions
- **Telegram Bot Token** — from [@BotFather](https://t.me/BotFather)
- **OpenAI API Key** — for the browser-use Agent's LLM

---

## Quick Start

```bash
# 1. Clone the repo
git clone https://github.com/your-org/EzLink.git
cd EzLink

# 2. One-time setup (creates .venv, installs deps, generates .env template)
./scripts/setup.sh

# 3. Edit backend/.env with your tokens
#    TELEGRAM_BOT_TOKEN=...
#    LLM_API_KEY=...

# 4. Start the bot + API
./scripts/dev.sh
```

| Service      | Details                      |
|--------------|------------------------------|
| Telegram Bot | Polling mode                 |
| Backend API  | http://localhost:8000        |
| API docs     | http://localhost:8000/docs   |

---

## Manual Setup (Alternative)

```bash
# Backend
python3 -m venv backend/.venv
source backend/.venv/bin/activate
pip install -r backend/requirements.txt
mkdir -p backend/uploads

# Copy and edit .env
cp backend/.env.example backend/.env  # or create manually
```

Start services individually:

```bash
# Terminal 1 — backend API
cd backend && uvicorn app.main:app --reload --port 8000

# Terminal 2 — Telegram bot
cd backend && python -m app.bot.run
```

---

## Telegram Bot Flow

```
/start
  → Upload resume (.md or .txt)
  → Set outreach goal
  → Define target roles (comma-separated)
  → Define target companies (comma-separated)
  → Choose style (casual / formal)
  → Pick platform: [LinkedIn] [GitHub] [Twitter/X]
      → browser-use Agent autonomously searches & extracts profiles
      → Each candidate is evaluated and a draft is generated
      → Cards sent with [Approve] [Send] [Skip] buttons

/history — view all candidates in current session
/start   — start a new session
/cancel  — cancel current flow
```

---

## API Endpoints

| Method | Path                            | Description                                       |
|--------|---------------------------------|---------------------------------------------------|
| POST   | `/context/upload`               | Upload a Markdown resume / experience document    |
| GET    | `/context/current`              | Retrieve the currently active experience document |
| POST   | `/sessions`                     | Create a new outreach session                     |
| GET    | `/sessions/{session_id}`        | Get details for a specific session                |
| POST   | `/collect`                      | Discover profiles on a platform (browser-use)     |
| POST   | `/evaluate/{candidate_id}`      | Evaluate a collected candidate profile            |
| POST   | `/draft/{candidate_id}`         | Draft an outreach message for a candidate         |
| PUT    | `/draft/{candidate_id}`         | Update the drafted message                        |
| POST   | `/send/approve/{candidate_id}`  | Mark a drafted message as approved                |
| POST   | `/send/send/{candidate_id}`     | Send the approved message                         |
| GET    | `/history`                      | List all outreach history records                 |
| GET    | `/history/{candidate_id}`       | Get history for a specific candidate              |
| GET    | `/health`                       | Service health check                              |

---

## Architecture Overview

```
backend/
├── app/
│   ├── main.py             # FastAPI app, lifespan
│   ├── config.py           # Environment / settings
│   ├── db.py               # Async SQLite engine & session factory
│   ├── models.py           # SQLAlchemy ORM models
│   ├── schemas.py          # Pydantic request/response schemas
│   ├── dependencies.py     # FastAPI dependency injectors
│   ├── bot/                # Telegram bot
│   │   ├── handlers.py     # Conversation & callback handlers
│   │   └── run.py          # Bot entry point
│   ├── routes/             # One file per resource group
│   │   ├── context.py      # Resume upload & retrieval
│   │   ├── sessions.py     # Outreach session management
│   │   ├── collect.py      # Platform-based profile discovery
│   │   ├── evaluate.py     # Candidate evaluation
│   │   ├── draft.py        # Message drafting & editing
│   │   ├── send.py         # Approval & sending
│   │   └── history.py      # Outreach history queries
│   ├── services/           # Business logic / external integrations
│   │   ├── browser_collector.py   # browser-use autonomous discovery
│   │   ├── lead_evaluator.py      # Rule-based evaluation (MVP)
│   │   ├── message_drafter.py     # Template-based drafting (MVP)
│   │   ├── sender.py              # Messaging platform stub
│   │   └── context_loader.py      # Loads resume + goal for a session
│   └── utils/
│       └── logging.py      # Structured logging helpers
└── uploads/                # Uploaded resume files (gitignored)
```

---

## Environment Variables

Create a `backend/.env` file (auto-generated by `setup.sh`):

| Variable               | Default                          | Description                              |
|------------------------|----------------------------------|------------------------------------------|
| `TELEGRAM_BOT_TOKEN`   | *(required)*                     | Telegram bot token from @BotFather       |
| `LLM_API_KEY`          | *(required)*                     | OpenAI API key for browser-use Agent     |
| `LLM_MODEL`            | `gpt-4o`                         | LLM model name for browser-use           |
| `CHROME_PATH`          | `/Applications/.../Google Chrome` | Chrome executable for browser-use        |
| `DATABASE_URL`         | `sqlite+aiosqlite:///./ezlink.db` | Async SQLAlchemy database URL           |
| `EXPERIENCE_UPLOAD_DIR`| `./uploads`                       | Directory where resume files are stored |

---

## TODO

- [ ] **LLM evaluation** — replace rule-based `lead_evaluator.py` with LLM-powered contextual reasoning
- [ ] **LLM drafting** — replace template-based `message_drafter.py` with LLM-generated personalised messages
- [ ] **Real messaging** — implement `sender.py` to deliver approved messages via LinkedIn API, email, or browser-use
- [ ] Add user authentication
- [ ] Containerise with Docker Compose
- [ ] Add end-to-end tests
