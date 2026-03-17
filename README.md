# EzLink — Networking Outreach Agent

EzLink is an AI-powered networking outreach tool that automates the "collect → evaluate → draft → approve → send" pipeline for professional outreach messages. Upload your resume, point it at a list of LinkedIn-style profile URLs, and let the agent evaluate each candidate, draft personalised messages, and (once real integrations land) send them on your behalf.

---

## Tech Stack

| Layer    | Technology                                      |
|----------|-------------------------------------------------|
| Backend  | Python 3.11+, FastAPI, SQLAlchemy (async), SQLite, Uvicorn |
| Frontend | React 18, Vite, TypeScript, React Router v6, Axios |
| Agent    | browser-use (browser automation, stub today)    |

---

## Prerequisites

- **Python 3.11+** — `python3 --version`
- **Node.js 18+** — `node --version`
- **npm 9+** — bundled with Node.js

---

## Quick Start

```bash
# 1. Clone the repo
git clone https://github.com/your-org/EzLink.git
cd EzLink

# 2. One-time setup (creates .venv, installs all deps)
./scripts/setup.sh

# 3. Start both dev servers
./scripts/dev.sh
```

| Service  | URL                          |
|----------|------------------------------|
| Frontend | http://localhost:5173        |
| Backend  | http://localhost:8000        |
| API docs | http://localhost:8000/docs   |

---

## Manual Setup (Alternative)

```bash
# Backend
python3 -m venv backend/.venv
source backend/.venv/bin/activate
pip install -r backend/requirements.txt
mkdir -p backend/uploads

# Frontend
cd frontend
npm install
```

Start servers individually:

```bash
# Terminal 1 — backend
cd backend && uvicorn app.main:app --reload --port 8000

# Terminal 2 — frontend
cd frontend && npm run dev
```

---

## API Endpoints

| Method | Path                            | Description                                      |
|--------|---------------------------------|--------------------------------------------------|
| POST   | `/context/upload`               | Upload a Markdown resume / experience document   |
| GET    | `/context/current`              | Retrieve the currently active experience document |
| POST   | `/sessions`                     | Create a new outreach session                    |
| GET    | `/sessions/{session_id}`        | Get details for a specific session               |
| POST   | `/collect`                      | Collect a candidate profile from a URL           |
| POST   | `/evaluate/{candidate_id}`      | Evaluate a collected candidate profile           |
| POST   | `/draft/{candidate_id}`         | Draft an outreach message for a candidate        |
| PUT    | `/draft/{candidate_id}`         | Update the drafted message                       |
| POST   | `/send/approve/{candidate_id}`  | Mark a drafted message as approved               |
| POST   | `/send/send/{candidate_id}`     | Send the approved message                        |
| GET    | `/history`                      | List all outreach history records                |
| GET    | `/history/{candidate_id}`       | Get history for a specific candidate             |
| GET    | `/health`                       | Service health check                             |

---

## Frontend Pages

| Page            | Route      | Description                                                                     |
|-----------------|------------|---------------------------------------------------------------------------------|
| **Setup**       | `/`        | Upload your resume and set your outreach goal to configure a session            |
| **Review**      | `/review`  | Step through candidates — view collected profiles, evaluate, draft, and approve |
| **History**     | `/history` | Browse all past outreach records and their current statuses                     |

---

## Architecture Overview

```
frontend/                   # Vite + React + TypeScript SPA
│
backend/
├── app/
│   ├── main.py             # FastAPI app, CORS, lifespan
│   ├── config.py           # Environment / settings
│   ├── db.py               # Async SQLite engine & session factory
│   ├── models.py           # SQLAlchemy ORM models
│   ├── schemas.py          # Pydantic request/response schemas
│   ├── dependencies.py     # FastAPI dependency injectors
│   ├── routes/             # One file per resource group
│   │   ├── context.py      # Resume upload & retrieval
│   │   ├── sessions.py     # Outreach session management
│   │   ├── collect.py      # Browser-based profile collection
│   │   ├── evaluate.py     # LLM-powered candidate evaluation
│   │   ├── draft.py        # Message drafting & editing
│   │   ├── send.py         # Approval & sending
│   │   └── history.py      # Outreach history queries
│   ├── services/           # Business logic / external integrations
│   │   ├── browser_collector.py   # browser-use stub
│   │   ├── lead_evaluator.py      # LLM evaluation stub
│   │   ├── message_drafter.py     # LLM drafting stub
│   │   ├── sender.py              # Messaging platform stub
│   │   └── context_loader.py     # Loads resume for a session
│   └── utils/
│       └── logging.py      # Structured logging helpers
└── uploads/                # Uploaded resume files (gitignored)
```

---

## Environment Variables

Create a `backend/.env` file (copied from `backend/.env.example` if present):

| Variable               | Default           | Description                                      |
|------------------------|-------------------|--------------------------------------------------|
| `DATABASE_URL`         | `sqlite+aiosqlite:///./ezlink.db` | Async SQLAlchemy database URL   |
| `EXPERIENCE_UPLOAD_DIR`| `uploads/`        | Directory where resume files are stored          |
| `CORS_ORIGINS`         | `http://localhost:5173` | Comma-separated list of allowed CORS origins |
| `OPENAI_API_KEY`       | *(unset)*         | Required when LLM integration is added           |

---

## TODO

- [ ] **browser-use integration** — replace stub in `browser_collector.py` with real browser automation to scrape LinkedIn / other profile pages
- [ ] **LLM integration** — wire `lead_evaluator.py` and `message_drafter.py` to an OpenAI / Anthropic model for genuine evaluation and personalised message drafting
- [ ] **Real messaging platform** — implement `sender.py` to deliver approved messages via LinkedIn API, email, or another channel
- [ ] Add user authentication
- [ ] Containerise with Docker Compose
- [ ] Add end-to-end tests
