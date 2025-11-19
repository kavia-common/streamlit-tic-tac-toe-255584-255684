#!/usr/bin/env bash
set -euo pipefail
# Optional testing scaffold (pytest) using import-safe module
WORKSPACE="${WORKSPACE:-/home/kavia/workspace/code-generation/streamlit-tic-tac-toe-255584-255684/tic_tac_toe_native_app}"
cd "$WORKSPACE"
USE_PYTEST="${USE_PYTEST:-0}"
if [ "$USE_PYTEST" != "1" ]; then
  exit 0
fi
# Ensure user's local bin is available for --user installs in future sessions
mkdir -p "$HOME/.local/bin"
cat >/etc/profile.d/python_user_bin.sh <<'SH' || true
# make user-local python binaries available in interactive shells
export PATH="$HOME/.local/bin:$PATH"
export PYTHONUSERBASE="${PYTHONUSERBASE:-$HOME/.local}"
SH
# Export into current session so pip --user is visible immediately
export PATH="$HOME/.local/bin:$PATH"
export PYTHONUSERBASE="${PYTHONUSERBASE:-$HOME/.local}"
# Install pytest into user site (non-root)
python3 -m pip install --user --quiet pytest
# Create import-safe minimal tests
mkdir -p tests
cat > tests/test_app.py <<'PY'
# import-safe tests: do not execute side-effects at import time
import importlib
import types

# import streamlit to verify it's available
import streamlit as st

def test_streamlit_api():
    assert hasattr(st, 'title')

# import app_core safely: use importlib and ensure module exists
def test_render_callable():
    mod = importlib.import_module('app_core')
    # prefer attribute named render_app, fallback to render
    func = getattr(mod, 'render_app', None) or getattr(mod, 'render', None)
    assert callable(func)
PY
# Run pytest using python -m pytest so same interpreter sees --user packages
python3 -m pytest -q tests || { echo "pytest failed" >&2; exit 7; }
