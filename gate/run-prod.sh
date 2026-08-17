#!/usr/bin/env bash
# Gate API — production start (Render/Railway/local prod)
set -euo pipefail
cd "$(dirname "$0")"
PORT="${PORT:-5001}"
exec gunicorn app:app --bind "0.0.0.0:${PORT}" --workers 2 --timeout 60
