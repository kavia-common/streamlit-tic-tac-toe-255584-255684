#!/usr/bin/env bash
set -euo pipefail
# Install Python deps into user site with pip sanity checks
WORKSPACE="${WORKSPACE:-/home/kavia/workspace/code-generation/streamlit-tic-tac-toe-255584-255684/tic_tac_toe_native_app}"
cd "$WORKSPACE"
# ensure user local bin is on PATH for this session
export PATH="$HOME/.local/bin:${PATH:-}"
# ensure PYTHONUSERBASE is set to a sane default (resolved at runtime)
export PYTHONUSERBASE="${PYTHONUSERBASE:-$(python3 -m site --user-base 2>/dev/null || echo "$HOME/.local") }"
# Ensure pip is available for python3
PIP_INFO=$(python3 -m pip --version 2>/dev/null || true)
if [ -z "$PIP_INFO" ]; then
  echo "error: pip not available for python3" >&2
  exit 3
fi
# parse pip version robustly (second token usually X.Y.Z)
PIP_VER=$(printf "%s" "$PIP_INFO" | awk '{print $2}')
PIP_MAJOR=$(printf "%s" "$PIP_VER" | cut -d. -f1 || echo 0)
# If pip major version is zero or not numeric, attempt user upgrade (very old pip)
if ! printf "%s" "$PIP_MAJOR" | grep -Eq '^[0-9]+$' || [ "$PIP_MAJOR" -lt 1 ]; then
  python3 -m pip install --upgrade --user pip --quiet || true
fi
# Install requirements into user site (quiet, non-interactive)
if [ -f requirements.txt ]; then
  python3 -m pip install --upgrade --user -r requirements.txt --quiet
else
  echo "warning: requirements.txt not found in $WORKSPACE" >&2
fi
# verify usersite path
USERSITE=$(python3 - <<'PY'
import site
try:
    print(site.getusersitepackages())
except Exception:
    print('')
PY
)
if [ -z "$USERSITE" ] || [ ! -d "$USERSITE" ]; then
  echo "warning: python user-site not found: $USERSITE" >&2
fi
# verify streamlit import and print version
INSTALLED_STREAMLIT=$(python3 - <<'PY'
try:
    import importlib
    s = importlib.import_module('streamlit')
    print(getattr(s, '__version__', ''))
except Exception:
    print('')
PY
)
if [ -z "$INSTALLED_STREAMLIT" ]; then
  echo "error: streamlit not importable after install" >&2
  exit 6
fi
printf "streamlit %s\n" "$INSTALLED_STREAMLIT"
# If REQUIREMENTS_PIN provided, print it and warn on mismatch (simple textual check)
if [ -n "${REQUIREMENTS_PIN:-}" ]; then
  printf "REQUIREMENTS_PIN=%s\n" "${REQUIREMENTS_PIN}"
  # If REQUIREMENTS_PIN looks like a pinned version for streamlit (e.g. streamlit==1.25.0), warn if mismatch
  case "${REQUIREMENTS_PIN}" in
    *streamlit==*)
      PIN_VER=${REQUIREMENTS_PIN#*streamlit==}
      if [ "$PIN_VER" != "$INSTALLED_STREAMLIT" ]; then
        echo "warning: installed streamlit ($INSTALLED_STREAMLIT) does not match REQUIREMENTS_PIN ($PIN_VER)" >&2
      fi
      ;;
  esac
fi
