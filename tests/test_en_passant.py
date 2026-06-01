"""Test en passant and rook line-of-sight (ported from original test_verify.py)."""
import sys
sys.path.insert(0, '/Users/lebronjames/Documents/lyceum/chess')
from modules.field import Field
from modules.rook import Rook
from modules.pawn import Pawn
from modules.constants import WHITE, BLACK

# --- Rook line-of-sight ---
f0 = Field()
r = Rook(f0, WHITE)
r.place(7, 0)
f0.turn = WHITE
moved, msg = r.can_move(7, 2)
assert moved, f"Rook (7,0)->(7,2) should be clear: {msg}"
moved, msg = r.can_move(4, 0)
assert moved, f"Rook (7,0)->(4,0) should be clear: {msg}"
# Block
blocker = Pawn(f0, WHITE)
blocker.place(5, 0)
moved, msg = r.can_move(2, 0)
assert not moved, "Rook should be blocked"
print("Rook line-of-sight OK")

# --- En passant ---
f = Field()
f.turn = BLACK
f.board[1][0] = None
f.board[1][1] = None
wp = Pawn(f, WHITE)
wp.place(3, 0)
wp.first_move = False
bp = Pawn(f, BLACK)
bp.place(1, 1)
bp.move(3, 1)
assert f.en_passant_target == (2, 1), f"Expected (2,1) got {f.en_passant_target}"
f.change_turn()
moved, msg = wp.can_move(2, 1)
assert moved, f"En passant should be valid: {msg}"
wp.move(2, 1)
assert f.board[3][1] is None, "Black pawn should be captured"
assert wp.row == 2 and wp.col == 1
print("En passant capture OK")

print("All en passant tests OK")
