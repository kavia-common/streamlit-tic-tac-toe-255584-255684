#!/usr/bin/env bash
set -euo pipefail
# Idempotent scaffolding for Streamlit project
WS="/home/kavia/workspace/code-generation/streamlit-tic-tac-toe-255584-255684/tic_tac_toe_native_app"
mkdir -p "$WS" && cd "$WS"
# import-safe app.py
if [ ! -f "$WS/app.py" ]; then
  cat > "$WS/app.py" <<'PY'
try:
    import streamlit as st
except Exception:
    # keep import-time failures visible during test/install but avoid crashing tools
    st = None

def app():
    if not st:
        raise RuntimeError('streamlit not available')
    st.title('Tic Tac Toe (dev container stub)')
    st.write('This is a minimal scaffold for local development.')

if __name__ == '__main__':
    app()
PY
fi
mkdir -p "$WS/static"
# requirements placeholder
if [ ! -f "$WS/requirements.txt" ]; then
  cat > "$WS/requirements.txt" <<'REQ'
streamlit
pytest
REQ
fi
# robust start script (only create if missing)
if [ ! -f "$WS/start_streamlit.sh" ]; then
  cat > "$WS/start_streamlit.sh" <<'SH'
#!/usr/bin/env bash
set -euo pipefail
WS="$(cd "$(dirname "$0")" && pwd)"
# source workspace-local env then global if present
[ -f "$WS/.env_streamlit" ] && source "$WS/.env_streamlit" || true
[ -f /etc/profile.d/streamlit_env.sh ] && source /etc/profile.d/streamlit_env.sh || true
LOG="$WS/streamlit.log"
PIDFILE="$WS/streamlit.pid"
VENV="$WS/.venv"
# handle stale pidfile
if [ -f "$PIDFILE" ]; then
  PID=$(cat "$PIDFILE" 2>/dev/null || true)
  if [ -n "$PID" ] && ps -p "$PID" >/dev/null 2>&1; then
    echo "streamlit already running (PID $PID)" >&2
    exit 1
  else
    rm -f "$PIDFILE"
  fi
fi
# choose streamlit executable: prefer venv
if [ -x "$VENV/bin/streamlit" ]; then
  STREAMLIT_EXEC="$VENV/bin/streamlit"
else
  STREAMLIT_EXEC="$(command -v streamlit || true)"
fi
if [ -z "$STREAMLIT_EXEC" ]; then
  echo "streamlit not found in PATH or venv" >&2
  exit 2
fi
# start under new session so killing the group works; redirect logs
setsid "$STREAMLIT_EXEC" run "$WS/app.py" --server.port=8501 --server.address=0.0.0.0 >"$LOG" 2>&1 &
CHILD=$!
# write pid atomically
TMPPID="${PIDFILE}.tmp.$$"
echo "$CHILD" > "$TMPPID" && mv "$TMPPID" "$PIDFILE"
# ensure pidfile removed on exit
trap 'rm -f "$PIDFILE" >/dev/null 2>&1 || true' EXIT
wait $CHILD
SH
  chmod +x "$WS/start_streamlit.sh"
fi
