from types import SimpleNamespace
from typing import List, Optional

import os
import pytest

# We will import app and monkeypatch minimal parts of streamlit session_state interface
import app as app_module


class DummySessionState(dict):
    """Minimal dict-like session state used to simulate st.session_state."""

    def __getattr__(self, item):
        try:
            return self[item]
        except KeyError as exc:
            raise AttributeError(item) from exc

    def __setattr__(self, key, value):
        self[key] = value


class DummyST:
    """A very small stub for streamlit used to satisfy functions under test that access session_state."""

    def __init__(self):
        self.session_state = DummySessionState()

    # The following are st functions referenced by code paths we exercise.
    # We provide no-op or simple behaviors for tests that focus on session logic.
    def markdown(self, *_args, **_kwargs):
        return None

    def sidebar(self):
        # Not used in our tests; context manager in real app
        return None

    def button(self, *args, **kwargs):
        # We won't click UI in these integration session tests.
        return False

    def columns(self, *args, **kwargs):
        # Not used by these tests, but keep signature if needed
        return [SimpleNamespace()] * 3

    def set_page_config(self, *args, **kwargs):
        return None

    def radio(self, *args, **kwargs):
        return "Player vs Computer"

    def select_slider(self, *args, **kwargs):
        return "medium"

    def divider(self):
        return None

    def caption(self, *_args, **_kwargs):
        return None

    def expander(self, *_args, **_kwargs):
        class _CM:
            def __enter__(self_inner):
                return None

            def __exit__(self_inner, exc_type, exc, tb):
                return False

        return _CM()

    def stop(self):
        # In real st.stop raises an exception to halt execution.
        raise RuntimeError("st.stop called")


@pytest.fixture
def stub_streamlit(monkeypatch):
    """
    Monkeypatch the streamlit module used by app_module with a minimal stub
    to allow exercising session-state logic deterministically.
    """
    dummy_st = DummyST()
    monkeypatch.setattr(app_module, "st", dummy_st, raising=True)
    return dummy_st


class TestInitSessionState:
    def test_init_session_state_sets_defaults(self, stub_streamlit):
        # Arrange
        # Ensure session state is empty
        stub_streamlit.session_state.clear()

        # Act
        app_module.init_session_state()

        # Assert
        ss = stub_streamlit.session_state
        assert ss["current_player"] == "X"
        assert ss["winner"] is None
        assert ss["moves"] == 0
        assert ss["mode"] in ("Player vs Player", "Player vs Computer")
        assert ss["difficulty"] in ("easy", "medium")
        assert isinstance(ss["board"], list) and len(ss["board"]) == 9


class TestRuntimePort:
    def test_get_runtime_port_parses_env(self, monkeypatch):
        # Arrange
        monkeypatch.setenv("PORT", "7777")
        # import function from __main__ guard scope is accessible as attribute
        from app import get_runtime_port

        # Act
        port = get_runtime_port()

        # Assert
        assert port == 7777

    def test_get_runtime_port_fallback_on_invalid(self, monkeypatch):
        monkeypatch.setenv("PORT", "not-a-number")
        from app import get_runtime_port

        assert get_runtime_port() == 8501

    def test_get_runtime_port_default(self, monkeypatch):
        monkeypatch.delenv("PORT", raising=False)
        from app import get_runtime_port

        assert get_runtime_port() == 8501


class TestSessionTransitions:
    def test_player_click_updates_board_and_switches_player(self, stub_streamlit):
        # Arrange
        app_module.init_session_state()
        ss = stub_streamlit.session_state
        assert ss.current_player == "X"
        assert ss.board[0] == ""

        # Act: simulate a player click by calling private handler
        app_module._handle_player_click(0)

        # Assert
        assert ss.board[0] == "X"
        assert ss.moves == 1
        # No winner yet, should switch to O
        assert ss.current_player == "O"

    def test_player_click_ignores_when_game_over(self, stub_streamlit):
        # Arrange
        app_module.init_session_state()
        ss = stub_streamlit.session_state
        # Simulate a winning position for X on first row
        ss.board = ["X", "X", "X", "", "", "", "", "", ""]
        ss.winner = "X"

        # Act
        app_module._handle_player_click(4)  # attempt to click after win

        # Assert: no change
        assert ss.board[4] == ""
        assert ss.moves == 0
        assert ss.winner == "X"

    def test_ai_move_trigger_in_pvc_mode(self, stub_streamlit, monkeypatch):
        # Arrange
        app_module.init_session_state()
        ss = stub_streamlit.session_state
        ss.mode = "Player vs Computer"
        ss.current_player = "O"  # it's AI's turn
        # Force a deterministic AI move at index 4
        monkeypatch.setattr(
            app_module, "compute_ai_move", lambda board, player, difficulty: 4
        )

        # Act
        app_module._maybe_ai_move()

        # Assert
        assert ss.board[4] == "O"
        assert ss.moves == 1
        # Should switch back to X if not draw and no winner
        assert ss.current_player == "X"
        assert ss.winner is None

    def test_ai_move_does_not_move_in_pvp_mode(self, stub_streamlit, monkeypatch):
        # Arrange
        app_module.init_session_state()
        ss = stub_streamlit.session_state
        ss.mode = "Player vs Player"
        ss.current_player = "O"
        called = {"moved": False}

        def fake_ai(board, player, difficulty):
            called["moved"] = True
            return 0

        monkeypatch.setattr(app_module, "compute_ai_move", fake_ai)

        # Act
        app_module._maybe_ai_move()

        # Assert
        assert called["moved"] is False
        assert all(cell == "" for cell in ss.board)

    def test_status_bar_draw_and_win_paths_do_not_crash(self, stub_streamlit):
        # These calls rely on st.markdown; our stub is a no-op.
        app_module.init_session_state()
        ss = stub_streamlit.session_state

        # Draw state
        ss.board = ["X", "O", "X", "X", "O", "O", "O", "X", "X"]
        ss.winner = None
        app_module._status_bar()  # should not raise

        # Win state
        ss.board = ["X", "X", "X", "", "", "", "", "", ""]
        ss.winner = "X"
        app_module._status_bar()  # should not raise


class TestLightweightPerformanceFlows:
    def test_sequence_of_player_and_ai_moves_is_fast(self, stub_streamlit, monkeypatch):
        # Arrange
        app_module.init_session_state()
        ss = stub_streamlit.session_state
        ss.mode = "Player vs Computer"
        # A simple deterministic AI that chooses first available
        monkeypatch.setattr(
            app_module,
            "compute_ai_move",
            lambda board, player, difficulty: next(
                (i for i, v in enumerate(board) if v == ""), None
            ),
        )

        # Act
        for _ in range(3):
            # Player X plays first empty
            idx = next(i for i, v in enumerate(ss.board) if v == "")
            app_module._handle_player_click(idx)
            app_module._maybe_ai_move()  # O plays next

        # Assert: At least 6 moves should be recorded quickly
        assert ss.moves >= 6
