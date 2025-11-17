#!/usr/bin/env bash
set -euo pipefail

# Ensure we're in the correct directory (this script resides next to app.py)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Install dependencies if not already installed
if command -v pip >/dev/null 2>&1; then
  pip install --no-cache-dir -r requirements.txt
elif command -v pip3 >/dev/null 2>&1; then
  pip3 install --no-cache-dir -r requirements.txt
else
  echo "pip not found. Please ensure Python 3 and pip are installed."
  exit 1
fi

# Default to 8501 if PORT is not set by the platform
PORT="${PORT:-8501}"

# Run the Streamlit application, binding to 0.0.0.0 for container environments
exec streamlit run app.py --server.port="${PORT}" --server.address=0.0.0.0
