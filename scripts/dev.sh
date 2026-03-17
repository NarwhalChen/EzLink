#!/usr/bin/env bash
set -euo pipefail

source .venv/bin/activate
(
  cd backend
  uvicorn app.main:app --reload --port 8000
) &
BACK_PID=$!

(
  cd frontend
  npm run dev
) &
FRONT_PID=$!

trap 'kill $BACK_PID $FRONT_PID' EXIT
wait
