#!/bin/sh
# One-click Atlas start (macOS/Linux). Env: MODEL_API_KEY (live AI), ATLAS_PORT (default 8765).
set -eu
cd "$(dirname "$0")"
[ -x .venv/bin/python ] || ./install.sh
PORT="${ATLAS_PORT:-8765}"
( (command -v xdg-open >/dev/null && xdg-open "http://127.0.0.1:$PORT") || (command -v open >/dev/null && open "http://127.0.0.1:$PORT") || true ) >/dev/null 2>&1
.venv/bin/python -m atlas.app --port "$PORT"
