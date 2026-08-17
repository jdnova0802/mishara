#!/usr/bin/env bash
# Gate API — first-time setup (run once on your laptop)
set -euo pipefail
cd "$(dirname "$0")"

echo "→ Gate API setup"

if ! command -v python3 >/dev/null 2>&1; then
  echo "Install Python 3.11+ first."
  exit 1
fi

USE_VENV=1
if [ -d .venv ] && [ ! -f .venv/bin/activate ]; then
  echo "→ Removing broken .venv"
  rm -rf .venv
fi

if [ ! -d .venv ]; then
  echo "→ Creating virtualenv"
  if python3 -m venv .venv 2>/dev/null && [ -f .venv/bin/activate ]; then
    USE_VENV=1
  else
    rm -rf .venv
    echo "→ venv unavailable — using system python"
    USE_VENV=0
  fi
fi

if [ "$USE_VENV" = 1 ]; then
  # shellcheck disable=SC1091
  source .venv/bin/activate
fi

echo "→ Installing dependencies"
python3 -m pip install -q --upgrade pip
python3 -m pip install -q -r requirements.txt

if [ ! -f .env ]; then
  echo "→ Creating .env in dev mode"
  cp .env.example .env
  python3 -c "from pathlib import Path; import secrets; p=Path('.env'); t=p.read_text(); t=t.replace('GATE_DEV_MODE=0','GATE_DEV_MODE=1'); t=t.replace('GATE_SECRET_KEY=change-me', 'GATE_SECRET_KEY='+secrets.token_hex(32)); p.write_text(t)"
fi

echo ""
echo "✓ Ready. Run:"
echo "    ./start.sh"
echo ""
echo "Then open: http://localhost:5001"
echo "Install page: http://localhost:5001/install"
echo "Signup: http://localhost:5001/signup"
