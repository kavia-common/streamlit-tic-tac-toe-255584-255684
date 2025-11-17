# Streamlit Tic Tac Toe (Ocean Professional)

A simple Tic Tac Toe game implemented using Streamlit. Includes:
- 3×3 grid UI
- Player vs Player and Player vs Computer (easy/medium) modes
- Ocean Professional theme with minimal CSS
- No external services or environment variables required

## Quick Start

1) Install dependencies:
```bash
pip install -r requirements.txt
# For running tests, also install dev requirements:
pip install -r requirements-dev.txt
```

2) Run the app:
```bash
bash start.sh
# or
python -m streamlit run app.py --server.port="${PORT:-8501}" --server.address 0.0.0.0
```

This will start a local development server and open the app in your browser.

## Container/Preview Notes

- This project is pure Python/Streamlit. There is no CMake/Qt build. Do not call `cmake` or `make`.
- Startup is Streamlit-only. The platform should invoke one of:
  - `bash start.sh`
  - `web: python -m streamlit run app.py --server.port $PORT --server.address 0.0.0.0` (Procfile)
- A `Procfile` is included so platforms that support it can start the app with the correct web command.
- A minimal `runtime.txt` is provided to hint the Python version on supported platforms.

## Files

- `app.py` — Streamlit UI and session state
- `game_logic.py` — Pure game logic functions
- `requirements.txt` — Python dependencies (Streamlit)
- `start.sh` — Startup script that launches Streamlit
- `Procfile` — Process type definition for platforms that auto-detect
- `runtime.txt` — Optional Python runtime hint

## Notes

- No environment variables are required. If a platform provides `PORT`, it will be respected; otherwise defaults to `8501`.
- Use the sidebar to switch modes and difficulty; use "New Game" to reset.

Enjoy!

## Testing

This project includes a pytest-based test suite with unit, integration-like, and lightweight performance tests.

- Install runtime + dev dependencies (pytest is kept in a separate dev file to keep runtime light):
  pip install -r requirements.txt -r requirements-dev.txt

- Run tests from the container root:
  pytest -q

Test layout:
- tests/test_game_logic_unit.py — unit tests for pure game logic functions
- tests/test_app_session_integration.py — integration-style tests that simulate session state transitions without launching Streamlit
