#!/usr/bin/env bash
set -euo pipefail
WS="/home/kavia/workspace/code-generation/streamlit-tic-tac-toe-255584-255684/tic_tac_toe_native_app"
cd "$WS"
# Source workspace-local and global env files if present so STREAMLIT headless vars are visible
[ -f "$WS/.env_streamlit" ] && source "$WS/.env_streamlit" || true
[ -f /etc/profile.d/streamlit_env.sh ] && source /etc/profile.d/streamlit_env.sh || true
# Ensure tests directory and simple import test
mkdir -p tests
TEST_FILE="$WS/tests/test_import_app.py"
if [ ! -f "$TEST_FILE" ]; then
  cat > "$TEST_FILE" <<'PY'
# simple import test — app.py is import-safe (does not execute UI code on import)
import importlib

def test_import_app():
    importlib.import_module('app')
PY
fi
# Run pytest from workspace venv if available, otherwise fallback to system pytest
if [ -x "$WS/.venv/bin/pytest" ]; then
  "$WS/.venv/bin/pytest" -q tests --disable-warnings
else
  pytest -q tests --disable-warnings
fi
