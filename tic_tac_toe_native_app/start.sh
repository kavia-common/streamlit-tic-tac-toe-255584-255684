#!/usr/bin/env bash
set -euo pipefail
PORT_ENV=${PORT:-8501}
exec python -m streamlit run app.py --server.port "$PORT_ENV" --server.address 0.0.0.0
