#!/usr/bin/env bash
set -euo pipefail
# install: create deterministic venv and install requirements non-interactively
WS="/home/kavia/workspace/code-generation/streamlit-tic-tac-toe-255584-255684/tic_tac_toe_native_app"
cd "$WS"
VENV="$WS/.venv"
PIP_LOG="$WS/pip-install.log"
REQ="$WS/requirements.txt"
# create venv if missing
if [ ! -d "$VENV" ]; then
  python3 -m venv "$VENV"
fi
# ensure pip in venv is usable; upgrade pip quietly (best-effort)
"$VENV/bin/python" -m pip install --upgrade pip >/dev/null 2>&1 || true
# install dependencies: prefer requirements.txt when non-empty, otherwise install streamlit and pytest
if [ -f "$REQ" ] && [ -s "$REQ" ]; then
  "$VENV/bin/pip" install --no-input --disable-pip-version-check --no-cache-dir -r "$REQ" >"$PIP_LOG" 2>&1
else
  "$VENV/bin/pip" install --no-input --disable-pip-version-check --no-cache-dir streamlit pytest >"$PIP_LOG" 2>&1
fi
# verify imports using venv python
"$VENV/bin/python" - <<'PY'
import sys
try:
    import streamlit, pytest
except Exception as e:
    print('dependency-import-failure:', e, file=sys.stderr)
    sys.exit(4)
print('ok')
PY
