# Streamlit Tic Tac Toe (Ocean Professional)

A simple Tic Tac Toe game implemented using [Streamlit]. Includes:
- 3×3 grid UI
- Player vs Player and Player vs Computer (easy/medium) modes
- Ocean Professional theme with minimal CSS
- No external services or environment variables required

## Quick Start

1) Install dependencies:
```bash
pip install streamlit
```

2) Run the app:
```bash
streamlit run app.py
```

This will start a local development server and open the app in your browser.

## Files

- `app.py` — Streamlit UI and session state
- `game_logic.py` — Pure game logic functions
- `.streamlit/config.toml` — Optional theme customization (colors)

## Notes

- No environment variables are required.
- The platform auto-detects Streamlit as the container entrypoint.
- Use the sidebar to switch modes and difficulty; use "New Game" to reset.

Enjoy!
