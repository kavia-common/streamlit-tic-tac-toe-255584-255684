#!/usr/bin/env bash
set -euo pipefail
WS="/home/kavia/workspace/code-generation/streamlit-tic-tac-toe-255584-255684/tic_tac_toe_native_app"
cd "$WS"
LOG="$WS/streamlit.log"
PIDFILE="$WS/streamlit.pid"
# source envs if present
[ -f "$WS/.env_streamlit" ] && source "$WS/.env_streamlit" || true
[ -f /etc/profile.d/streamlit_env.sh ] && source /etc/profile.d/streamlit_env.sh || true
# stale pidfile cleanup
if [ -f "$PIDFILE" ]; then
  PID=$(cat "$PIDFILE" 2>/dev/null || true)
  if [ -z "$PID" ] || ! ps -p "$PID" >/dev/null 2>&1; then
    rm -f "$PIDFILE"
  else
    echo "port 8501 appears in use by PID $PID; aborting validation" >&2
    exit 5
  fi
fi
# check port in use (ss fallback grep)
if command -v ss >/dev/null 2>&1 && ss -ltn | grep -q ':8501' >/dev/null 2>&1; then
  echo "port 8501 appears in use; aborting validation" >&2
  exit 5
fi
# start helper that runs start_streamlit.sh (it writes pidfile and log)
# start in background so this script can monitor pidfile
./start_streamlit.sh &
START_HELPER_PID=$!
# wait for pidfile
ATTEMPTS=30
OK=0
for i in $(seq 1 $ATTEMPTS); do
  if [ -f "$PIDFILE" ] && [ -s "$PIDFILE" ]; then
    PID=$(cat "$PIDFILE" | tr -d ' ')
    if ps -p "$PID" >/dev/null 2>&1; then OK=1 && break; fi
  fi
  sleep 1
done
if [ "$OK" -ne 1 ]; then
  echo "Streamlit pidfile not created or process not running. Tail of log:" >&2
  tail -n 200 "$LOG" >&2 || true
  kill "$START_HELPER_PID" >/dev/null 2>&1 || true
  exit 3
fi
# obtain PGID and wait for HTTP readiness
PGID=$(ps -o pgid= "$PID" | tr -d ' ' || true)
ATTEMPTS=60
OK=0
for i in $(seq 1 $ATTEMPTS); do
  if curl -sSf --max-time 3 http://127.0.0.1:8501/ >/dev/null 2>&1 || curl -sSf --max-time 3 http://[::1]:8501/ >/dev/null 2>&1 || curl -sSf --max-time 3 http://localhost:8501/ >/dev/null 2>&1; then
    OK=1 && break
  fi
  sleep 1
done
if [ "$OK" -ne 1 ]; then
  echo "Streamlit did not respond within timeout. Tail of log:" >&2
  tail -n 200 "$LOG" >&2 || true
  # attempt group kill
  if [ -n "$PGID" ]; then kill -TERM -"$PGID" >/dev/null 2>&1 || true; fi
  kill "$PID" >/dev/null 2>&1 || true
  exit 4
fi
# evidence: small HTTP snippet and tail of log
curl -s http://127.0.0.1:8501/ | head -c 200 || true
echo
echo "--- streamlit.log tail ---"
tail -n 50 "$LOG" || true
echo "PID=$PID PGID=$PGID"
# stop server: kill process group if available, else PID
if [ -n "$PGID" ]; then
  kill -TERM -"$PGID" >/dev/null 2>&1 || true
else
  kill "$PID" >/dev/null 2>&1 || true
fi
sleep 1
# ensure helper process stopped
kill "$START_HELPER_PID" >/dev/null 2>&1 || true
rm -f "$PIDFILE"
echo "validation: success"
