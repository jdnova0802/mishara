#!/usr/bin/env bash
# Gate API — production start (Render/Railway). Refuses localhost unless GATE_DEV_MODE=1.
set -euo pipefail
cd "$(dirname "$0")"
PORT="${PORT:-5001}"
python3 -c "from public_url import assert_prod_public; print('public', assert_prod_public())"
exec gunicorn app:app --bind "0.0.0.0:${PORT}" --workers 2 --timeout 60
