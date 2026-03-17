#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

echo "==> Setting up EzLink..."

# 1. Python virtual environment
echo "--> Creating Python virtual environment at backend/.venv"
python3 -m venv "$REPO_ROOT/backend/.venv"

# 2. Backend dependencies
echo "--> Installing backend Python dependencies"
cd "$REPO_ROOT/backend"
"$REPO_ROOT/backend/.venv/bin/pip" install --upgrade pip --quiet
"$REPO_ROOT/backend/.venv/bin/pip" install -r requirements.txt --quiet

# 3. Frontend dependencies
echo "--> Installing frontend Node dependencies"
cd "$REPO_ROOT/frontend"
npm install --silent

# 4. Uploads directory
echo "--> Creating uploads directory"
mkdir -p "$REPO_ROOT/backend/uploads"

echo ""
echo "✅  Setup complete!"
echo "   Run './scripts/dev.sh' to start both services."
