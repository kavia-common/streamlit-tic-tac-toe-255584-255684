#!/usr/bin/env bash
set -euo pipefail
WORKSPACE="${WORKSPACE:-/home/kavia/workspace/code-generation/streamlit-tic-tac-toe-255584-255684/tic_tac_toe_native_app}"
mkdir -p "$WORKSPACE"
cd "$WORKSPACE"
REQUIREMENTS_PIN="${REQUIREMENTS_PIN:-streamlit>=1.20.0,<2.0.0}"
cat > requirements.txt <<EOF
# Minimal runtime dependencies (change REQUIREMENTS_PIN before deps step if needed)
$REQUIREMENTS_PIN
# numpy  # uncomment if used
EOF
if [ ! -f app_core.py ]; then
  cat > app_core.py <<'PY'
import streamlit as st

def render_app():
    st.title('Tic Tac Toe (dev)')
    st.markdown('Place your application code here.')

PY
fi
if [ ! -f app.py ]; then
  cat > app.py <<'PY'
from app_core import render_app

# Streamlit will import this file; calling render_app at import time ensures UI loads
render_app()

PY
fi
mkdir -p .streamlit
cat > .streamlit/config.toml <<'CF'
[server]
headless = true
port = 8501
enableCORS = false
enableXsrfProtection = false
address = "0.0.0.0"
CF
cat > start.sh <<'SH'
#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
STREAMLIT_ARGS="${STREAMLIT_ARGS:-}"
exec python3 -m streamlit run app.py --server.headless true --server.port 8501 --server.address 0.0.0.0 $STREAMLIT_ARGS
SH
# chmod may require sudo in some containers; attempt without and fallback
if ! chmod +x start.sh 2>/dev/null; then
  sudo chmod +x start.sh
fi
