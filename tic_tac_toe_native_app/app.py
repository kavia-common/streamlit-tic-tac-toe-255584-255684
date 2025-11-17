import streamlit as st
from typing import List, Optional, Tuple
from game_logic import (
    new_board,
    is_valid_move,
    make_move,
    check_winner,
    is_draw,
    switch_player,
    compute_ai_move,
)

# PUBLIC_INTERFACE
def init_session_state() -> None:
    """Initialize Streamlit session state for the Tic Tac Toe app."""
    defaults = {
        "board": new_board(),
        "current_player": "X",
        "winner": None,
        "moves": 0,
        "mode": "Player vs Computer",
        "difficulty": "medium",
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v


def _reset_game() -> None:
    """Reset the board and related session state values."""
    st.session_state.board = new_board()
    st.session_state.current_player = "X"
    st.session_state.winner = None
    st.session_state.moves = 0


def _apply_base_style() -> None:
    """Inject minimal CSS to apply Ocean Professional theme accents and rounded corners."""
    st.markdown(
        """
        <style>
        :root {
            --primary: #2563EB; /* Blue-600 */
            --secondary: #F59E0B; /* Amber-500 */
            --success: #F59E0B;
            --error: #EF4444; /* Red-500 */
            --text: #111827; /* Gray-900 */
            --background: #f9fafb; /* Gray-50 */
            --surface: #ffffff; /* White */
            --radius: 10px;
        }
        .main, .stApp {
            background: var(--background);
            color: var(--text);
        }
        .o-card {
            background: var(--surface);
            border-radius: var(--radius);
            box-shadow: 0 2px 8px rgba(0,0,0,0.06);
            padding: 1rem 1.25rem;
            border: 1px solid rgba(0,0,0,0.06);
        }
        .o-header {
            display: flex; align-items: center; gap: 10px;
        }
        .o-pill {
            display: inline-flex; align-items: center; gap: 6px;
            background: linear-gradient(135deg, rgba(37,99,235,0.08), rgba(249,250,251,0.9));
            color: var(--primary);
            border: 1px solid rgba(37,99,235,0.25);
            border-radius: 999px;
            padding: 4px 10px;
            font-size: 0.8rem;
            font-weight: 600;
        }
        .o-status {
            font-weight: 600;
            padding: 6px 10px;
            border-radius: 8px;
            border: 1px solid rgba(0,0,0,0.06);
            background: #fff;
        }
        .o-status.win { color: var(--success); border-color: rgba(245,158,11,0.35); background: rgba(245,158,11,0.08); }
        .o-status.draw { color: #6b7280; background: rgba(17,24,39,0.04); }
        .o-status.play { color: var(--primary); border-color: rgba(37,99,235,0.35); background: rgba(37,99,235,0.06); }

        button[kind="secondary"] {
            border-radius: var(--radius) !important;
        }
        .o-help {
            font-size: 0.9rem; color: #374151;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def _header() -> None:
    """Render app header."""
    st.markdown(
        """
        <div class="o-card o-header">
            <span class="o-pill">Tic Tac Toe</span>
            <div style="font-weight:800; font-size:1.25rem;">Ocean Professional</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _sidebar() -> None:
    """Render sidebar controls."""
    with st.sidebar:
        st.markdown("### Settings")
        st.session_state.mode = st.radio(
            "Mode",
            options=["Player vs Player", "Player vs Computer"],
            index=1 if st.session_state.mode == "Player vs Computer" else 0,
        )
        if st.session_state.mode == "Player vs Computer":
            st.session_state.difficulty = st.select_slider(
                "Computer Difficulty",
                options=["easy", "medium"],
                value=st.session_state.difficulty,
                help="Easy: random moves. Medium: rule-based strategy.",
            )

        st.divider()
        col1, col2 = st.columns(2)
        with col1:
            if st.button("New Game", use_container_width=True):
                _reset_game()
        with col2:
            if st.button("Reset Board", use_container_width=True):
                _reset_game()

        st.caption("No environment variables are required.")


def _status_bar() -> None:
    """Render status line about current game state."""
    winner: Optional[str] = st.session_state.winner
    board: List[str] = st.session_state.board

    status = ""
    css_class = "play"
    if winner:
        status = f"Winner: {winner} 🎉"
        css_class = "win"
    elif is_draw(board):
        status = "It's a draw 🤝"
        css_class = "draw"
    else:
        status = f"Current player: {st.session_state.current_player}"

    st.markdown(
        f"""
        <div class="o-card o-status {css_class}">
            {status}
        </div>
        """,
        unsafe_allow_html=True,
    )


def _handle_player_click(idx: int) -> None:
    """Handle a click on the board cell for human player."""
    if st.session_state.winner or is_draw(st.session_state.board):
        return

    if is_valid_move(st.session_state.board, idx):
        st.session_state.board = make_move(
            st.session_state.board, idx, st.session_state.current_player
        )
        st.session_state.moves += 1

        winner = check_winner(st.session_state.board)
        if winner:
            st.session_state.winner = winner
            return

        if is_draw(st.session_state.board):
            return

        st.session_state.current_player = switch_player(st.session_state.current_player)


def _maybe_ai_move() -> None:
    """If in PvC mode and it's the computer's turn, compute and apply the AI move."""
    if st.session_state.mode != "Player vs Computer":
        return
    if st.session_state.winner or is_draw(st.session_state.board):
        return

    # Assume 'O' is the computer if X always starts
    if st.session_state.current_player == "O":
        move = compute_ai_move(
            st.session_state.board, player="O", difficulty=st.session_state.difficulty
        )
        if move is not None and is_valid_move(st.session_state.board, move):
            st.session_state.board = make_move(st.session_state.board, move, "O")
            st.session_state.moves += 1

            winner = check_winner(st.session_state.board)
            if winner:
                st.session_state.winner = winner
                return

            if not is_draw(st.session_state.board):
                st.session_state.current_player = switch_player(
                    st.session_state.current_player
                )


def _board_ui() -> None:
    """Render the 3x3 grid with buttons."""
    board = st.session_state.board

    def cell_label(val: str) -> str:
        return val if val != "" else " "

    for row in range(3):
        c1, c2, c3 = st.columns(3, gap="small")
        for col, col_container in enumerate([c1, c2, c3]):
            idx = row * 3 + col
            with col_container:
                btn_label = cell_label(board[idx])

                # Color the button subtly based on value
                if board[idx] == "X":
                    help_txt = "X played here"
                elif board[idx] == "O":
                    help_txt = "O played here"
                else:
                    help_txt = "Click to play"

                clicked = st.button(
                    btn_label,
                    key=f"cell_{idx}",
                    help=help_txt,
                    use_container_width=True,
                )
                if clicked and not st.session_state.winner and not is_draw(board):
                    # If PvC and current player is computer, ignore clicks
                    if st.session_state.mode == "Player vs Computer" and st.session_state.current_player == "O":
                        st.stop()
                    _handle_player_click(idx)
                    # Trigger AI move if needed after player's action
                    _maybe_ai_move()


def main() -> None:
    """Streamlit entrypoint for the Tic Tac Toe application."""
    st.set_page_config(
        page_title="Tic Tac Toe - Ocean Professional",
        page_icon="🎯",
        layout="centered",
        initial_sidebar_state="expanded",
    )
    _apply_base_style()
    init_session_state()
    _header()
    _sidebar()
    _status_bar()
    _board_ui()

    # Provide a brief help section
    with st.expander("How to play"):
        st.markdown(
            """
            <div class="o-help">
            - Players take turns placing X and O on the 3×3 grid.<br/>
            - First to align three marks horizontally, vertically, or diagonally wins.<br/>
            - In Player vs Computer mode, X starts as human and O is the computer.<br/>
            - Difficulty:
              <ul>
                <li><b>Easy</b>: random valid moves.</li>
                <li><b>Medium</b>: rule-based strategy (win > block > center > corner > side).</li>
              </ul>
            </div>
            """,
            unsafe_allow_html=True,
        )


if __name__ == "__main__":
    main()
