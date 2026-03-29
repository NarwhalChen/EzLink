#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
VENV_PYTHON="$REPO_ROOT/backend/.venv/bin/python"

# Verify the virtual environment exists
if [[ ! -f "$VENV_PYTHON" ]]; then
  echo "❌  Virtual environment not found. Run './scripts/setup.sh' first."
  exit 1
fi

echo "==> Starting EzLink..."
echo "    Telegram Bot: polling"
echo "    API docs:     http://localhost:8000/docs"
echo ""

# Start backend API in the background
cd "$REPO_ROOT/backend"
"$REPO_ROOT/backend/.venv/bin/uvicorn" app.main:app --reload --port 8000 &
BACKEND_PID=$!

# Kill backend on exit
trap 'echo ""; echo "==> Shutting down..."; kill "$BACKEND_PID" 2>/dev/null; wait "$BACKEND_PID" 2>/dev/null; exit 0' INT TERM EXIT

# Start Telegram bot in the foreground
cd "$REPO_ROOT/backend"
"$VENV_PYTHON" -m app.bot.run
