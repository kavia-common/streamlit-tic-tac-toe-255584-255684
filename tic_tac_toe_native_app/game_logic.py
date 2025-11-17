from typing import List, Optional
import random

# PUBLIC_INTERFACE
def new_board() -> List[str]:
    """Create a new empty Tic Tac Toe board (3x3) represented as a list of 9 strings."""
    return [""] * 9


# PUBLIC_INTERFACE
def is_valid_move(board: List[str], idx: int) -> bool:
    """Check if a move at given index is valid (index in range and cell empty)."""
    return 0 <= idx < 9 and board[idx] == ""


# PUBLIC_INTERFACE
def make_move(board: List[str], idx: int, player: str) -> List[str]:
    """Return a new board with the player's move applied at the given index."""
    if not is_valid_move(board, idx):
        return board[:]
    nb = board[:]
    nb[idx] = player
    return nb


# PUBLIC_INTERFACE
def check_winner(board: List[str]) -> Optional[str]:
    """Return 'X' or 'O' if a winner exists on the board, otherwise None."""
    wins = [
        (0, 1, 2),
        (3, 4, 5),
        (6, 7, 8),  # rows
        (0, 3, 6),
        (1, 4, 7),
        (2, 5, 8),  # cols
        (0, 4, 8),
        (2, 4, 6),  # diagonals
    ]
    for a, b, c in wins:
        if board[a] and board[a] == board[b] == board[c]:
            return board[a]
    return None


# PUBLIC_INTERFACE
def is_draw(board: List[str]) -> bool:
    """Return True if board is full and no winner."""
    return all(cell != "" for cell in board) and check_winner(board) is None


# PUBLIC_INTERFACE
def switch_player(player: str) -> str:
    """Switch the current player from 'X' to 'O' or 'O' to 'X'."""
    return "O" if player == "X" else "X"


def _winning_move(board: List[str], player: str) -> Optional[int]:
    """Find a winning move for player if available."""
    for idx in range(9):
        if is_valid_move(board, idx):
            trial = make_move(board, idx, player)
            if check_winner(trial) == player:
                return idx
    return None


def _blocking_move(board: List[str], player: str) -> Optional[int]:
    """Find a blocking move to prevent opponent from winning."""
    opponent = switch_player(player)
    for idx in range(9):
        if is_valid_move(board, idx):
            trial = make_move(board, idx, opponent)
            if check_winner(trial) == opponent:
                return idx
    return None


def _preferred_positions(board: List[str], positions: List[int]) -> Optional[int]:
    """Return first available position from preferred positions list."""
    for p in positions:
        if is_valid_move(board, p):
            return p
    return None


# PUBLIC_INTERFACE
def compute_ai_move(board: List[str], player: str, difficulty: str = "medium") -> Optional[int]:
    """Compute AI move for the given player.

    Strategy:
    - easy: choose any random valid move.
    - medium: rule-based:
        1) win if possible
        2) block opponent win
        3) take center
        4) take any corner
        5) take any side
    Returns index of chosen move, or None if no valid moves remain.
    """
    empty_indices = [i for i, v in enumerate(board) if v == ""]
    if not empty_indices:
        return None

    if difficulty == "easy":
        return random.choice(empty_indices)

    # Medium difficulty: rule-based heuristic
    winner_idx = _winning_move(board, player)
    if winner_idx is not None:
        return winner_idx

    block_idx = _blocking_move(board, player)
    if block_idx is not None:
        return block_idx

    # Center
    if is_valid_move(board, 4):
        return 4

    # Corners then sides
    corners = [0, 2, 6, 8]
    sides = [1, 3, 5, 7]
    corner_idx = _preferred_positions(board, corners)
    if corner_idx is not None:
        return corner_idx

    side_idx = _preferred_positions(board, sides)
    if side_idx is not None:
        return side_idx

    # Fallback to first available
    return empty_indices[0]
