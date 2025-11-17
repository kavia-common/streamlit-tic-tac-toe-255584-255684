# Tests for Streamlit Tic Tac Toe

This folder contains tests powered by pytest.

- Unit tests: `test_game_logic_unit.py`
- Integration-like tests: `test_app_session_integration.py` (uses a minimal stub for `streamlit` to validate session state logic deterministically)
- Lightweight performance checks are embedded within the test files to ensure functions remain efficient.

How to run:
1. Install runtime + dev requirements (pytest lives in requirements-dev.txt):
   pip install -r requirements.txt -r requirements-dev.txt

2. From the container root directory:
   pytest -q

Notes:
- We intentionally avoid spinning up the Streamlit server in tests. Instead, we stub the `streamlit` module used by `app.py` to validate session logic and ensure fast, deterministic tests.
- If CI requires it, consider adding `pytest` to a dev requirements file (e.g., `requirements-dev.txt`) rather than the runtime `requirements.txt` used for deployment.
