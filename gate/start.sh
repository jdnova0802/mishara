#!/usr/bin/env bash
# Gate API — local dev server
set -euo pipefail
cd "$(dirname "$0")"

if [ -f .venv/bin/activate ]; then
  # shellcheck disable=SC1091
  source .venv/bin/activate
elif [ ! -f .env ]; then
  echo "Run ./setup.sh first"
  exit 1
fi

if [ ! -f .env ]; then
  echo "Run ./setup.sh first"
  exit 1
fi

set -a
# shellcheck disable=SC1091
source .env
set +a

export PORT="${PORT:-5001}"
export GATE_PUBLIC_URL="${GATE_PUBLIC_URL:-http://localhost:5001}"

echo "→ Gate API on http://localhost:${PORT}"
echo "  Home:      http://localhost:${PORT}/"
echo "  Install:   http://localhost:${PORT}/install"
echo "  Docs:      http://localhost:${PORT}/docs"
echo "  Dashboard: http://localhost:${PORT}/signup"
echo ""
echo "Ctrl+C to stop"

exec python3 app.py
