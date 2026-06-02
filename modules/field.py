from __future__ import annotations

from modules.constants import BLACK, WHITE
from modules.piece import Piece
from modules.pawn import Pawn
from modules.knight import Knight
from modules.rook import Rook
from modules.bishop import Bishop
from modules.queen import Queen
from modules.king import King


class Field:
    def __init__(self, setup: bool = True) -> None:
        self.board: list[list[None | Piece]] = [[None] * 8 for _ in range(8)]
        self.captured_white = []
        self.captured_black = []
        self.turn = WHITE
        self.en_passant_target = None
        self._checking_attack = False
        if setup:
            self.setup()

    def get_board(self) -> list[list[None | Piece]]:
        return self.board

    def change_turn(self) -> None:
        self.turn = self.turn ^ 1

    def setup(self) -> None:
        self.turn = WHITE
        
        # pawns
        for i in range(8):
            self.place_piece(Pawn(self, WHITE), 6, i)
            self.place_piece(Pawn(self, BLACK), 1, i)

        # rooks
        self.place_piece(Rook(self, BLACK), 0, 0)
        self.place_piece(Rook(self, BLACK), 0, 7)
        self.place_piece(Rook(self, WHITE), 7, 0)
        self.place_piece(Rook(self, WHITE), 7, 7)

        # knights
        self.place_piece(Knight(self, BLACK), 0, 1)
        self.place_piece(Knight(self, BLACK), 0, 6)
        self.place_piece(Knight(self, WHITE), 7, 1)
        self.place_piece(Knight(self, WHITE), 7, 6)

        # bishops
        self.place_piece(Bishop(self, BLACK), 0, 2)
        self.place_piece(Bishop(self, BLACK), 0, 5)
        self.place_piece(Bishop(self, WHITE), 7, 2)
        self.place_piece(Bishop(self, WHITE), 7, 5)

        # queens
        self.place_piece(Queen(self, BLACK), 0, 3)
        self.place_piece(Queen(self, WHITE), 7, 3)

        # kings
        self.place_piece(King(self, BLACK), 0, 4)
        self.place_piece(King(self, WHITE), 7, 4)

    def place_piece(self, piece, row, col) -> bool:
        if piece.place(row, col):
            return True
        return False

    def move_piece(self, player_id, row1, col1, row2, col2) -> str:
        if player_id != self.turn:
          return ""
        piece = self.board[row1][col1]
        if not piece:
            return "No piece in cell"
        if piece.get_color() != self.turn:
            turn_word = "white's" if self.turn == WHITE else "black's"
            return "It's " + turn_word + " turn"

        moved, message = piece.can_move(row2, col2)
        if not moved:
            return message

        # --- Save state for possible undo (king safety check) ---
        captured = self.board[row2][col2]
        old_en_passant = self.en_passant_target
        old_first_move = None
        en_passant_captured = None
        if isinstance(piece, Pawn):
            old_first_move = piece.first_move
            if self.en_passant_target is not None and (row2, col2) == self.en_passant_target:
                en_passant_captured = self.board[row1][col2]

        # --- Execute the move on the board ---
        self.board[row1][col1] = None

        # En passant capture
        if en_passant_captured:
            self.board[row1][col2] = None
            if en_passant_captured.get_color() == WHITE:
                self.captured_white.append(en_passant_captured)
            else:
                self.captured_black.append(en_passant_captured)

        # Regular capture
        if captured and not en_passant_captured:
            if captured.get_color() == WHITE:
                self.captured_white.append(captured)
            else:
                self.captured_black.append(captured)

        # Move the piece
        piece.row = row2
        piece.col = col2
        self.board[row2][col2] = piece

        # --- Check if own king is in check after the move ---
        if self.is_king_in_check(self.turn):
            # Undo the move
            self.board[row2][col2] = captured
            piece.row = row1
            piece.col = col1
            self.board[row1][col1] = piece

            if en_passant_captured:
                self.board[row1][col2] = en_passant_captured
                if en_passant_captured.get_color() == WHITE:
                    self.captured_white.pop()
                else:
                    self.captured_black.pop()

            if captured and not en_passant_captured:
                if captured.get_color() == WHITE:
                    self.captured_white.pop()
                else:
                    self.captured_black.pop()

            if isinstance(piece, Pawn):
                piece.first_move = old_first_move

            self.en_passant_target = old_en_passant
            return "Can't leave king in check"

        # --- Pawn promotion ---
        if isinstance(piece, Pawn) and (row2 == 0 or row2 == 7):
            self.board[row2][col2] = None
            queen = Queen(self, piece.get_color())
            queen.row = row2
            queen.col = col2
            self.board[row2][col2] = queen

        # --- Manage en passant target ---
        if isinstance(piece, Pawn) and old_first_move and abs(row2 - row1) == 2:
            self.en_passant_target = ((row1 + row2) // 2, col2)
        else:
            self.en_passant_target = None

        # --- Mark pawn first_move as false ---
        if isinstance(piece, Pawn):
            piece.first_move = False

        self.change_turn()

        # --- Check for check / checkmate ---
        result = self.check_for_win()
        return result

    def capture_piece(self, row, col) -> None:
        piece = self.board[row][col]
        if piece:
            if piece.get_color() == WHITE:
                self.captured_white.append(piece)
            else:
                self.captured_black.append(piece)
            self.board[row][col] = None

    def is_under_attack(self, row, col, by_color) -> bool:
        """Check if square (row, col) is attacked by any piece of by_color."""
        if self._checking_attack:
            return False
        self._checking_attack = True
        original_turn = self.turn
        self.turn = by_color
        attacked = False
        try:
            for r in range(8):
                for c in range(8):
                    piece = self.board[r][c]
                    if piece and piece.get_color() == by_color:
                        can, _ = piece.can_move(row, col)
                        if can:
                            attacked = True
                            break
                if attacked:
                    break
        finally:
            self.turn = original_turn
            self._checking_attack = False
        return attacked

    def _find_king(self, color) -> tuple[int, int] | None:
        """Return (row, col) of the king of the given color, or None."""
        for r in range(8):
            for c in range(8):
                piece = self.board[r][c]
                if piece and isinstance(piece, King) and piece.get_color() == color:
                    return (r, c)
        return None

    def is_king_in_check(self, color) -> bool:
        """Check if the king of `color` is in check."""
        king_pos = self._find_king(color)
        if king_pos is None:
            return False
        return self.is_under_attack(king_pos[0], king_pos[1], color ^ 1)

    def _has_legal_moves(self, color) -> bool:
        """Check if the given color has any legal move (doesn't leave own king in check)."""
        for r1 in range(8):
            for c1 in range(8):
                piece = self.board[r1][c1]
                if piece and piece.get_color() == color:
                    for r2 in range(8):
                        for c2 in range(8):
                            if r1 == r2 and c1 == c2:
                                continue
                            can, _ = piece.can_move(r2, c2)
                            if can:
                                # Simulate the move to check king safety
                                if self._would_move_be_legal(r1, c1, r2, c2, color):
                                    return True
        return False

    def _would_move_be_legal(self, r1, c1, r2, c2, color) -> bool:
        """Check if moving piece at (r1,c1) to (r2,c2) leaves the moving player's king safe."""
        piece = self.board[r1][c1]
        captured = self.board[r2][c2]
        en_passant_captured = None
        old_first_move = None

        if isinstance(piece, Pawn):
            old_first_move = piece.first_move
            if self.en_passant_target is not None and (r2, c2) == self.en_passant_target:
                en_passant_captured = self.board[r1][c2]

        # Execute move
        self.board[r1][c1] = None
        if en_passant_captured:
            self.board[r1][c2] = None
        piece.row = r2
        piece.col = c2
        self.board[r2][c2] = piece

        # Check king safety
        legal = not self.is_king_in_check(color)

        # Undo
        self.board[r2][c2] = captured
        piece.row = r1
        piece.col = c1
        self.board[r1][c1] = piece
        if en_passant_captured:
            self.board[r1][c2] = en_passant_captured
        if isinstance(piece, Pawn):
            piece.first_move = old_first_move

        return legal

    def check_for_win(self) -> str:
        """Check for check, checkmate, or stalemate. Returns a message or empty string."""
        opponent = self.turn  # Turn has already been changed

        if not self._has_legal_moves(opponent):
            if self.is_king_in_check(opponent):
                winner = "White" if self.turn == BLACK else "Black"
                return "Checkmate! " + winner + " wins!"
            else:
                return "Stalemate!"

        if self.is_king_in_check(opponent):
            return "Check!"

        return ""


if __name__ == "__main__":
    f = Field()
    f.draw_board()
