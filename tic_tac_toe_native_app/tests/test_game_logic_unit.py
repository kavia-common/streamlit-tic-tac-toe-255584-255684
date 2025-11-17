import builtins
import time
from typing import List, Optional

import pytest

# Import the pure game logic module
import game_logic as gl


class TestNewBoard:
    def test_new_board_is_empty_and_of_length_9(self):
        # Arrange & Act
        board = gl.new_board()

        # Assert
        assert isinstance(board, list)
        assert len(board) == 9
        assert all(cell == "" for cell in board)


class TestIsValidMove:
    def test_is_valid_move_true_on_empty_cell(self):
        board = gl.new_board()
        assert gl.is_valid_move(board, 0) is True

    def test_is_valid_move_false_on_occupied_cell(self):
        board = gl.new_board()
        board[0] = "X"
        assert gl.is_valid_move(board, 0) is False

    def test_is_valid_move_false_on_out_of_range_index(self):
        board = gl.new_board()
        assert gl.is_valid_move(board, -1) is False
        assert gl.is_valid_move(board, 9) is False


class TestMakeMove:
    def test_make_move_applies_when_valid(self):
        board = gl.new_board()
        new_board = gl.make_move(board, 4, "X")
        assert new_board is not board  # returns a new copy
        assert new_board[4] == "X"
        assert board[4] == ""  # original not mutated

    def test_make_move_ignored_when_invalid(self):
        board = gl.new_board()
        board[2] = "O"
        new_board = gl.make_move(board, 2, "X")
        assert new_board is not board
        assert new_board[2] == "O"  # unchanged


class TestCheckWinner:
    @pytest.mark.parametrize(
        "indices,player",
        [
            ((0, 1, 2), "X"),
            ((3, 4, 5), "X"),
            ((6, 7, 8), "O"),
            ((0, 3, 6), "X"),
            ((1, 4, 7), "O"),
            ((2, 5, 8), "X"),
            ((0, 4, 8), "O"),
            ((2, 4, 6), "X"),
        ],
    )
    def test_detects_winner_patterns(self, indices, player):
        board = gl.new_board()
        for i in indices:
            board[i] = player
        assert gl.check_winner(board) == player

    def test_no_winner_returns_none(self):
        board = ["X", "O", "X", "X", "O", "", "", "", ""]
        assert gl.check_winner(board) is None


class TestIsDraw:
    def test_is_draw_true_when_full_and_no_winner(self):
        # Classic draw board
        board = ["X", "O", "X", "X", "O", "O", "O", "X", "X"]
        assert gl.is_draw(board) is True
        assert gl.check_winner(board) is None

    def test_is_draw_false_when_not_full(self):
        board = gl.new_board()
        assert gl.is_draw(board) is False

    def test_is_draw_false_when_winner(self):
        board = ["X", "X", "X", "", "", "", "", "", ""]
        assert gl.is_draw(board) is False


class TestSwitchPlayer:
    def test_switch_player(self):
        assert gl.switch_player("X") == "O"
        assert gl.switch_player("O") == "X"


class TestComputeAIMoveEasy:
    def test_easy_returns_random_valid_index(self):
        board = gl.new_board()
        board[0] = "X"
        move = gl.compute_ai_move(board, player="O", difficulty="easy")
        assert move in [i for i, v in enumerate(board) if v == ""]

    def test_easy_returns_none_when_no_moves(self):
        board = ["X", "O", "X", "X", "O", "O", "O", "X", "X"]
        assert gl.compute_ai_move(board, player="O", difficulty="easy") is None


class TestComputeAIMoveMediumStrategy:
    def test_medium_prefers_winning_move(self):
        # O can win at index 2
        board = ["O", "O", "", "", "", "", "", "", ""]
        move = gl.compute_ai_move(board, player="O", difficulty="medium")
        assert move == 2

    def test_medium_blocks_opponent(self):
        # X threatens to win at index 2; O should block at 2
        board = ["X", "X", "", "", "", "", "", "", ""]
        move = gl.compute_ai_move(board, player="O", difficulty="medium")
        assert move == 2

    def test_medium_takes_center_if_available(self):
        board = ["X", "", "", "", "", "", "", "", ""]
        move = gl.compute_ai_move(board, player="O", difficulty="medium")
        assert move == 4

    def test_medium_takes_corner_when_center_unavailable(self):
        board = gl.new_board()
        board[4] = "X"  # center taken
        move = gl.compute_ai_move(board, player="O", difficulty="medium")
        assert move in [0, 2, 6, 8]

    def test_medium_takes_side_as_last_preference(self):
        # Corners occupied; should pick a side
        board = gl.new_board()
        for c in [0, 2, 6, 8]:
            board[c] = "X"
        # Ensure at least one side is open
        board[1] = ""
        move = gl.compute_ai_move(board, player="O", difficulty="medium")
        assert move in [1, 3, 5, 7]


class TestPerformanceLightweight:
    def test_compute_ai_move_medium_performance_under_threshold(self):
        # This is a lightweight perf sanity check (unit-level), not a full load test.
        board = [""] * 9
        start = time.perf_counter()
        for _ in range(5000):
            _ = gl.compute_ai_move(board, player="O", difficulty="medium")
        duration = time.perf_counter() - start
        # Should be very fast; assert under a reasonable threshold
        assert duration < 0.5  # seconds
