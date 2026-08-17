#!/usr/bin/env bash
# Gate API — first-time setup (run once on your laptop)
set -euo pipefail
cd "$(dirname "$0")"

echo "→ Gate API setup"

if ! command -v python3 >/dev/null 2>&1; then
  echo "Install Python 3.11+ first."
  exit 1
fi

if [ ! -d .venv ]; then
  echo "→ Creating virtualenv"
  python3 -m venv .venv
fi

# shellcheck disable=SC1091
source .venv/bin/activate

echo "→ Installing dependencies"
pip install -q --upgrade pip
pip install -q -r requirements.txt

if [ ! -f .env ]; then
  echo "→ Creating .env (dev mode — no Stripe required)"
  cp .env.example .env
  python3 - <<'PY'
from pathlib import Path
p = Path(".env")
text = p.read_text()
text = text.replace("GATE_DEV_MODE=0", "GATE_DEV_MODE=1")
text = text.replace("GATE_SECRET_KEY=change-me", f"GATE_SECRET_KEY={__import__('secrets').token_hex(32)}")
if "GATE_PUBLIC_URL=http://localhost:5001" not in text:
    pass
p.write_text(text)
PY
fi

echo ""
echo "✓ Ready. Run:"
echo "    ./start.sh"
echo ""
echo "Then open: http://localhost:5001"
echo "Install page: http://localhost:5001/install"
echo "Signup: http://localhost:5001/signup"
