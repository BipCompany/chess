"""Quick smoke test — game starts and responds to input."""
import sys
sys.path.insert(0, '/Users/lebronjames/Documents/lyceum/chess')
from modules.field import Field
f = Field()
f.start_position()
# White pawn e2->e4
r = f.move_piece(0, 6, 4, 4, 4)
assert r == "" or r == "Check!", f"e2e4 failed: {r}"
# Black pawn e7->e5
r = f.move_piece(1, 1, 4, 3, 4)
assert r == "" or r == "Check!", f"e7e5 failed: {r}"
# White bishop f1->b5 (Italian)
r = f.move_piece(0, 7, 5, 4, 2)
assert r == "" or r == "Check!", f"Bf1b5 failed: {r}"
# White king safety — moving knight that blocks bishop? no, bishop already moved
# Just verify we can query the board
b = f.get_board()
assert b[4][4] is not None  # white pawn at e4
assert b[3][4] is not None  # black pawn at e5
print("Smoke test OK")
