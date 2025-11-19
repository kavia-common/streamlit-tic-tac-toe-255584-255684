#!/usr/bin/env bash
set -euo pipefail
# Validation: start streamlit in background, probe, then stop cleanly
WORKSPACE="${WORKSPACE:-/home/kavia/workspace/code-generation/streamlit-tic-tac-toe-255584-255684/tic_tac_toe_native_app}"
cd "$WORKSPACE"
export PATH="$HOME/.local/bin:$PATH"
READY_TIMEOUT="${READY_TIMEOUT:-60}"
LOG=streamlit.log
PIDFILE=streamlit.pid
PORT=8501
# broad port check (tcp4/tcp6, all addresses)
if ss -ltn | grep -q ":[0-9]*${PORT}\b" ; then
  echo "port ${PORT} appears in use; cannot start streamlit" >&2
  ss -ltn | grep ":${PORT}" || true
  exit 10
fi
# start streamlit in background, capture PID
nohup python3 -m streamlit run app.py --server.headless true --server.port ${PORT} --server.address 0.0.0.0 > "$LOG" 2>&1 &
PARENT_PID=$!
echo "$PARENT_PID" > "$PIDFILE"
# recursively collect descendant PIDs
collect_pids(){
  local pids="$1" all="$pids" pid children
  for pid in $pids; do
    children=$(pgrep -P "$pid" || true)
    if [ -n "$children" ]; then
      all="$all $children"
      # recurse and append
      all="$all $(collect_pids "$children")"
    fi
  done
  echo "$all"
}
# create probe output file
PROBE_OUT=$(mktemp --tmpdir="${WORKSPACE}" streamlit_probe.XXXXXX) || PROBE_OUT="${WORKSPACE}/streamlit_probe.out"
READY=0
END=$((SECONDS + READY_TIMEOUT))
while [ $SECONDS -lt $END ]; do
  sleep 1
  HTTP_STATUS=$(curl --silent --write-out "%{http_code}" --max-time 3 -o "$PROBE_OUT" "http://127.0.0.1:${PORT}/" 2>/dev/null || true)
  if [ "$HTTP_STATUS" = "200" ]; then
    if grep -q -E "Tic Tac Toe|Streamlit" "$PROBE_OUT" 2>/dev/null || true; then
      READY=1
      break
    fi
  fi
done
if [ "$READY" -ne 1 ]; then
  echo "streamlit did not respond within ${READY_TIMEOUT}s" >&2
  echo "---- last ${LOG} tail ----" >&2
  tail -n 200 "$LOG" || true
  [ -f "$PROBE_OUT" ] && { echo "---- probe snippet ----" >&2; head -n 80 "$PROBE_OUT" || true; }
  # attempt cleanup
  if [ -f "$PIDFILE" ]; then
    P=$(cat "$PIDFILE" 2>/dev/null || true)
    if [ -n "$P" ]; then
      DESC=$(collect_pids "$P")
      for dp in $DESC; do kill "$dp" 2>/dev/null || true; done
      kill "$P" 2>/dev/null || true
    fi
    rm -f "$PIDFILE" || true
  fi
  exit 8
fi
# Success evidence
echo "STREAMLIT_OK"
echo "---- HTTP probe snippet ----"
head -n 40 "$PROBE_OUT" || true
echo "---- log tail ----"
tail -n 50 "$LOG" || true
# cleanup: recursive kill (descendants first) then parent
cleanup(){
  if [ -f "$PIDFILE" ]; then
    P=$(cat "$PIDFILE" 2>/dev/null || true)
    if [ -n "$P" ]; then
      DESC=$(collect_pids "$P")
      for dp in $DESC; do kill "$dp" 2>/dev/null || true; done
      kill "$P" 2>/dev/null || true
      # wait briefly for exit
      for i in {1..8}; do
        sleep 1
        if ! kill -0 "$P" 2>/dev/null; then break; fi
      done
      if kill -0 "$P" 2>/dev/null; then
        kill -9 "$P" 2>/dev/null || true
      fi
    fi
    rm -f "$PIDFILE" || true
  fi
}
trap cleanup EXIT
# keep script running short time to allow trap on exit to run after evidence printed
sleep 1
