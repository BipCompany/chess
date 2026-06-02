"""Tests for new chess pieces and game mechanics."""

import sys
sys.path.insert(0, '/Users/lebronjames/Documents/lyceum/chess')

from modules.field import Field
from modules.rook import Rook
from modules.bishop import Bishop
from modules.queen import Queen
from modules.king import King
from modules.pawn import Pawn
from modules.constants import WHITE, BLACK


def test_start_position():
    f = Field()
    b = f.get_board()
    # Back rank piece types
    assert isinstance(b[0][0], Rook) and b[0][0].get_color() == BLACK
    assert isinstance(b[0][2], Bishop) and b[0][2].get_color() == BLACK
    assert isinstance(b[0][3], Queen) and b[0][3].get_color() == BLACK
    assert isinstance(b[0][4], King) and b[0][4].get_color() == BLACK
    assert isinstance(b[0][5], Bishop) and b[0][5].get_color() == BLACK
    assert isinstance(b[7][2], Bishop) and b[7][2].get_color() == WHITE
    assert isinstance(b[7][3], Queen) and b[7][3].get_color() == WHITE
    assert isinstance(b[7][4], King) and b[7][4].get_color() == WHITE
    print("test_start_position OK")


def test_bishop_movement():
    f = Field(setup=False)
    f.turn = WHITE
    # Place bishop in center
    bishop = Bishop(f, WHITE)
    bishop.place(4, 4)
    # Diagonal moves
    assert bishop.can_move(6, 6)[0], "Bishop should move SE"
    assert bishop.can_move(2, 2)[0], "Bishop should move NW"
    assert bishop.can_move(6, 2)[0], "Bishop should move SW"
    assert bishop.can_move(2, 6)[0], "Bishop should move NE"
    # Non-diagonal moves
    assert not bishop.can_move(4, 6)[0], "Bishop shouldn't move horizontally"
    assert not bishop.can_move(6, 4)[0], "Bishop shouldn't move vertically"
    # Blocked
    f.board[5][5] = Pawn(f, WHITE)
    assert not bishop.can_move(6, 6)[0], "Bishop shouldn't jump over pieces"
    print("test_bishop_movement OK")


def test_queen_movement():
    f = Field(setup=False)
    f.turn = WHITE
    queen = Queen(f, WHITE)
    queen.place(4, 4)
    # Horizontal
    assert queen.can_move(4, 7)[0], "Queen should move horizontally"
    # Vertical
    assert queen.can_move(0, 4)[0], "Queen should move vertically"
    # Diagonal
    assert queen.can_move(6, 6)[0], "Queen should move diagonally"
    # Blocked
    p = Pawn(f, WHITE)
    p.place(4, 6)
    assert not queen.can_move(4, 7)[0], "Queen shouldn't jump over pieces"
    print("test_queen_movement OK")


def test_king_movement():
    f = Field(setup=False)
    f.turn = WHITE
    king = King(f, WHITE)
    king.place(4, 4)
    # One step any direction
    assert king.can_move(4, 5)[0], "King should move one step right"
    assert king.can_move(5, 5)[0], "King should move one step diagonal"
    assert king.can_move(4, 3)[0], "King should move one step left"
    # Not two steps
    assert not king.can_move(4, 6)[0], "King shouldn't move two steps"
    # Can't move into check — rook at (3,5) attacks (4,5)
    r = Rook(f, BLACK)
    r.place(3, 5)
    assert not king.can_move(4, 5)[0], "King shouldn't move into attacked square"
    print("test_king_movement OK")


def test_king_safety():
    """Moving a piece that leaves own king in check should be rejected."""
    f = Field(setup=False)
    f.turn = WHITE
    king = King(f, WHITE)
    king.place(0, 4)
    # Pawn blocking a bishop attack on the king
    pawn = Pawn(f, WHITE)
    pawn.place(1, 3)
    pawn.first_move = False
    bishop = Bishop(f, BLACK)
    bishop.place(3, 1)  # Attacks (0,4) via diagonal, but pawn at (1,3) blocks

    # Move pawn out of the way — should be rejected
    result = f.move_piece(0, 1, 3, 2, 3)
    assert result == "Can't leave king in check", f"Expected king safety error, got: {result}"
    print("test_king_safety OK")


def test_check_detection():
    """Simple check scenario."""
    f = Field(setup=False)
    f.turn = WHITE
    king = King(f, WHITE)
    king.place(0, 4)
    rook = Rook(f, BLACK)
    rook.place(0, 0)

    assert f.is_king_in_check(WHITE), "King should be in check from rook"
    print("test_check_detection OK")


def test_checkmate():
    """Back-rank checkmate."""
    f = Field(setup=False)
    f.turn = WHITE
    king = King(f, WHITE)
    king.place(0, 4)
    rook1 = Rook(f, BLACK)
    rook1.place(1, 4)  # Checks along col 4
    rook2 = Rook(f, BLACK)
    rook2.place(1, 5)  # Covers escape square (0,5)
    rook3 = Rook(f, BLACK)
    rook3.place(1, 3)  # Covers escape square (0,3)

    assert f.is_king_in_check(WHITE), "White should be in check"
    assert not f._has_legal_moves(WHITE), "White should have no legal moves"
    print("test_checkmate OK")


def test_promotion():
    """Pawn reaching rank 0 promotes to queen."""
    f = Field(setup=False)
    f.turn = WHITE
    pawn = Pawn(f, WHITE)
    pawn.place(1, 0)
    pawn.first_move = False

    result = f.move_piece(0, 1, 0, 0, 0)
    promoted = f.board[0][0]
    assert isinstance(promoted, Queen), f"Pawn should promote to Queen, got {type(promoted).__name__}"
    assert promoted.get_color() == WHITE, "Promoted queen should be white"
    print("test_promotion OK")


def test_black_promotion():
    """Black pawn reaching rank 7 promotes to queen."""
    f = Field(setup=False)
    f.turn = BLACK
    pawn = Pawn(f, BLACK)
    pawn.place(6, 0)
    pawn.first_move = False

    result = f.move_piece(1, 6, 0, 7, 0)
    promoted = f.board[7][0]
    assert isinstance(promoted, Queen), "Black pawn should promote to Queen"
    assert promoted.get_color() == BLACK
    print("test_black_promotion OK")


if __name__ == "__main__":
    test_start_position()
    test_bishop_movement()
    test_queen_movement()
    test_king_movement()
    test_king_safety()
    test_check_detection()
    test_checkmate()
    test_promotion()
    test_black_promotion()
    print("\nAll tests passed!")
