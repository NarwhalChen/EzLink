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

# 3. Uploads directory
echo "--> Creating uploads directory"
mkdir -p "$REPO_ROOT/backend/uploads"

# 4. Remind about .env
if [[ ! -f "$REPO_ROOT/backend/.env" ]]; then
  echo "--> Creating backend/.env template"
  cat > "$REPO_ROOT/backend/.env" <<'EOF'
TELEGRAM_BOT_TOKEN=your-token-here
LLM_API_KEY=your-openai-api-key
# LLM_MODEL=gpt-4o
# CHROME_PATH=/Applications/Google Chrome.app/Contents/MacOS/Google Chrome
EOF
fi

echo ""
echo "✅  Setup complete!"
echo "   1. Set TELEGRAM_BOT_TOKEN and LLM_API_KEY in backend/.env"
echo "   2. Run './scripts/dev.sh' to start the bot."
