#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
STREAMLIT_ARGS="${STREAMLIT_ARGS:-}"
exec python3 -m streamlit run app.py --server.headless true --server.port 8501 --server.address 0.0.0.0 $STREAMLIT_ARGS
