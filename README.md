# streamlit-tic-tac-toe-255584-255684

This workspace hosts a Streamlit-based Tic Tac Toe app.

Run locally:
```bash
cd tic_tac_toe_native_app
pip install -r requirements.txt
bash start.sh
```

Notes:
- The container uses Python/Streamlit; any previous CMake/Qt build flow has been removed.
- Preview systems should execute: `streamlit run app.py --server.port=${PORT:-8501} --server.address=0.0.0.0` in `tic_tac_toe_native_app/`.
- A root `Procfile` is provided to help platforms that auto-detect process types.