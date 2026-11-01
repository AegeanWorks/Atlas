#!/bin/sh
# One-click Atlas install (macOS/Linux): creates .venv, installs dependencies.
set -eu
cd "$(dirname "$0")"
[ -d .venv ] || python3 -m venv .venv
.venv/bin/pip install --upgrade pip >/dev/null
.venv/bin/pip install -r requirements.txt
echo "Atlas installed. Start it with: ./start.sh"
