#!/usr/bin/env bash
set -euo pipefail
# Start script for Streamlit app (execs start.sh in foreground for process managers)
WORKSPACE="${WORKSPACE:-/home/kavia/workspace/code-generation/streamlit-tic-tac-toe-255584-255684/tic_tac_toe_native_app}"
cd "$WORKSPACE"
# Ensure user-local bin is available this session (persisting should be done in env/setup step)
export PATH="$HOME/.local/bin:$PATH"
# Ensure start.sh is executable and present
if [ ! -x "./start.sh" ]; then
  if [ -f "./start.sh" ]; then
    chmod +x ./start.sh
  else
    echo "Error: start.sh not found in workspace ($WORKSPACE)" >&2
    exit 2
  fi
fi
# Exec the project start script so this PID becomes the Streamlit process (foreground)
exec ./start.sh
