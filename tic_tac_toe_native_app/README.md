# Streamlit Tic Tac Toe (Ocean Professional)

A simple Tic Tac Toe game implemented using [Streamlit]. Includes:
- 3×3 grid UI
- Player vs Player and Player vs Computer (easy/medium) modes
- Ocean Professional theme with minimal CSS
- No external services or environment variables required

## Quick Start

1) Install dependencies:
```bash
pip install -r requirements.txt
```

2) Run the app:
```bash
bash start.sh
# or
streamlit run app.py --server.port=${PORT:-8501} --server.address=0.0.0.0
```

This will start a local development server and open the app in your browser.

## Container/Preview Notes

- This project is pure Python/Streamlit. There is no CMake/Qt build. Do not call `cmake` or `make` for Qt.
- The provided `start.sh` installs dependencies and launches Streamlit.
- A `Procfile` is included so platforms that support it can start the app with: `web: bash start.sh`.
- A `Makefile` is provided with `make start`/`make run` targets for convenience.

## Files

- `app.py` — Streamlit UI and session state
- `game_logic.py` — Pure game logic functions
- `requirements.txt` — Python dependencies (Streamlit)
- `start.sh` — Startup script that installs deps and runs Streamlit
- `Procfile` — Process type for platforms that auto-detect
- `.streamlit/config.toml` — Optional theme customization (colors)

## Notes

- No environment variables are required. If a platform provides `PORT`, it will be respected; otherwise defaults to `8501`.
- Use the sidebar to switch modes and difficulty; use "New Game" to reset.

Enjoy!
