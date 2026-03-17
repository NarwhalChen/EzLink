# EzLink - Networking Outreach Agent MVP

Local-first monorepo MVP with FastAPI backend + React frontend.

## Structure

- `backend/` FastAPI, SQLite persistence, rule-based evaluator/drafter/sender stubs
- `frontend/` React + Vite + TypeScript swipe-style review UX
- `scripts/setup.sh` install dependencies
- `scripts/dev.sh` run backend + frontend together

## Requirements

- Python 3.11+
- Node 18+

## Quickstart

```bash
./scripts/setup.sh
./scripts/dev.sh
```

- Backend: `http://localhost:8000`
- Frontend: `http://localhost:5173`

## Backend Notes

- SQLite DB auto-created at `backend/data/ezlink.db`
- Context is injected from the start of each pipeline call via session lookup:
  - `experience_markdown` from uploaded markdown
  - `user_goal` from session payload
- Browser collection currently uses a clear TODO placeholder in `browser_collector.py` to integrate `browser-use` while preserving:
  - one profile at a time
  - page stability waiting
  - no fabricated data
  - partial extraction allowed

## API Endpoints

- `POST /context/upload`
- `GET /context/current`
- `POST /sessions`
- `POST /pipeline/collect`
- `POST /pipeline/evaluate`
- `POST /pipeline/draft`
- `POST /pipeline/approve`
- `POST /pipeline/send`
- `POST /pipeline/approve-and-send`
- `GET /history/sessions/{session_id}/candidates`
- `GET /history/candidates/{candidate_id}`

## Frontend Flow

1. Setup page: upload markdown + define goal + start session.
2. Review page: collect/evaluate/draft per candidate card with explicit approval/send actions.
3. History page: status tracking for approval/send.

## Safety Constraints in MVP

- No auto-send.
- Sending requires explicit approval endpoint first.
- Drafting blocked if `should_contact=false`.
